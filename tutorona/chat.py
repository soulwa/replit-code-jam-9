import pytz
from datetime import datetime
# from hashlib import sha256

from flask import Blueprint, g, render_template, request, redirect, url_for, abort, session
from flask_socketio import SocketIO, join_room, emit

from .auth import login_required
from .db import get_db
from . import socketio

bp = Blueprint('chat', __name__)


def hash_unique_room(id1, id2):
	if id1 > id2:
		return hash(str(id2)) + hash(str(id1))
	elif id2 > id1:
		return hash(str(id2)) + hash(str(id1))
	else:
		return None


@socketio.on('connect')
def handle_connection():
	print("Client connected")


@socketio.on('disconnect')
def handle_disconnection():
	print("Client disconnected")


@socketio.on('joined')
def load_room(msg):
	# maybe db query, session user should be the same as sent user
	print(msg)
	if session.get('user_id') != int(msg['id']):
		print(session.get('user_id'))
		print(msg['id'])
		return abort(401, 'cannot load room for other users!')

	if msg['other_id'] is '' or msg['id'] is '':
		return abort(403, 'no user! socketio error')

	unique_room = hash_unique_room(msg['id'], msg['other_id'])
	join_room(unique_room)
	print("%s joined room %s" % (msg['id'], unique_room))


# duplicate from the send message- ideally turn that into an xhp request and recieve msg from ws
@socketio.on('message_send')
def handle_message(msg):
	db = get_db()
	content = msg['content']
	recipient = msg['recipient']
	sender = msg['sender']

	if content == '' or recipient == '' or sender == '':
		return abort(403, 'no content or user on message sent')

	user = db.execute("SELECT * FROM users WHERE id = ?", (sender,)).fetchone()
	other_user = db.execute("SELECT * FROM users WHERE id = ?", (recipient,)).fetchone()
	if user is None or other_user is None:
		return abort(403, 'message sent to/from nonexistent user')

	current_time = datetime.now().astimezone(pytz.timezone('US/Eastern'))

	db.execute(
		"INSERT INTO messages (sender, recipient, created, content) VALUES (?, ?, ?, ?)",
		(sender, recipient, current_time, content)
	)
	db.commit()

	message = {
		'sender': sender,
		'recipient': recipient,
		'created': str(current_time),
		'content': content
	}

	print(message)
	room = hash_unique_room(sender, recipient)
	print(room)
	emit('message_receive', message, room=room)


@bp.route('/chat/<username>', methods=['GET'])
@login_required
def chat(username):
	db = get_db()
	user = g.user

	other_user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
	if other_user is None:
		return abort(404, "user does not exist")

	messages = db.execute(
		"SELECT * FROM messages WHERE sender = ? AND recipient = ? OR sender = ? AND recipient = ? \
		ORDER BY created ASC",
		(user['id'], other_user['id'], other_user['id'], user['id'])
	).fetchall()

	return render_template('chat/chatroom.html', other_user=other_user, messages=messages)


@bp.route('/send/<id>', methods=['POST'])
@login_required
def send_message(id):
	db = get_db()
	user = g.user
	other_user = db.execute("SELECT * FROM users WHERE id = ?", (id,)).fetchone()
	room = sha256((str(sha256(user['username'].encode('utf-8'))) + str(sha256(other_user['username'].encode('utf-8')))).encode('utf-8'))

	message_content = request.form.get('message')
	if message_content is None:
		return abort(403, 'please send a message!')

	current_time = datetime.now().astimezone(pytz.timezone('US/Eastern'))

	db.execute(
		"INSERT INTO messages (sender, recipient, created, content) VALUES (?, ?, ?, ?)",
		(user['id'], id, current_time, message_content)
	)
	db.commit()

	message = {
		'sender': user['id'],
		'recipient': id,
		'created': current_time,
		'content': message_content
	}

	socketio.send('chat_message', json=message, room=room)
	return redirect(url_for('chat.chat', username=other_user['username']))

