DROP TABLE IF EXISTS tags_to_posts;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(32) NOT NULL UNIQUE,
  pw_hash TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  created TIMESTAMP NOT NULL,
  last_signin TIMESTAMP NOT NULL,
  lang CHAR(3) NOT NULL,
  bio TEXT NOT NULL DEFAULT ''
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  title VARCHAR(128) NOT NULL,
  post_content TEXT NOT NULL,
  created TIMESTAMP NOT NULL,
  lang CHAR(2) NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE comments (
  id SERIAL PRIMARY KEY,
  comment_content TEXT NOT NULL,
  created TIMESTAMP NOT NULL,
  post_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY(post_id) REFERENCES posts(id),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  tag_content TEXT NOT NULL
);

CREATE TABLE tags_to_posts (
  id SERIAL NOT NULL,
  post_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  FOREIGN KEY(post_id) REFERENCES posts(id),
  FOREIGN KEY(tag_id) REFERENCES tags(id)
);

CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  sender INTEGER NOT NULL,
  recipient INTEGER NOT NULL,
  created TIMESTAMP NOT NULL,
  content TEXT NOT NULL,
  FOREIGN KEY(sender) REFERENCES users(id),
  FOREIGN KEY(recipient) REFERENCES users(id)
);