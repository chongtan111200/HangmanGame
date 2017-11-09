This game is written in Python Flask. The game requires signing up and logging in to record the hits and misses in the relational database. The server generates randomly a word from an English dictionary. The server then passes the length to the frontend so the frontend could create the empty slots for the player to guess. The player guesses one character at a time, and this character would be passed to the server to check if it is a hit. If so, the server would pass back the hit with the index. The frontend displays the hit and miss. The frontend displays part of the hanging man according to the number of misses. If the misses are 10, the game is over and the whole picture is displayed. 

2.	Installation
•	Unzip all the files into a folder
•	Navigate to the unzipped folder
•	Set up virtualenv
o	$ virtualenv venv
o	$ source venv/bin/activate
•	Install dependencies 
o	$ pip install –r requirements.txt
•	Set up the database
o	$ python db.py
•	Start the server
o	$ python hangman.py
•	Use a browser to load http://127.0.0.1:5000/
•	The game starts

3.	Playing the game
The game requires signing up and logging in.
•	For the first time player, type in the username and password, and click “sign up”. Then click “log in”.
•	For registered player, type in the username and password, and click “log in”.
•	Put in one character each time, hit “enter” or click “submit”.
•	Win the game or lose the game according to the rules.
•	Click “restart” after winning or losing the game.

