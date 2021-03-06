import pickle, random, os
from flask import Flask, render_template, redirect, session, request, make_response
from flask_session import Session

IP = 'localhost'

# Configure routes
homeaddress = 'http://' + IP + ':5000/'
initaddress = 'http://' + IP + ':5000/init'
p1address = 'http://' + IP + ':5000/player1'
p2address = 'http://' + IP + ':5000/player2'
exitaddress = 'http://' + IP + ':5000/exit'

CWD = os.getcwd()

app = Flask(__name__)


# Display board in console
def display(board):
    for i in range(3):
        print (board[i][0] + ' | ' + board[i][1] + ' | ' + board[i][2])
        if i<2:
            print ('---------')

# Get move from console input and validate. Return updated list of used moves
def getmove(used, turn):
    validated = False
    while validated == False:
        move = input('Player ' + str(turn) + ' Move (1 - 9): ')
        move = move-1
        if move>=0 and move<9:
            if move not in used:
                used.append(move)
                validated = True
    return used

# If new move is not already used, update and return list of used moves
def addmove(used, move):
    move -= 1
    if move not in used:
        used.append(move)
    return used

# Update board with current move, return board
def updateboard(board, move, symbol):
    move -= 1
    if move < 3:
        board[0][move%3] = symbol
    elif move < 6:
        board[1][move%3] = symbol
    elif move < 9:
        board[2][move%3] = symbol
    return board

# Check board to see if there is a winner
def checkforwinner(board):
    winner = 0
    for i in range(3):
        if board[i][0]=='X' and board[i][1]=='X' and board[i][2]=='X':
            winner = 1
        elif board[0][i]=='X' and board[1][i]=='X' and board[2][i]=='X':
            winner = 1
        elif board[i][0]=='O' and board[i][1]=='O' and board[i][2]=='O':
            winner = 2
        elif board[0][i]=='O' and board[1][i]=='O' and board[2][i]=='O':
            winner = 2
    if board[0][0]=='X' and board[1][1]=='X' and board[2][2]=='X':
        winner = 1
    elif board[0][2]=='X' and board[1][1]=='X' and board[2][0]=='X':
        winner = 1
    elif board[0][0]=='O' and board[1][1]=='O' and board[2][2]=='O':
        winner = 2
    elif board[0][2]=='O' and board[1][1]=='O' and board[2][0]=='O':
        winner = 2
    return winner

# End the game by writing '0' to turnFile
def endgame():
    try:
        boardFile, usedFile, turnFile = getFileNames()
    except:
        return redirect(exitaddress)
    with open(turnFile, 'w') as f:
        f.write('0')
    return

# Return gameID cookie
def getcookies():
    cookies = dict()
    cookies['gameID'] = request.cookies.get('gameID')
    cookies['player'] = request.cookies.get('player')
    return cookies

# Return filenames for a given game based on the assigned cookie value
def getFileNames():
    cookies = getcookies()
    try:
        boardFile = CWD + '/gameFiles/' + cookies['gameID'] + 'board.txt'
        usedFile = CWD + '/gameFiles/' + cookies['gameID'] + 'used.txt'
        turnFile = CWD + '/gameFiles/' + cookies['gameID'] + 'turn.txt'
    except:
        return
    return boardFile, usedFile, turnFile

# Initialize specific game's files
def initgame():
    try:
        boardFile, usedFile, turnFile = getFileNames()
    except:
        return redirect(homeaddress)
    used = []
    board = []
    for i in range(3):
        board.append([' ', ' ', ' '])

    with open(boardFile, 'w') as f:
        pickle.dump(board, f)
    with open(usedFile, 'w') as f:
        pickle.dump(used, f)
    with open(turnFile, 'w') as f:
        f.write('1')
    return

# Return current game state based on assigned cookies
def getGameState():
    try:
        boardFile, usedFile, turnFile = getFileNames()
    except:
        return
    with open(boardFile, 'r') as f:
        board = pickle.load(f)
    with open(usedFile, 'r') as f:
        used = pickle.load(f)
    with open(turnFile, 'r') as f:
        turn = f.read()
    return board, used, turn

