PRAGMA FOREIGN_KEY = ON;
PRAGMA ENCODING = "UTF-8";

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS recipes;
CREATE TABLE users (
    user_mail VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY,
    user_username VARCHAR(255) UNIQUE NOT NULL,
    user_password VARCHAR(255) NOT NULL
);
CREATE TABLE recipes (
    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_author VARCHAR(255) NOT NULL,
    recipe_name VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (recipe_author) REFERENCES users (user_username)
);
CREATE TABLE ingredients (
    ingre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingre_name VARCHAR(255) NOT NULL,
    ingre_img VARCHAR(255) NOT NULL
);
CREATE TABLE recipe_ingre(
    recipe_ingre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingre_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    qt INTEGER,
    FOREIGN KEY (ingre_id) REFERENCES ingredients (ingre_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id)
);

INSERT INTO "recipes" ('recipe_author', 'recipe_name', 'body') VALUES
(
    'jérém',
    'Charlotte',
    'De la pate dans la casserole je crois'
);
INSERT INTO "recipes" ('recipe_author', 'recipe_name', 'body') VALUES
(
    'jérém',
    'Tiramisu',
    'Test'
);
INSERT INTO "recipes" ('recipe_author', 'recipe_name', 'body') VALUES
(
    'jérém',
    'Moules frites',
    'Test'
);
INSERT INTO "recipe_ingre" ('ingre_id', 'recipe_id', 'qt') VALUES
(
    2,
    1,
    3
),(
    1,
    1,
    2
);
INSERT INTO "ingredients" ('ingre_name', 'ingre_img') VALUES
(
    "carottes",
    "/static/img/carottes.png"
),(
    "farine",
    "/static/img/farine.png"
);