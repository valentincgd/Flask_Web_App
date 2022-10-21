DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS recipes;

CREATE TABLE users (
  user_mail TEXT UNIQUE NOT NULL PRIMARY KEY,
  user_username TEXT UNIQUE NOT NULL,
  user_password TEXT NOT NULL
);

CREATE TABLE recipes (
  recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
  recipe_author_mail INTEGER NOT NULL,
  recipe_name TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (recipe_author_mail) REFERENCES users (user_mail)
);