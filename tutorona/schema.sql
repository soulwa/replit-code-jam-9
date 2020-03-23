DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS tags_to_posts;

CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(32) NOT NULL UNIQUE,
  pw_hash TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  created DATETIME NOT NULL,
  last_signin DATETIME NOT NULL,
  lang CHAR(3) NOT NULL,
  bio TEXT NOT NULL DEFAULT ''
);

CREATE TABLE posts (
  id INTEGER PRIMARY KEY,
  title VARCHAR(128) NOT NULL,
  post_content TEXT NOT NULL,
  created DATETIME NOT NULL,
  lang CHAR(2) NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE comments (
  id INTEGER PRIMARY KEY,
  comment_content TEXT NOT NULL,
  created DATETIME NOT NULL,
  post_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY(post_id) REFERENCES posts(id),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE tags (
  id INTEGER PRIMARY KEY,
  tag_content TEXT NOT NULL,
);

CREATE TABLE tags_to_posts (
  post_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  FOREIGN KEY(post_id) REFERENCES posts(id),
  FOREIGN KEY(tag_id) REFERENCES tags(id)
);