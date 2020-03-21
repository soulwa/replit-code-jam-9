import os

from flask import Flask
from werkzeug.exceptions import HTTPException

from . import db
from . import auth, forum, userpage
from . import error

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY = 'dev',
    DATABASE = os.path.join(app.instance_path, 'db.sqlite3'),
  )

  if test_config is None:
    app.config.from_pyfile('config.py', silent=True)
  else:
    app.config.from_mapping(test_config)
  
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass
  
  db.init_app(app)

  app.register_blueprint(auth.bp)

  app.register_blueprint(forum.bp)
  app.register_blueprint(userpage.bp)
  app.add_url_rule('/', endpoint='index')

  app.register_error_handler(404, error.handle_http_404)
  app.register_error_handler(HTTPException, error.handle_http_exception)

  return app
