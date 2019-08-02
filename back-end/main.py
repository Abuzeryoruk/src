from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from flask import session

app = Flask(__name__, template_folder='./templates')


app.config['SECRET_KEY'] = 'aber_flask'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'deneme'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['default_authentication_plugin'] = 'sha2_password'

mysql = MySQL(app)


def protected(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if session['logged_in']:
            return f(*args, **kwargs)
        else:
            return redirect('/login')
    return decorator


@app.route('/')
@protected
def home():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Persons;')
    persons = list(cur.fetchall())
    print('persons= ', persons)

    return render_template('home.html', **locals())


@app.route('/addUser', methods=['GET', 'POST'])
@protected
def addUser():
    if (request.method == 'POST'):
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        age = request.form['age']
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO Persons (LastName, FirstName, Age) 
                            VALUES ('{}','{}',{})""".format(last_name, first_name, int(age)))
        mysql.connection.commit()
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/deleteUser', methods=['POST'])
def deleteUser():
    Personid = request.form['personId']
    print(Personid)
    cur = mysql.connection.cursor()

    cur.execute('DELETE FROM Persons WHERE Personid={}'.format(Personid))
    mysql.connection.commit()
    cur.close()
    return "success"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_canditate = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username='{}'".format(username))
        user = cur.fetchone()
        if user is not None:  # if users exist
            # password != user['password']:
            if sha256_crypt.verify(password_canditate, user['password']):
                message = "User/Password not found."
                return render_template('login.html', message=message)
            else:
                session['logged_in'] = True
                session['username'] = username
                return redirect('/')
        else:  # if user not exist
            message = "User not found."
            return render_template('login.html', message=message)
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        re_entered_password = request.form['re_entered_password']

        crypt_password = sha256_crypt.encrypt(str(password))

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT username FROM users WHERE username='{}'".format(username))
        user_exist = cur.fetchone()
        if not user_exist:
            if (password != re_entered_password):
                message = 'Passwords not matched!!'
                return render_template('register.html', message=message)
            else:
                cur.execute("INSERT INTO users (username, password) VALUES ('{}', '{}')".format(
                    username, crypt_password))
                mysql.connection.commit()
                cur.close()
                message = "Successfully Registered"
                return redirect('/login')
        else:
            message = "User Already exist"
            return render_template('register.html', message=message)
    return render_template('register.html')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['username'] = ""
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)