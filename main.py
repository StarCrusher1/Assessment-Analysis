from flask import Flask, render_template, redirect, url_for, request, session
import hashlib
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def hash_password(password): # converts password to sha256
    password_bytes = password.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password_bytes)
    return sha256_hash.hexdigest()

def acceptable_password(password):
    digits = 0
    letters = 0
    special = 0
    if len(password) < 8:
        return False

    for i in range(len(password)):
        if password[i].isdigit():
            digits += 1
        elif password[i].isalpha():
            letters += 1
        else:
            special += 1

    if digits == 0 or letters == 0 or special == 0:
        return False
    else:
        return True

@app.route('/', methods=["GET","POST"])
def index():
    if not session.get('logged_in'):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route('/login', methods=["GET","POST"])
def login():
    # Obtains usernames and password to check
    sql_query = "SELECT username, passkey FROM LoginDetails"
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()
    cursor.execute(sql_query)
    login_details = cursor.fetchall()
    login_details = list(login_details)
    username_list = [detail[0] for detail in login_details]
    conn.close()
    # checks the details entered
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = hash_password(password)
        
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        check_query = cursor.execute("SELECT passkey FROM LoginDetails WHERE username=?", (username,))
        matching_password = cursor.fetchone()
        conn.close()
        
        if matching_password is None:
            print("Username does not exist")
            return render_template("login.html")
        stored_password = matching_password[0]
        if hashed_password != stored_password:
            print("Passwords do not match")
            return render_template("login.html")
        session['logged_in'] = True
        print(session)
        return redirect(url_for("index"))
        
    return render_template("login.html")

@app.route('/reset_password')
def reset():
    return render_template("reset.html")

@app.route('/change_password')
def change():
    return render_template("change.html")

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
