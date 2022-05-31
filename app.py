#https://flask-socketio.readthedocs.io/en/latest/getting_started.html
from flask import Flask, render_template, url_for, redirect, request, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

app = Flask(__name__)

app.debug = True
app.config['SECRET_TYPE'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'


messageList = []
Session(app)


socketio = SocketIO(app, always_connect=True)

#wejście do aplikacji, wyrenderowanie templete 'start.html'
@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('start.html')


# wypełnienie formularza
@app.route('/chatroom', methods=['GET', 'POST'])
def chatroom():
    # w momencie wysłania formularza wygeneruje się metoda post, elementy formularza zostają przypisane do zmiennych sesji
    # po czym następuje wyrenderowanie template 'chatroom.html' z przekazanymi zmiennymi sesji
    if(request.method=="POST"):
        name = request.form['name']
        room = request.form['room']

        session['name'] = name
        session['room'] = room
        return render_template('chatroom.html', session = session)

    # zabezpieczenie
    else:
        if(session.get('name') is not None):
            return render_template('chatroom.html', session=session)
        else:
            return redirect(url_for('start'))





# przy połączeniu
@socketio.on('connect')
def connected():
    #lista wiadomości (ulotna baza danych) zostaje zresetowana
    messageList = []
    print('Connection established!')
    


# sprawdzenie poprawnego odłączenia
@socketio.on('disconnect')
def disconnect():
    print('Disconnected from session')




# wyemitowanie wiadomości (statusu) o dołączeniu użytkowanika
# namespace odnosi sie do miejsca, gdzie nadsłuchujemy 
@socketio.on('join', namespace='/chatroom')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('name') + ' entered the room.', 'author': session.get('name')}, room=room)




# wyemitowanie wiadomości
@socketio.on('text', namespace='/chatroom')
def text(message):
    #jeśli wiadomość jest pusta, odrzuć
    if (not message['msg']): 
        return

    room = session.get('room')

    # pobranie wiadomości
    newMessage = {'msg': message['msg'], 'author': session.get('name')}

    # dodanie wiadomości do listy wszystkich wiadomości sesji - "ulotna baza danych", utrzymywana tylko podczas sesji
    messageList.append(newMessage)
    print(messageList)

    #wyemitowanie wiadomości, która zostaje wyświetlona w HTML
    emit('message', newMessage, room=room)




# wyemitowanie wiadomości ze zdjęciem - wczytane zostało za pomocą <input type="file"> 
# i przekształcone do formatu DataURL, czyli tekstowego opisu pliku
@socketio.on('image-upload', namespace='/chatroom')
def imageUpload(image):
    room= session.get('room')
    emit('send-image', {'msg': image, 'author': session.get('name')}, room=room, broadcast=True)




# funkcja wykonywana podczas wyjścia z pokoju
@socketio.on('left', namespace='/chatroom')
def left(message):
    room = session.get('room')
    name = session.get('name')

    #wyczyszczeniee tablicy sesji
    session.clear()
    #wyemitowanie wiadomosci (statusu) o wyjściu
    emit('status', {'msg': name + ' has left the room', 'author': session.get('name')}, room=room)





if __name__ == '__main__':
    socketio.run(app, debug=True)
