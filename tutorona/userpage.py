from flask import Blueprint, request, g, abort, render_template, redirect, url_for, session
from tutorona.auth import login_required
from tutorona.db import get_db, get_dict_cursor

bp = Blueprint('userpage', __name__)

@bp.route('/<username>', methods=['POST', 'GET'])
@login_required
def user(username):
  db = get_db()
  cur = get_dict_cursor(db)
  user = g.user

  cur.execute(
    "SELECT * FROM users WHERE username = %s;",
    (username,)
  )
  user_info = cur.fetchone()
  
  # changed this so the equality check is in the template, avoids the 3rd query
  if user_info is not None:
    cur.execute("SELECT * FROM posts WHERE user_id = %s;", (user_info['id'],))
    user_posts = cur.fetchall()
    return render_template('userpage/index.html', user_info=user_info, user_posts=user_posts)
  else:
    return abort(403, "invalid user!")


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
  db = get_db()
  cur = get_dict_cursor(db)
  user = g.user

  if request.method=='POST':
    new_bio = request.form.get('new_bio')
    print(new_bio)

    cur.execute("UPDATE users SET bio=%s WHERE users.username=%s;", (new_bio, user['username']))
    db.commit()
  
  cur.close()

  return redirect(url_for('userpage.user', username=user['username']))
