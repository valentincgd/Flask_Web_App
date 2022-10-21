from flask import Flask, url_for, render_template, request, redirect, session
import sqlite3

conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
c = conn.cursor()

app = Flask(__name__)
app.config["SECRET_KEY"] = "H@McQfTjWnZr4u7x!A%D*G-KaNdRgUkX"

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # check if the form is valid

            if not request.form.get("email") or not request.form.get("password") or not request.form.get("username"):
                return "please fill out all fields"

            # check if email exist in the database
            exist = c.execute("SELECT * FROM users WHERE email=:email", {"email": request.form.get("email")}).fetchall()

            if len(exist) != 0:
                return "user already registered"

            # hash the password
            pwhash = request.form.get("password")

            # insert the row
            c.execute("INSERT INTO users (email, password) VALUES (:email, :password)", {"email": request.form.get("email"), "password": pwhash})
            conn.commit()

            # return success
            return "registered successfully!"
    else:
        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        # check the form is valid
        if not request.form.get("email") or not request.form.get("password"):
            return "please fill out all required fields"

        # check if email exist in the database
        user = c.execute("SELECT * FROM users WHERE email=:email", {"email": request.form.get("email")}).fetchall()

        if len(user) != 1:
            return "you didn't register"
        # check the password is same to password hash
        pwhash = user[0][1]
        if pwhash != request.form.get("password"):
            return "wrong password"

        # login the user using session
        session["user_id"] = user[0][0]

        # return success
        return redirect("/")

    else:
        return render_template("login.html")

@app.route('/')
def index():
    if 'user_id' in session:
        return f'Logged in as {session["user_id"]}'
    return redirect("/login")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__=='__main__':
    app.run(debug=True)