# Update game state based on assigned cookies
def updateGameState(board, used, turn):
    try:
        boardFile, usedFile, turnFile = getFileNames()
    except:
        return redirect(exitaddress)
    with open(boardFile, 'w') as f:
        pickle.dump(board, f)
    with open(usedFile, 'w') as f:
        pickle.dump(used, f)
    with open(turnFile, 'w') as f:
        f.write(turn)
    return

# Validate player 1 move and update game if valid
def p1move(move):
    try:
        board, used, turn = getGameState()
    except:
        return redirect(exitaddress)
    if turn == '0':
        return redirect(exitaddress)
    elif turn != '1':
        return
    oldlength = len(used)
    used = addmove(used, move)
    if len(used) > oldlength:
        board = updateboard(board, move, 'X')
        updateGameState(board, used, '2')
    return

# Validate player 2 move and update if valid
def p2move(move):
    try:
        board, used, turn = getGameState()
    except:
        return redirect(exitaddress)
    if turn == '0':
        return redirect(exitaddress)
    elif turn != '2':
        return
    oldlength = len(used)
    used = addmove(used, move)
    if len(used) > oldlength:
        board = updateboard(board, move, 'O')
        updateGameState(board, used, '1')
    return

# Delete game files of a specific game based on cookies if they exist
def deleteData():
    try:
        boardFile, usedFile, turnFile = getFileNames()
    except:
        return redirect(homeaddress)
    try:
        os.remove(boardFile)
    except OSError:
        pass
    try:
        os.remove(usedFile)
    except OSError:
        pass
    try:
        os.remove(turnFile)
    except OSError:
        pass
    return

# Check if specific game files exist
def checkFiles():
    try:
        boardFile, usedFile, turnFile = getFileNames()
    except:
        return redirect(homeaddress)
    if os.path.isfile(boardFile):
        return True
    else:
        return False

# Count number of existing game files. If over threshold, delete oldest game.
def deleteExcessFiles():
    files = dict()
    count = 0
    for file in os.listdir(CWD + '/gameFiles'):
        if file.endswith('.txt'):
            count += 1
            files[file] = os.stat(CWD + '/gameFiles/' + file).st_mtime
    if count > 300:
        filePrefix = min(files, key=files.get)[:6]
        try:
            os.remove(CWD + '/gameFiles/' + filePrefix + 'board.txt')
        except OSError:
            pass
        try:
            os.remove(CWD + '/gameFiles/' + filePrefix + 'used.txt')
        except OSError:
            pass
        try:
            os.remove(CWD + '/gameFiles/' + filePrefix + 'turn.txt')
        except OSError:
            pass
    return

def randomize():
    try:
        boardFile, usedFile, turnFile = getFileNames()
        with open(turnFile, 'w') as f:
            f.write(str(random.randint(1,2)))
    except:
        pass
    return


#####################################
# Primary routes
#####################################

# Home HTML
@app.route("/")
def home():
    return render_template('home.html')

# Create a game, assigns gameID cookie to client
@app.route("/creategame")
def creategame():
    gameID = getcookies()['gameID']
    if gameID is None:
        while True:
            gameID = str(random.randint(100000, 999999))
            if not os.path.isfile(CWD + '/gameFiles/' + gameID + 'board.txt'):
                break
    resp = make_response(redirect(initaddress))
    resp.set_cookie('gameID', gameID)
    resp.set_cookie('player', '1')
    return resp

# Initialize game based on cookies and delete excess files
@app.route("/init")
def init():
    gameID = getcookies()['gameID']
    if gameID is None:
        return redirect(homeaddress)
    message = 'Game ID: ' + gameID
    initgame()
    deleteExcessFiles()
    return render_template('gameID.html', message=message)

# Join game HTML
@app.route("/joingame")
def joingame():
    return render_template('joingame.html')

# Receive gameID post, set cookie and load HTML on success, redirect to join game HTML on failure
@app.route("/joinpost", methods=["POST"])
def joinpost():
    if request.method == "POST":
        gameID = request.form['gameID']
        if os.path.isfile(CWD + '/gameFiles/' + gameID + 'board.txt'):
            message = 'Successfully joined game ' + gameID + '.'
            resp = make_response(render_template('gamejoined.html', message=message))
            resp.set_cookie('gameID', gameID)
            resp.set_cookie('player', '2')
            return resp
    return render_template('joingame.html')

