from flask import Flask, url_for, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3
from pathlib import Path

# coding: UTF-8


if not Path("MarmiFlask.db").exists():
    db = sqlite3.connect("MarmiFlask.db")
    db.row_factory = sqlite3.Row
    db.executescript(Path("MarmiFlask.sql").read_text(encoding="utf-8"))


def log_database():
    return sqlite3.connect("MarmiFlask.db", check_same_thread=False)


app = Flask(__name__)

app.config[
    "SECRET_KEY"
] = "9af5477e9770cc80f836ba957033432486844f49e24a62c79f2df6cca073a27a"


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        conn = log_database()
        c = conn.cursor()

        # check if the form is valid
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]

        # hash the password
        pwhash = generate_password_hash(password)

        # insert the row
        sqlCmd = "INSERT INTO users (user_mail, user_password,user_username) VALUES (:email, :password,:username)"

        try:
            c.execute(
                sqlCmd,
                {
                    "email": email,
                    "password": pwhash,
                    "username": username,
                },
            )
        except sqlite3.IntegrityError:
            return render_template(
                "signup.html", error_message="Username or email already exist."
            )

        conn.commit()

        # get user id for session
        sqlCmd = "SELECT * FROM users WHERE user_mail=:email"
        userInformation = c.execute(
            sqlCmd,
            {"email": email},
        ).fetchone()

        # return success
        session["user_id"] = userInformation[0]

        return redirect("/")
    else:
        return render_template("signup.html", error_message="")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        conn = log_database()
        c = conn.cursor()

        email = request.form["email"]
        password = request.form["password"]

        # check if email exist in the database
        sqlCmd = "SELECT * FROM users WHERE user_mail=:email"
        userInformation = c.execute(
            sqlCmd,
            {"email": email},
        ).fetchone()

        if not userInformation:
            error_message = "You didn't register."
            return render_template("login.html", error_message=error_message)

        # check the password is same to password hash
        pwhash = userInformation[2]

        if check_password_hash(pwhash, password) == False:
            error_message = "Wrong password."
            return render_template("login.html", error_message=error_message)

        # login the user using session

        session["user_id"] = userInformation[0]

        # return success
        return redirect("/")

    else:
        return render_template("login.html", error_message="")


@app.route("/")
def index():
    if "user_id" in session:
        conn = log_database()
        c = conn.cursor()

        recipes = c.execute("SELECT * FROM recipes").fetchall()
        rating = c.execute(
            "SELECT rating_recipe_id, rating_author, ROUND(AVG(rating)) FROM ratings GROUP BY rating_recipe_id"
        ).fetchall()
        return render_template("index.html", recipes=recipes, rating=rating)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/recipe/<int:recipe_id>", methods=["GET", "POST"])
def recipe(recipe_id):
    if "user_id" in session:
        conn = log_database()
        c = conn.cursor()

        if request.method == "GET":

            fetchAllRecipes = "SELECT re.recipe_id, re.recipe_author, re.recipe_name, re.body, ROUND(AVG(ra.rating)) FROM recipes re INNER JOIN ratings ra ON re.recipe_id = ra.rating_recipe_id WHERE re.recipe_id = :recipe_id"
            fetchMyRecipes = "SELECT re.recipe_id, re.recipe_author, re.recipe_name, re.body, ra.rating FROM recipes re INNER JOIN ratings ra ON re.recipe_id = ra.rating_recipe_id WHERE re.recipe_id = :recipe_id AND ra.rating_author = :rating_author"
            recipe = c.execute(fetchAllRecipes, {"recipe_id": recipe_id}).fetchall()
            myRecipe = c.execute(
                fetchMyRecipes,
                {"recipe_id": recipe_id, "rating_author": session["user_id"]},
            ).fetchall()

            fetchAllIngredients = "SELECT ingredients.ingre_name, ingredients.ingre_img, recipe_ingre.qt FROM recipe_ingre INNER JOIN ingredients ON ingredients.ingre_id = recipe_ingre.ingre_id WHERE recipe_id = :recipe_id"
            ingre = c.execute(
                fetchAllIngredients,
                {"recipe_id": recipe_id},
            ).fetchall()

            return render_template(
                "recipe.html", recipes=recipe, ingres=ingre, myRecipe=myRecipe
            )

        elif request.method == "POST":

            rating = request.form.get("rating")

            cmdSql = "INSERT INTO ratings ('rating_recipe_id', 'rating_author', 'rating') VALUES (:recipe_id, :author, :rating) ON CONFLICT DO UPDATE SET rating = :rating WHERE rating_recipe_id = :recipe_id AND rating_author = :author"
            c.execute(
                cmdSql,
                {
                    "recipe_id": recipe_id,
                    "author": session["user_id"],
                    "rating": rating,
                },
            )
            conn.commit()

            return redirect(url_for("recipe", recipe_id=recipe_id))
    else:
        return redirect(url_for("login"))


@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" in session:
        conn = log_database()
        c = conn.cursor()

        if request.method == "POST":
            # check if the form is valid

            recipe_name = request.form["recipe_name"]
            recipe_body = request.form["recipe_body"]

            if not recipe_name or not recipe_body:
                error_message = "Please fill out all fields."
                return render_template("add.html", error_message=error_message)

            # check if recipe exist in the database
            cmdSql = "SELECT * FROM recipes WHERE recipe_name=:recipe_name"
            exist = c.execute(
                cmdSql,
                {"recipe_name": recipe_name},
            ).fetchall()

            if len(exist) != 0:
                error_message = "This recipe already exists"
                return render_template("add.html", error_message=error_message)

            # get the username of connected user
            cmdSql = "SELECT user_username FROM users WHERE user_mail=:user_mail"
            username = c.execute(
                cmdSql,
                {"user_mail": session["user_id"]},
            ).fetchall()

            # insert the row
            cmdSql = "INSERT INTO recipes ('recipe_author', 'recipe_name', 'body') VALUES (:username, :title,:body)"
            c.execute(
                cmdSql,
                {
                    "username": username[0][0],
                    "title": recipe_name,
                    "body": recipe_body,
                },
            )
            conn.commit()

            newRecipId = c.execute(
                "SELECT MAX(recipe_id) FROM recipes WHERE 1",
            ).fetchall()

            newRecipId = newRecipId[0][0]

            ingreSelectId = []
            ingreSelectQt = []
            for i in request.form:
                if "check_" in i:
                    ingreSelectId.append(request.form.get(i))
                    cmdSql = "INSERT INTO recipe_ingre ('ingre_id', 'recipe_id', 'qt') VALUES (:ingre, :recipe,:qt)"
                    c.execute(
                        cmdSql,
                        {
                            "ingre": request.form.get(i),
                            "recipe": newRecipId,
                            "qt": request.form.get(i.replace("check_", "qt_")),
                        },
                    )

            conn.commit()

            return redirect("/")

        else:

            cmdSql = "SELECT * FROM ingredients WHERE 1"
            ingres = c.execute(cmdSql).fetchall()

            return render_template("add.html", error_message="", ingres=ingres)
    else:
        return render_template("login.html", error_message="")


if __name__ == "__main__":
    app.run(debug=True)
