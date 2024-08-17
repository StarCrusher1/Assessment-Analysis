from flask import Flask, render_template, redirect, url_for, request
import hashlib
import sqlite3

app = Flask(__name__)
logged_in = False
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

@app.route('/')
def index():
    while logged_in == False:
        return redirect(url_for("login"))
    conn = sqlite3.connect('marks.db')
    cursor = conn.cursor()
    conn.close()
    return render_template("index.html")

@app.route('/login')
def login():
    # Obtains usernames and password to check
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()
    query = "SELECT username, passkey FROM LoginDetails"
    cursor.execute("query")
    login_details = cursor.fetchall()
    conn.close()
    # checks the details entered
    valid_login = False
    username = ""
    password = ""
    while not valid_login:
        username = request.form.get()
    return render_template("login.html")

@app.route('/reset_password')
def reset():
    return render_template("reset.html")


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
