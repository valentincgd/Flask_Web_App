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
INSERT INTO "users"
VALUES ('j@j.j', 'jérém', 'j');
INSERT INTO "recipes" ('recipe_author', 'recipe_name', 'body') VALUES
(
    'j',
    'Crêpes',
    'De la pate dans la casserole je crois'
);
INSERT INTO "recipes" ('recipe_author', 'recipe_name', 'body') VALUES
(
    'j',
    'Tiramisu',
    'Test'
);
INSERT INTO "recipes" ('recipe_author', 'recipe_name', 'body') VALUES
(
    'j',
    'Moules frites',
    'Test'
);