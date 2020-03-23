from flask import Blueprint, request, g, abort, render_template, redirect, url_for, session
from tutorona.auth import login_required
from tutorona.db import get_db

bp = Blueprint('userpage', __name__)

@bp.route('/<username>', methods=['POST', 'GET'])
@login_required
def user(username):
  db = get_db()
  user = g.user

  user_info = db.execute(
    "SELECT * FROM users WHERE username = ?",
    (username,)).fetchone()
  
  # changed this so the equality check is in the template, avoids the 3rd query
  if user_info is not None:
    user_posts = db.execute("SELECT * FROM posts WHERE user_id = ?", (user_info['id'],)).fetchall()
    return render_template('userpage/index.html', user_info=user_info, user_posts=user_posts)
  else:
    return abort(403, "invalid user!")


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
  db = get_db()
  user = g.user

  if request.method=='POST':
    new_bio = request.form.get('new_bio')
    print(new_bio)
    db.execute("UPDATE users SET bio=? WHERE users.username=?", (new_bio, user['username']))
    db.commit()

  return redirect(url_for('userpage.user', username=user['username']))
