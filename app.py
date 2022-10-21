from flask import Flask, url_for, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3
from pathlib import Path


def init_db():
    db = sqlite3.connect("MarmiFlask.db")
    db.row_factory = sqlite3.Row
    db.executescript(Path("MarmiFlask.sql").read_text())


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

        if (
            not request.form.get("email")
            or not request.form.get("password")
            or not request.form.get("username")
        ):
            return render_template(
                "signup.html", errorMessage="Please fill out all fields."
            )

        # check if email exist in the database
        exist = c.execute(
            "SELECT * FROM users WHERE user_mail=:email",
            {"email": request.form.get("email")},
        ).fetchall()

        if len(exist) != 0:
            return render_template(
                "signup.html", errorMessage="Email already registered."
            )

        # hash the password
        pwhash = request.form.get("password")
        # generate_password_hash(request.form.get("password"))

        # insert the row
        c.execute(
            "INSERT INTO users (user_mail, user_password,user_username) VALUES (:email, :password,:username)",
            {
                "email": request.form.get("email"),
                "password": pwhash,
                "username": request.form.get("username"),
            },
        )
        conn.commit()

        # return success
        session["user_id"] = request.form.get("email")

        return redirect("/")
    else:
        return render_template("signup.html", errorMessage="")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        # check the form is valid
        if not request.form.get("email") or not request.form.get("password"):
            return render_template(
                "login.html", errorMessage="Please fill out all required fields."
            )

        # check if email exist in the database
        user = c.execute(
            "SELECT * FROM users WHERE user_mail=:email",
            {"email": request.form.get("email")},
        ).fetchall()

        if len(user) != 1:
            return render_template("login.html", errorMessage="You didn't register.")

        # check the password is same to password hash
        pwhash = user[0][1]
        #        if check_password_hash(pwhash, request.form.get("password")) == False:

        if pwhash != request.form.get("password"):
            return render_template("login.html", errorMessage="Wrong password.")

        # login the user using session
        session["user_id"] = user[0][0]

        # return success
        return redirect("/")

    else:
        return render_template("login.html", errorMessage="")


@app.route("/")
def index():
    if "user_id" in session:
        return render_template("index.html", errorMessage="")
    return redirect("/login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
