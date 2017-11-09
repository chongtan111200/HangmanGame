from flask import Flask, render_template, request, session, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from random import choice
import os, datetime

"""The logic is to randomly choose a word from a txt dictionary file.
Then the game returns the length of the word.Each time the user type 
in a word, the cal_guess returns the a json with index and character
which are correctly guessed. If the palyer loses the game, the game 
returns the answer by visiting the /answer. Even though the player can visit
the answer site directly, he can't go back to type in the answer (each time he
goes back, a new answer is generated). So this prevents the
player from cheating and also let the player know the answer at last."""


# stores the words in a list
words = []
app_root = os.path.dirname(os.path.abspath(__file__))
app_static = os.path.join(app_root, 'static')

with open(os.path.join(app_static, 'words.txt'),'r') as all_words:
    for word in all_words:
        words.append(word.strip())

# constant for lives of the user
LIVES = 10

# a cache to record the status of the game
cache = {}

# set up the app with bootstrap
app = Flask(__name__)
app.config['SECRET_KEY'] = 'You wont know this key is Chong'
app.config['SQLALCHEMY_DATABASE_URI'] =\
     'sqlite:///' + os.path.join(app_root,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

# use 30 minutes of session to record the status of the current game 
@app.before_request
def make_session_longer():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes = 30)

# main route
@app.route('/')
def index():
    return render_template('index.html')

# randomly choose the word and return the length of the answer
@app.route('/game', methods=['POST'])
def game():
    guessed_char =[] 
    missed_char = [] 
    user_info = cache.get(session.get('user'))
    # not cached user
    if len(user_info) == 0: 
        session['the_answer'] = choice(words)
    elif request.form.get('restart') == '1':
        session['the_answer'] = choice(words)
        cache[session.get('user')] = {}
    else:
        guessed_char = user_info['guessed_char']
        missed_char = user_info['missed_char']
    
    user_json = {}
    user_json['len'] = str(len(session.get('the_answer')))
    user_json['guessed_char'] = guessed_char
    user_json['missed_char'] = missed_char
    return jsonify(user_json)

# check what index and character is correctly guessed and return a json file
@app.route('/cal_guess')
def cal_guess():
    guess_char = request.args.get('guess_char')
    json_reply = []
    missed_guess = True
    for i,each_char_in_the_answer in enumerate(session.get('the_answer')):
        if guess_char == each_char_in_the_answer:
            missed_guess = False
            one_hit = {}
            one_hit['index'] = i
            one_hit['ch'] = guess_char
            json_reply.append(one_hit)

    # update cache
    if missed_guess:
        if 'missed_char' not in cache.get(session.get('user')):
            cache.get(session.get('user'))['missed_char'] = [] 
        cache.get(session.get('user'))['missed_char'].append(guess_char)
    else:
        if 'guessed_char' not in cache.get(session.get('user')):
            cache.get(session.get('user'))['guessed_char'] = [] 
        cache.get(session.get('user'))['guessed_char'].append(one_hit)
    return jsonify(json_reply)

#check with db to log in user, return the won and lost or 0 for not a user
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('name')
    userpass = request.form.get('password')
    user = User.query.filter_by(name = username).first()
    # cache the user
    session['user'] = username
    if cache.get(username) is None:
        cache[username] = {}
    if user is not None and user.verify_password(userpass):
        return str(user.won) + ' ' + str(user.lost)
    return '0'

# return 1 if sign up sucessful, 0 otherwise
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('name')
    userpass = request.form.get('password')
    user = User.query.filter_by(name = username).first()
    if user is None:
        add_user = User(name = username, password=userpass,won=0,lost=0)
        db.session.add(add_user)
        return '1'
    return '0'

# deal with end game condition reutrn 1 if won, return the answer if lost
@app.route('/end', methods=['POST'])
def end():
    hits = int(request.form.get('hits'))
    misses =int(request.form.get('misses'))
    username = request.form.get('name')
    user = User.query.filter_by(name = username).first()
    if misses == LIVES:
        user.lost += 1
        return str(session.get('the_answer'))
    elif hits == len(session.get('the_answer')):
        user.won += 1
        return '1'
    else:
        return '0'

# model for the user, includes name, password hash, won game, and lost game
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    won = db.Column(db.Integer)
    lost = db.Column(db.Integer)
    
    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


# starts the app
if __name__ == '__main__':
    app.run(threaded = True)
