from flask import Flask , redirect , render_template



app=Flask(__name__)


@app.route('/',methods=['GET'])
def get_home():
    return render_template('home.html')


@app.route('/login',methods=['GET'])
def get_login():
    return render_template('login.html')


@app.route('/signup',methods=['GET'])
def get_signup():
    return render_template('signup.html')

@app.route('/login',methods=['POST'])
def login_post():
    return redirect('/')

@app.route('/signup',methods=['POST'])
def signup_post():
    return redirect('/')

@app.route('/logout',methods=['GET'])
def logout():
    return redirect('/login')



if __name__=='__main__':
    app.run(debug=True)