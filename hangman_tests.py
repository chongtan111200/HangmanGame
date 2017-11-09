import os, hangman, unittest, tempfile, json

""" For testing the hang man game
Tested the log in, sign up, start game, restart game, and single guess"""

class HangmanTestCase(unittest.TestCase):
    def setUp(self):
        hangman.app.testing = True
        self.app = hangman.app.test_client()

    def tearDown(self):
        return
        
    # test the main page
    def test_main_information(self):
        main = self.app.get('/')
        assert 'Start' in main.data
        assert 'Chong\'s Hangman Game' in main.data
        assert 'sign up' in main.data
        assert 'Player Name:' in main.data
        assert 'Password:' in main.data
    
    # sign up testing set up
    def signup(self, username, password):
        return self.app.post('/signup', data = dict(
            name = username, password = password))
    
    # log in testing set up
    def login(self, username, password):
        return self.app.post('/login', data = dict(
            name = username, password = password))
 
    # test sign up and log in
    def test_signup_login(self):
        signup_chong = self.signup('chong', '123')
        # 1 for the frist time, 0 for signing up again
        assert '1' in signup_chong.data
        # the sign up response does not contain the won lost numbers
        assert ' ' not in signup_chong.data
        login_chong = self.login('chong', '123')
        # the log in response has won and lost numbers seperated by space
        assert ' ' in login_chong.data

    # game test set up
    def setup_game(self, restart):
        return self.app.post('/game', data = dict(restart = restart))


    # test the game response
    def test_game(self):
        # initial the first game
        login_chong = self.login('chong', '123')
        initial_game = json.loads(self.setup_game('').data)
        assert int(initial_game['len']) > 0
        
        # restart a game
        restart_game = json.loads(self.setup_game('1').data)
        assert len(restart_game['guessed_char']) == 0
        assert len(restart_game['missed_char']) == 0

    # end game test set up
    def end_game(self, hits, misses, name):
        return self.app.post('/end', data = dict(
            hits = hits, misses = misses, name = name))

    # test the end game condition
    def test_end_game(self):
        # lost the game
        signup_lost_game = self.signup('ct','123')
        login_chong = self.login('ct', '123')
        lost_game = self.end_game(1, 10, 'ct')
        assert len(lost_game.data) > 0

        # won the game
        signup_won_game = self.signup('c','123')
        login_chong = self.login('c', '123')
        first_game = json.loads(self.setup_game('').data)
        the_answer = int(first_game['len']) 
        won_game = self.end_game(the_answer, 1, 'c')
        assert won_game.data == '1'  

    # test guess set up
    def setup_guess(self, guess_char):
        return self.app.get('/cal_guess', query_string = dict(
            guess_char = guess_char))

    # test the single guess
    def test_guess(self):
        signup_won_game = self.signup('c','123')
        login_chong = self.login('c', '123')
        with self.app as c:
            # test single guess
            with c.session_transaction() as sess:
                sess['the_answer']= 'the'
            good_reply = json.loads(self.setup_guess('e').data)
            assert good_reply[0]['index'] == 2
            good_reply = json.loads(self.setup_guess('t').data)
            assert good_reply[0]['index'] == 0
            miss_reply = json.loads(self.setup_guess('o').data)
            assert len(miss_reply) == 0
            miss_reply = json.loads(self.setup_guess('i').data)
            assert len(miss_reply) == 0
            
            # test guess return length
            with c.session_transaction() as sess:
                sess['the_answer']= 'ssss'
            good_reply = json.loads(self.setup_guess('s').data)
            assert len(good_reply) == 4
            good_reply = json.loads(self.setup_guess('s').data)
            assert good_reply[3]['index'] == 3
            miss_reply = json.loads(self.setup_guess('S').data)
            assert len(miss_reply) == 0
            miss_reply = json.loads(self.setup_guess('x').data)
            assert len(miss_reply) == 0

if __name__=='__main__':
    unittest.main()
