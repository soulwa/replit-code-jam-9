import os

from flask import Flask
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException

socketio = SocketIO()

def create_app(test_config=None, debug=False):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY = 'dev',
  )

  if test_config is None:
    app.config.from_pyfile('config.py', silent=True)
  else:
    app.config.from_mapping(test_config)

  app.debug = debug
  
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass
  
  from . import db
  db.init_app(app)
  socketio.init_app(app)

  from . import auth, forum, userpage, chat
  app.register_blueprint(auth.bp)
  app.register_blueprint(forum.bp)
  app.register_blueprint(userpage.bp)
  app.register_blueprint(chat.bp)

  app.add_url_rule('/', endpoint='index')

  from . import error
  app.register_error_handler(404, error.handle_http_404)
  app.register_error_handler(HTTPException, error.handle_http_exception)

  return app
