import os
import psycopg2
import psycopg2.extras
import sqlite3
import click

from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
  if 'db' not in g:
    g.db = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
  return g.db

def get_dict_cursor(db):
  return db.cursor(cursor_factory=psycopg2.extras.DictCursor)


def close_db(e=None):
  db = g.pop('db', None)
  if db is not None:
    db.close()


def init_db():
  db = get_db()
  with current_app.open_resource('schema.sql') as f, db.cursor() as cur:
    contents = f.read()
    cur.execute(contents)
    db.commit()



@click.command('init-db')
@with_appcontext
def init_db_command():
  init_db()
  print("database initialized successfully")


def init_app(app):
  app.teardown_appcontext(close_db)
  app.cli.add_command(init_db_command)
