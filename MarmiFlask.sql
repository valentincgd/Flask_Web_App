DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS recipes;
CREATE TABLE users (
    user_mail TEXT UNIQUE NOT NULL PRIMARY KEY,
    user_username TEXT UNIQUE NOT NULL,
    user_password TEXT NOT NULL
);
CREATE TABLE recipes (
    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_author INTEGER NOT NULL,
    recipe_name TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (recipe_author) REFERENCES users (user_username)
);
INSERT INTO "users"
VALUES ('j@j.j', 'j', 'j');
INSERT INTO "recipes"
VALUES (
        1,
        'j',
        'Fondant au chocolat',
        'Faire fondre le chocolat dans le bol'
    );
INSERT INTO "recipes"
VALUES (
        2,
        'j',
        'Crêpes',
        'De la pate dans la casserole je crois'
    );
INSERT INTO "recipes"
VALUES (
        3,
        'j',
        'Tiramisu',
        'Mettre gateau dans café et crème et frigo et manger'
    );