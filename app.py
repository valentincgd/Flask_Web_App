from flask import Flask, url_for, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3
from pathlib import Path

# coding: UTF-8


def init_db():
    db = sqlite3.connect("MarmiFlask.db")
    db.row_factory = sqlite3.Row
    db.executescript(Path("MarmiFlask.sql").read_text(encoding="utf-8"))


if not Path("MarmiFlask.db").exists():
    init_db()


conn = sqlite3.connect("MarmiFlask.db", check_same_thread=False)
c = conn.cursor()

app = Flask(__name__)

app.config[
    "SECRET_KEY"
] = "9af5477e9770cc80f836ba957033432486844f49e24a62c79f2df6cca073a27a"


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        # check if the form is valid
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")

        formInformationIsNotComplet = not email or not password or not username

        if formInformationIsNotComplet:
            errorMessage = "Please fill out all fields."
            return render_template("signup.html", errorMessage=errorMessage)

        # check if email exist in the database
        sqlCmd = "SELECT * FROM users WHERE user_mail=:email"
        exist = c.execute(sqlCmd, {"email": email}).fetchall()

        if len(exist) != 0:
            errorMessage = "Email already registered."
            return render_template("signup.html", errorMessage=errorMessage)

        # hash the password
        pwhash = generate_password_hash(request.form.get("password"))

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
                "signup.html", errorMessage="Username already exist."
            )

        conn.commit()

        # return success
        session["user_id"] = email

        return redirect("/")
    else:
        return render_template("signup.html", errorMessage="")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # check the form is valid
        if not email or not password:
            errorMessage = "Please fill out all required fields."
            return render_template("login.html", errorMessage=errorMessage)

        # check if email exist in the database
        sqlCmd = "SELECT * FROM users WHERE user_mail=:email"
        userInformation = c.execute(
            sqlCmd,
            {"email": email},
        ).fetchall()

        if len(userInformation) != 1:
            errorMessage = "You didn't register."
            return render_template("login.html", errorMessage=errorMessage)

        # check the password is same to password hash
        pwhash = userInformation[0][2]
        if check_password_hash(pwhash, password) == False:
            errorMessage = "Wrong password."
            return render_template("login.html", errorMessage=errorMessage)

        # login the user using session

        session["user_id"] = email

        # return success
        return redirect("/")

    else:
        return render_template("login.html", errorMessage="")


@app.route("/")
def index():
    if "user_id" in session:
        recipes = c.execute("SELECT * FROM recipes").fetchall()
        return render_template("index.html", recipes=recipes)
    return redirect("/login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    if "user_id" in session:

        fetchAllRecipes = "SELECT * FROM recipes WHERE recipe_id = :recipe_id"
        recipe = c.execute(fetchAllRecipes, {"recipe_id": recipe_id}).fetchall()

        fetchAllIngredients = "SELECT ingredients.ingre_name, ingredients.ingre_img, recipe_ingre.qt FROM recipe_ingre INNER JOIN ingredients ON ingredients.ingre_id = recipe_ingre.ingre_id WHERE recipe_id = :recipe_id"
        ingre = c.execute(
            fetchAllIngredients,
            {"recipe_id": recipe_id},
        ).fetchall()
        return render_template("recipe.html", recipes=recipe, ingres=ingre)
    else:
        return render_template("login.html", errorMessage="")


@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" in session:

        if request.method == "POST":
            # check if the form is valid

            recipe_name = request.form.get("recipe_name")
            recipe_body = request.form.get("recipe_body")

            if not recipe_name or not recipe_body:
                errorMessage = "Please fill out all fields."
                return render_template("add.html", errorMessage=errorMessage)

            # check if recipe exist in the database
            cmdSql = "SELECT * FROM recipes WHERE recipe_name=:recipe_name"
            exist = c.execute(
                cmdSql,
                {"recipe_name": recipe_name},
            ).fetchall()

            if len(exist) != 0:
                errorMessage = "This recipe already exists"
                return render_template("add.html", errorMessage=errorMessage)

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

                if "qt_" in i and i.replace("qt_", "") in ingreSelectId:
                    ingreSelectQt.append(request.form.get(i))

            increment = 0
            for i in ingreSelectId:
                cmdSql = "INSERT INTO recipe_ingre ('ingre_id', 'recipe_id', 'qt') VALUES (:ingre, :recipe,:qt)"
                c.execute(
                    cmdSql,
                    {
                        "ingre": ingreSelectId[increment],
                        "recipe": newRecipId,
                        "qt": ingreSelectQt[increment],
                    },
                )
                conn.commit()

                increment += 1


            return redirect("/")

        else:

            cmdSql = "SELECT * FROM ingredients WHERE 1"
            ingres = c.execute(cmdSql).fetchall()

            return render_template("add.html", errorMessage="", ingres=ingres)
    else:
        return render_template("login.html", errorMessage="")


if __name__ == "__main__":
    app.run(debug=True)
