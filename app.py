#!/usr/bin/env python
from random import randrange
from threading import Lock

from flask import Flask, session, request
from flask_socketio import SocketIO, emit, join_room, rooms
from flask_sqlalchemy import SQLAlchemy
import datetime

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tictactoe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *
from forms import *

socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

global turn
turn = None

#global board
board = {1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '', 9: ''}
global userboard
userboard = {}

def check_winner(room, board):
    # first row
    if (board[room][1] == board[room][2] == board[room][3]) and (board[room][1] is not None and board[room][2] is not None and board[room][3] is not None):
        print('\nGame over.')
        print('{} won'.format(board[room][1]))
        return True, board[room][1]
    # middle row
    elif board[room][4] == board[room][5] == board[room][6] and (board[room][4] is not None and board[room][5] is not None and board[room][6] is not None):
        print('\nGame over.')
        print('{} won'.format(board[room][4]))
        return True, board[room][4]
    # last row
    elif board[room][7] == board[room][8] == board[room][9] and (board[room][7] is not None and board[room][8] is not None and board[room][9] is not None):
        print('\nGame over.')
        print('{} won'.format(board[room][7]))
        return True, board[room][7]
    # first column
    elif board[room][1] == board[room][4] == board[room][7] and (board[room][1] is not None and board[room][4] is not None and board[room][7] is not None):
        print('\nGame over.')
        print('{} won'.format(board[room][1]))
        return True, board[room][1]
    # middle column
    elif board[room][1] == board[room][5] == board[room][9] and (board[room][1] is not None and board[room][5] is not None and board[room][9] is not None):
        print('\nGame over.')
        print('{} won'.format(board[room][1]))
        return True, board[room][1]
    # last column
    elif board[room][3] == board[room][6] == board[room][9] and (board[room][3] is not None and board[room][6] is not None and board[room][9] is not None):
        print('\nGame over.')
        print('{} won'.format(board[room][3]))
        return True, board[room][3]
    # diagonal left
    elif board[room][1] == board[room][5] == board[room][9] and (board[room][1] is not None and board[room][5] is not None and board[room][9] is not None):
        print('\nGame over.')
        print('{} won'.format(board[room][1]))
        return True, board[room][1]
	# diagonal right
    elif board[room][3] == board[room][5] == board[room][7] and (board[room][3] is not None and board[room][5] is not None and board[room][7] is not None):
        print('\nGame over.')
        print('{} won'.format(board[room][3]))
        return True, board[room][3]

@app.route('/', methods=['POST', 'GET'])
def index():
    '''
    Create room for game and join it
    :return:
    '''
    #userboard.clear()
    #board.clear()
    create_room = Room()
    gameroom = JoinRoom()

    if request.method == 'POST':

        if create_room.createroom.data:
            if create_room.validate() == False:
                return render_template('index.html', title='Flask socketio example', createroomform=create_room, joinform=gameroom)
            else:

                roomnumber = randrange(1000, 9999)
                playername = create_room.name.data
                first_player_symbol = 'O'

                mytictactoe = TicTac(id=roomnumber, player1_name=playername, player1_id=first_player_symbol, start_time=datetime.datetime.now())

                try:
                    db.session.add(mytictactoe)
                    db.session.commit()
                except Exception as ex:
                    print('Error in creating new room: {} - {}'.format(roomnumber, ex))

                return render_template('game.html', title='Flask socketio example', player=playername, room=roomnumber, playersymbol = first_player_symbol)

        if gameroom.joinroom.data:
            if gameroom.validate() == False:
                return render_template('index.html', title='Flask socketio example', createroomform=create_room, joinform=gameroom)
            else:
                playername = gameroom.name.data
                roomnumber = gameroom.roomnumber.data
                second_player_symbol = 'X'

                try:
                    mytictactoe = TicTac.query.get_or_404(roomnumber)
                    if mytictactoe is not None:
                        mytictactoe.player2_name = playername
                        mytictactoe.player2_id = second_player_symbol
                        db.session.commit()
                except Exception as ex:
                    print('Error in joining room:{} - {}'.format(roomnumber, ex))

                return render_template('game.html', title='Flask socketio example', player=playername, room=roomnumber, playersymbol = second_player_symbol)

    elif request.method == 'GET':
        return render_template('index.html', title='Flask socketio example', createroomform=create_room,
                               joinform=gameroom)


