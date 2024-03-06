from flask import Flask , render_template, redirect , url_for, session, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re, hashlib

app = Flask(__name__)

app.secret_key= "masi"

#database connection details

app.config["MYSQL_HOST"]= "localhost"
app.config["MYSQL_USER"]= "root"
app.config["MYSQL_PASSWORD"] = "Madiba@1989"
app.config["MYSQL_DB"]= "LOGIN"

#initialising mySQL

mySql = MySQL(app)

#login route

@app.route('/')
@app.route('/login',methods=['GET','POST'])
def log_on():

   msg=""

   if request.method == "POST" and "username" in request.form and "password" in request.form:
      # get details from HTML form using post request
      username = request.form["username"]
      password = request.form["password"]


      #hash password prior to storing in DB
      hash = password + app.secret_key
      hash = hashlib.sha1(hash.encode())
      password = hash.hexdigest()

      #get details from my sql database
      cursor = mySql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute('SELECT * FROM form WHERE username = %s AND password = %s', (username, password,))

      account =cursor.fetchone()

      # If account exists in accounts table in out database

      if account:
         session['loggedin']= True
         session['id'] = account['id']
         session['username'] = account['username']
         
         return redirect(url_for('home'))
      else:

         msg= "Incorrect username/password!"
      


   return render_template("index.html",msg=msg)


@app.route("/login/logout")
def log_out():

   # Remove session data, this will log the user out
   session.pop('loggedin',None)
   session.pop('id',None)
   session.pop('username',None)

   return redirect(url_for('log_on'))


@app.route('/register', methods=["GET","POST"])
def register():
   msg= ""

   if request.method == "POST"  and "username" in request.form and "password" in request.form and "email" in request.form:
      username = request.form["username"]
      password = request.form["password"]
      email = request.form["email"]

      # Check if account exists using MySQL
      cursor = mySql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute("SELECT * FROM form WHERE username = %s",(username,))
      account = cursor.fetchone()

      # If account exists show error and validation checks
      if account:
         msg= "Account already exists"
      elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
         msg ="invalid email address"
      elif not re.match(r'[A-Za-z0-9]+', username):
         msg= 'Username must contain only characters and numbers!'
      elif not username or not password or not email:
         msg = "Please fill out form"
      else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()

            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            cursor.execute('INSERT INTO form VALUES (NULL, %s, %s, %s)', (username, password, email))
            mySql.connection.commit()
            msg = 'You have successfully registered!'


   elif request.method == "POST":
      msg = "Please complete form"



   return render_template('register.html', msg=msg)



@app.route('/login/home')
def home():

   # Check if the user is logged in
   if "loggedin" in session:

      return render_template('home.html',username=session["username"])
   
   return redirect(url_for(log_on))


@app.route('/login/profile')
def profile():
    # Check if the user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mySql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not logged in redirect to login page
    return redirect(url_for('login'))





if __name__ == "__main__":
    app.run(debug=True)