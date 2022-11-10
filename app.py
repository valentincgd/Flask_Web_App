from flask import Flask, url_for, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3
from pathlib import Path

# coding: UTF-8

# Create and connect DB
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
        pw_hash = generate_password_hash(password)

        # insert the row
        sql_cmd = "INSERT INTO users (user_mail, user_password,user_username) VALUES (:email, :password,:username)"

        try:
            c.execute(
                sql_cmd,
                {
                    "email": email,
                    "password": pw_hash,
                    "username": username,
                },
            )
        except sqlite3.IntegrityError:
            return render_template(
                "signup.html", error_message="Username or email already exist."
            )

        conn.commit()

        # get user id for session
        sql_cmd = "SELECT * FROM users WHERE user_mail=:email"
        user_information = c.execute(
            sql_cmd,
            {"email": email},
        ).fetchone()

        # return success
        session["user_id"] = user_information[0]

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
        sql_cmd = "SELECT * FROM users WHERE user_mail=:email"
        user_information = c.execute(
            sql_cmd,
            {"email": email},
        ).fetchone()

        if not user_information:
            error_message = "You didn't register."
            return render_template("login.html", error_message=error_message)

        # check the password is same to password hash
        pw_hash = user_information[2]

        if check_password_hash(pw_hash, password) == False:
            error_message = "Wrong password."
            return render_template("login.html", error_message=error_message)

        # login the user using session

        session["user_id"] = user_information[0]

        # return success
        return redirect("/")

    else:
        return render_template("login.html", error_message="")


@app.route("/")
def index():
    if "user_id" in session:
        conn = log_database()
        c = conn.cursor()

        # Select all recipes and ratings
        recipes = c.execute(
            "SELECT *, users.user_username FROM recipes LEFT JOIN users ON users.user_id = recipes.recipe_author"
        ).fetchall()
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

            # Select recipes and associated ratings
            fetch_all_recipes = "SELECT re.recipe_id, us.user_username, re.recipe_name, re.body, ROUND(AVG(ra.rating)) FROM recipes re LEFT JOIN ratings ra ON re.recipe_id = ra.rating_recipe_id LEFT JOIN users us ON re.recipe_author = us.user_id WHERE re.recipe_id = :recipe_id"
            fetch_my_rating = "SELECT re.recipe_id, re.recipe_author, re.recipe_name, re.body, ra.rating FROM recipes re LEFT JOIN ratings ra ON re.recipe_id = ra.rating_recipe_id WHERE re.recipe_id = :recipe_id AND ra.rating_author = :rating_author"
            recipe = c.execute(fetch_all_recipes, {"recipe_id": recipe_id}).fetchall()
            my_rating = c.execute(
                fetch_my_rating,
                {"recipe_id": recipe_id, "rating_author": session["user_id"]},
            ).fetchall()

            # Select associated ingredients
            fetchAllIngredients = "SELECT ingredients.ingre_name, ingredients.ingre_img, recipe_ingre.qt FROM recipe_ingre INNER JOIN ingredients ON ingredients.ingre_id = recipe_ingre.ingre_id WHERE recipe_id = :recipe_id"
            ingre = c.execute(
                fetchAllIngredients,
                {"recipe_id": recipe_id},
            ).fetchall()

            return render_template(
                "recipe.html", recipes=recipe, ingres=ingre, my_rating=my_rating
            )

        elif request.method == "POST":

            rating = request.form.get("rating")

            # Insert or update rating
            cmd_sql = "INSERT INTO ratings ('rating_recipe_id', 'rating_author', 'rating') VALUES (:recipe_id, :author, :rating) ON CONFLICT DO UPDATE SET rating = :rating WHERE rating_recipe_id = :recipe_id AND rating_author = :author"
            c.execute(
                cmd_sql,
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
            cmd_sql = "SELECT * FROM recipes WHERE recipe_name=:recipe_name"
            exist = c.execute(
                cmd_sql,
                {"recipe_name": recipe_name},
            ).fetchall()

            if len(exist) != 0:
                error_message = "This recipe already exists"
                return render_template("add.html", error_message=error_message)

            # insert the row
            cmd_sql = "INSERT INTO recipes ('recipe_author', 'recipe_name', 'body') VALUES (:username, :title,:body)"
            c.execute(
                cmd_sql,
                {
                    "username": session["user_id"],
                    "title": recipe_name,
                    "body": recipe_body,
                },
            )
            conn.commit()

            # Select the last recipe id
            new_recip_id = c.execute(
                "SELECT MAX(recipe_id) FROM recipes WHERE 1",
            ).fetchall()

            new_recip_id = new_recip_id[0][0]

            # Insert all associated ingredients
            ingre_select_id = []
            ingre_select_qt = []
            for i in request.form:
                if "check_" in i:
                    ingre_select_id.append(request.form.get(i))
                    cmd_sql = "INSERT INTO recipe_ingre ('ingre_id', 'recipe_id', 'qt') VALUES (:ingre, :recipe,:qt)"
                    c.execute(
                        cmd_sql,
                        {
                            "ingre": request.form.get(i),
                            "recipe": new_recip_id,
                            "qt": request.form.get(i.replace("check_", "qt_")),
                        },
                    )

            conn.commit()

            return redirect("/")

        else:

            # Select all ingredients
            cmd_sql = "SELECT * FROM ingredients WHERE 1"
            ingres = c.execute(cmd_sql).fetchall()

            return render_template("add.html", error_message="", ingres=ingres)
    else:
        return render_template("login.html", error_message="")


if __name__ == "__main__":
    app.run(debug=True)
