import pytz
from datetime import datetime
# from hashlib import sha256

from flask import Blueprint, g, render_template, request, redirect, url_for, abort, session
from flask_socketio import SocketIO, join_room, emit

from .auth import login_required
from .db import get_db, get_dict_cursor
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
	cur = get_dict_cursor(db)
	content = msg['content']
	recipient = msg['recipient']
	sender = msg['sender']

	if content == '' or recipient == '' or sender == '':
		return abort(403, 'no content or user on message sent')

	cur.execute("SELECT * FROM users WHERE id = %s;", (sender,))
	user = cur.fetchone()
	cur.execute("SELECT * FROM users WHERE id = %s;", (recipient,))
	other_user = cur.fetchone()
	if user is None or other_user is None:
		return abort(403, 'message sent to/from nonexistent user')

	current_time = datetime.now().astimezone(pytz.timezone('US/Eastern'))

	cur.execute(
		"INSERT INTO messages (sender, recipient, created, content) VALUES (%s, %s, %s, %s);",
		(sender, recipient, current_time, content)
	)
	db.commit()
	cur.close()

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
	cur = get_dict_cursor(db)
	user = g.user

	cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
	other_user = cur.fetchone()
	if other_user is None:
		return abort(404, "user does not exist")

	cur.execute(
		"SELECT * FROM messages WHERE sender = %s AND recipient = %s OR sender = %s AND recipient = %s \
		ORDER BY created ASC;",
		(user['id'], other_user['id'], other_user['id'], user['id'])
	)
	messages = cur.fetchall()
	cur.close()

	return render_template('chat/chatroom.html', other_user=other_user, messages=messages)


@bp.route('/send/<id>', methods=['POST'])
@login_required
def send_message(id):
	db = get_db()
	cur = get_dict_cursor(db)
	user = g.user
	cur.execute("SELECT * FROM users WHERE id = %s;", (id,))
	other_user = cur.fetchone()
	room = hash_unique_room(user['id'], id)

	# verify that other user exists

	message_content = request.form.get('message')
	if message_content is None:
		return abort(403, 'please send a message!')

	current_time = datetime.now().astimezone(pytz.timezone('US/Eastern'))

	cur.execute(
		"INSERT INTO messages (sender, recipient, created, content) VALUES (%s, %s, %s, %s)",
		(user['id'], id, current_time, message_content)
	)
	db.commit()
	cur.close()

	message = {
		'sender': user['id'],
		'recipient': id,
		'created': current_time,
		'content': message_content
	}

	socketio.emit('chat_message', message, room=room)
	return redirect(url_for('chat.chat', username=other_user['username']))

