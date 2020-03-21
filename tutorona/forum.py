import pytz
from datetime import datetime

from flask import Blueprint, request, g, abort, render_template, redirect, url_for

from tutorona.auth import login_required
from tutorona.db import get_db

bp = Blueprint('forum', __name__)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
  db = get_db()
  user = g.user

  if user is None:
    abort(403)

  if request.method == 'GET':
    lang = user['lang']
    posts = db.execute(
      "SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id WHERE posts.lang = ? \
      ORDER BY created DESC", 
      (lang,)
    ).fetchall()

    return render_template('forum/index.html', posts=posts)
  
  elif request.method == 'POST':
    lang = user['lang']
    title = request.form.get('title')
    post_content = request.form.get('post_content')

    if title is None or post_content is None or title == "" or post_content == "":
      abort(400, "please add a title/content!") # post missing title or content
    if len(title) > 128:
      abort(400, "title too long (max 128 characters)") # too long for database

    db.execute(
      "INSERT INTO posts (title, post_content, created, lang, user_id) VALUES (?, ?, ?, ?, ?)",
      (title, post_content, datetime.now().astimezone(pytz.timezone('US/Eastern')), lang, user['id'])
    )
    db.commit()

    return redirect(url_for('index'))


@bp.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def forum_post(id):
  db = get_db()
  user = g.user

  if user is None:
    abort(403)
  
  if request.method == 'GET':
    post = db.execute(
      "SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id WHERE posts.id=?", 
      (id,)
    ).fetchone()

    comments = db.execute(
      "SELECT comments.*, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE comments.post_id=? \
      ORDER BY created DESC",
      (id,)
    )

    return render_template('forum/post.html', forum_post=post, comments=comments)


@bp.route('/comment/<int:id>', methods=['POST'])
@login_required
def comment(id):
  db = get_db()
  user = g.user
  post_id = id

  comment_text = request.form.get('comment')
  if comment_text is None:
    return abort(403)
  
  db.execute(
    "INSERT INTO comments (comment_content, created, post_id, user_id) VALUES (?, ?, ?, ?)",
    (comment_text, datetime.now().astimezone(pytz.timezone('US/Eastern')), post_id, user['id'])
  )
  db.commit()

  return redirect(url_for('forum.forum_post', id=post_id))
  