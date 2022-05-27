#https://flask-socketio.readthedocs.io/en/latest/getting_started.html
from flask import Flask, render_template, url_for, redirect, request, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

app = Flask(__name__)

app.debug = True
app.config['SECRET_TYPE'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'


messageList = []
matchesList = []


Session(app)

socketio = SocketIO(app,always_connect=True, engineio_logger=True)


@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('start.html')


@app.route('/chatroom', methods=['GET', 'POST'])
def chatroom():
    #jeśli została wywołana metoda post (w momencie wysłania formularza z pokojem)
    if(request.method=="POST"):
        name = request.form['name']
        room = request.form['room']

        session['name'] = name
        session['room'] = room
        return render_template('chatroom.html', session = session)
    else:
        if(session.get('name') is not None):
            return render_template('chatroom.html', session=session)
        else:
            return redirect(url_for('start'))


@app.route('/messenger', methods=['GET', 'POST'])
def messenger():
    pass





@socketio.on('connect')
def connected():
    print('connect')
    
@socketio.on('disconnect')
def disconnect():
    print('disconnect')



@socketio.on('join', namespace='/chatroom')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('name') + ' entered the room.', 'author': session.get('name')}, room=room)



@socketio.on('text', namespace='/chatroom')
def text(message):
    if (not message['msg']): 
        return
    room = session.get('room')  
    newMessage = {'msg': message['msg'], 'author': session.get('name')}
    messageList.append(newMessage)
    print(messageList)
    emit('message', newMessage, room=room)



@socketio.on('image-upload', namespace='/chatroom')
def imageUpload(image):
    room= session.get('room')
    emit('send-image', {'msg': image, 'author': session.get('name')}, room=room)

# @socketio.on('image-upload')
# def imageUpload(image):
#     emit('send-image', image, broadcast = True)




@socketio.on('left', namespace='/chatroom')
def left(message):
    room = session.get('room')
    print(room)
    name = session.get('name')
    leave_room(room)
    session.clear()
    emit('status', {'msg': name + ' has left the room', 'author': session.get('name')}, room=room)




@socketio.on('message')
def handleMessage(data):
    print('received message: ' + data)
    



if __name__ == '__main__':
    
    socketio.run(app, debug=True)
