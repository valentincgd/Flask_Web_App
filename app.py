from flask import Flask, render_template_string,render_template, request, session, redirect, url_for



app=Flask(__name__)



app.secret_key = 'JaNdRgUkXp2s5v8y/B?E(H+MbPeShVmY'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"



@app.route('/',methods=['GET'])
def get_home():
    return render_template('home.html')


@app.route('/login',methods=['GET','POST'])
def get_login():
    if request.method == 'GET':
        print(session['Session'])
        return render_template('login.html')
    if request.method == 'POST':
            return redirect('/')



@app.route('/signup',methods=['GET','POST'])
def get_signup():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']        
        
        
        
        
        
        
        
        
        session['Session'] = username

        
        #ADD DANS LA BDD

        return redirect('/')



@app.route('/logout',methods=['GET'])
def logout():
    return redirect('/login')



if __name__=='__main__':
    app.run(debug=True)