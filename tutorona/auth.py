import functools
import pytz
from datetime import datetime

from flask import abort, Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__)

# abort(400) is a temporary solution, so nobody can register an invalid user
# will update with flash(error) and a client side prevention (eg bootstrap)
@bp.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    if not request.form.get('email'):
      return abort(400) # no email
    if not request.form.get('username'):
      print('no username')
      return abort(400) # no username
    if not request.form.get('password'):
      print('no pw')
      return abort(400) # no pw
    if not request.form.get('confirmation'):
      print('no confirm')
      return abort(400) # pw not confirmed
    if not request.form.get('language'):
      print('no lang')
      return abort(400) # no lang selected

    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    confirmation = request.form.get('confirmation')
    language = request.form.get('language')

    if password != confirmation:
      print('pw != conf')
      abort(400) # make sure pw and confirmation match
    
    db = get_db()
    if db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone() is not None:
      print('username taken')
      abort(400) # username already exists
    
    if len(username) > 32:
      print('too long')
      abort(400) # name too long
    
    hashed_pw = generate_password_hash(password)
    current_time = datetime.now().astimezone(pytz.timezone('US/Eastern'))
    db.execute(
      "INSERT INTO users (username, pw_hash, email, created, last_signin, lang) VALUES (?, ?, ?, ?, ?, ?)",
      (username, hashed_pw, email, current_time, current_time, language)
    )
    db.commit()

    return redirect(url_for('auth.login'))

  elif request.method == 'GET':
    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
  session.clear()

  if request.method == 'POST':
    if not request.form.get('username'):
      return abort(401) # no username
    if not request.form.get('password'):
      return abort(401) # no pw
    
    username = request.form.get('username')
    password = request.form.get('password')
    db = get_db()
    
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if user is None:
      return abort(401) # user doesn't exist
    if not check_password_hash(user['pw_hash'], password):
      return abort(401) # password incorrect
    
    session['user_id'] = user['id']
    return redirect(url_for('index'))

  elif request.method == 'GET':
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('auth.login'))


def login_required(view):

  @functools.wraps(view)
  def wrapped_view(*args, **kwargs):
    if session.get('user_id') is None:
      return redirect(url_for('auth.login'))
    return view(*args, **kwargs)

  return wrapped_view


@bp.before_app_request
def load_user():
  user_id = session.get('user_id')
  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