@app.route('/game')
def game():
    return render_template('game.html', async_mode=socketio.async_mode)


'''
@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})
'''


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    print('Here')
    global turn
    if turn is None:
        turn = 'O'

    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count'], 'tictac': turn},
         broadcast=True)

    if turn == 'O':
        turn = 'X'
    else:
        turn = 'O'



@socketio.on('join', namespace='/test')
def join(message):
    #print(message['room'])
    #print('Room Number : {}'.format(message['room']))
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    '''
    print(join(rooms()))
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})'''

'''
@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])
'''

@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):

    rightwrong = False
    global userboard
    #global board

    userboard.clear()

    userboard = {message['room']: board}
    pos = message['data'].replace('btn','')
    print(message['data'].replace('btn',''))
    print(message['playersymbol'])

    turn = message['playersymbol']

    session['receive_count'] = session.get('receive_count', 0) + 1
    userboard[message['room']][int(message['data'].replace('btn', ''))] = turn

    try:
        mytictactoe = TicTac.query.get_or_404(message['room'])

        if mytictactoe.turn is None and turn == 'O':
            col = 'mytictactoe.col{}="{}"'.format(pos, turn)
            print(col)
            exec(col)
            col = 'mytictactoe.turn="{}"'.format('X')
            exec(col)
            db.session.commit()
            rightwrong = True
        elif mytictactoe.turn == 'O' and mytictactoe.turn == 'O':
            col = 'mytictactoe.col{}="{}"'.format(pos, turn)
            print(col)
            exec(col)
            col = 'mytictactoe.turn="{}"'.format('X')
            exec(col)
            db.session.commit()
            rightwrong = True
        elif mytictactoe.turn == 'X' and mytictactoe.turn == 'X':
            col = 'mytictactoe.col{}="{}"'.format(pos, turn)
            print(col)
            exec(col)
            col = 'mytictactoe.turn="{}"'.format('O')
            exec(col)
            db.session.commit()
            rightwrong = True
        else:
            print('Wrong turn')
            rightwrong = False


        print(mytictactoe)
    except Exception as ex:
        print('Error in room: {}. {}'.format(message['room'], ex))

    print('button: {}'.format(message['data']))

    if rightwrong:
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count'], 'tictac': turn},
             room=message['room'])
    else:
        emit('my_result',
             {'result': 'Wrong Turn: {}, Try again!'.format(turn)},
             room=message['room'])

    if rightwrong:
        try:
            mytictactoe = TicTac.query.get_or_404(message['room'])
            #print(mytictactoe.__dict__)
            #print(type(mytictactoe))
            userboard[message['room']][1] = mytictactoe.col1
            userboard[message['room']][2] = mytictactoe.col2
            userboard[message['room']][3] = mytictactoe.col3
            userboard[message['room']][4] = mytictactoe.col4
            userboard[message['room']][5] = mytictactoe.col5
            userboard[message['room']][6] = mytictactoe.col6
            userboard[message['room']][7] = mytictactoe.col7
            userboard[message['room']][8] = mytictactoe.col8
            userboard[message['room']][9] = mytictactoe.col9

        except Exception as ex:
            print('Error in query :{}'.format(message['room']))

        print(len([item for item in userboard[message['room']].values() if item !='']))
        numOfRound = len([item for item in userboard[message['room']].values() if item is not None])

        if numOfRound >= 5:
            winner = check_winner(message['room'],userboard)
            print('Round check')
            print(winner)
            if winner is not None:
                if winner[0] == True:
                    print('Hey {}, you won'.format(winner[1]))

                    emit('my_result',
                         {'result': 'Hey {}, you won'.format(winner[1])},
                         room=message['room'])

            if numOfRound >= 9 and winner is None:
                print('Its draw!')
                emit('my_result',
                     {'result': 'Draw, Try again!'},
                     room=message['room'])

    print(userboard)
    print(message)
    print('message room:{}'.format(message['room']))


'''
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')
'''
'''
@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})
'''
'''
@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)
'''


@socketio.on('vote', namespace='/test')
def handleVote(ballot):
    vote = VotingResult(vote=ballot)
    db.session.add(vote)
    db.session.commit()

    results1 = VotingResult.query.filter_by(vote=1).count()
    results2 = VotingResult.query.filter_by(vote=2).count()

    emit('vote_results', {'results1': results1, 'results2': results2}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