# Delete game files, clear gameID cookie
@app.route("/exit")
def exit():
    deleteData()
    resp = make_response(redirect(homeaddress))
    resp.set_cookie('gameID', '', expires=0)
    return resp

# Player 1 board
@app.route("/player1")
def p1():
    if getcookies()['player'] == '2':
        return redirect(p2address)
    if checkFiles() == False:
        return redirect(homeaddress)
    try:
        board, used, turn = getGameState()
    except:
        return redirect(exitaddress)
    if turn == '1':
        message = 'Your move, player 1.'
    else:
        message = 'Waiting on player 2.'

    #display(board)
    winner = checkforwinner(board)

    if winner == 1:
        message = 'You won! Nice job, but don\'t you have work you should be doing?'
        endgame()
    elif winner == 2:
        message = 'You lost! Don\'t worry though, I still believe in you.'
        endgame()
    elif len(used) == 9 and winner == 0:
        message = 'Wow. It\'s a tie...shocker.'

    gameIDmessage = 'Game ID: ' + getcookies()['gameID']
    return render_template('p1board.html', board=board, message=message, gameID=gameIDmessage)

# Player 2 board
@app.route("/player2")
def p2():
    if getcookies()['player'] == '1':
        return redirect(p1address)
    if checkFiles() == False:
        return redirect(homeaddress)
    try:
        board, used, turn = getGameState()
    except:
        return redirect(exitaddress)
    if turn == '2':
        message = 'Your move, player 2.'
    else:
        message = 'Waiting on player 1.'

    #display(board)
    winner = checkforwinner(board)

    if winner == 1:
        message = 'You lost! Don\'t worry though, I still believe in you.'
        endgame()
    elif winner == 2:
        message = 'You won! Nice job, but don\'t you have work you should be doing?'
        endgame()
    elif len(used) == 9 and winner == 0:
        message = 'Wow. It\'s a tie...shocker.'

    gameIDmessage = 'Game ID: ' + getcookies()['gameID']
    return render_template('p2board.html', board=board, message=message, gameID=gameIDmessage)

@app.route("/p1restart")
def p1restart():
    initgame()
    randomize()
    return redirect(p1address)

@app.route("/p2restart")
def p2restart():
    initgame()
    randomize()
    return redirect(p2address)

#####################################
# Individual move routes
#####################################

@app.route("/p1-1")
def p11():
    p1move(1)
    return redirect(p1address)

@app.route("/p1-2")
def p12():
    p1move(2)
    return redirect(p1address)

@app.route("/p1-3")
def p13():
    p1move(3)
    return redirect(p1address)

@app.route("/p1-4")
def p14():
    p1move(4)
    return redirect(p1address)

@app.route("/p1-5")
def p15():
    p1move(5)
    return redirect(p1address)

@app.route("/p1-6")
def p16():
    p1move(6)
    return redirect(p1address)

@app.route("/p1-7")
def p17():
    p1move(7)
    return redirect(p1address)

@app.route("/p1-8")
def p18():
    p1move(8)
    return redirect(p1address)

@app.route("/p1-9")
def p19():
    p1move(9)
    return redirect(p1address)

@app.route("/p2-1")
def p21():
    p2move(1)
    return redirect(p2address)

@app.route("/p2-2")
def p22():
    p2move(2)
    return redirect(p2address)

@app.route("/p2-3")
def p23():
    p2move(3)
    return redirect(p2address)

@app.route("/p2-4")
def p24():
    p2move(4)
    return redirect(p2address)

@app.route("/p2-5")
def p25():
    p2move(5)
    return redirect(p2address)

@app.route("/p2-6")
def p26():
    p2move(6)
    return redirect(p2address)

@app.route("/p2-7")
def p27():
    p2move(7)
    return redirect(p2address)

@app.route("/p2-8")
def p28():
    p2move(8)
    return redirect(p2address)

@app.route("/p2-9")
def p29():
    p2move(9)
    return redirect(p2address)


# Run app at machine's IP and port 5000
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
