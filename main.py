from flask import Flask, render_template, redirect, url_for, request, session
import hashlib
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_subtable_info(db_path, username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Qn%'")
    tables = cursor.fetchall()

    qn_tables = [table[0] for table in tables]

    results = []

    for table in qn_tables:
        # Query each table for the given username
        query = f"SELECT * FROM {table} WHERE username = ?"
        cursor.execute(query, (username,))
        row = cursor.fetchall()
        results.extend(row)

    conn.close()
    print(f"Username: {username},results: {results}")
    return results

def hash_password(password): # converts password to sha256
    password_bytes = password.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password_bytes)
    return sha256_hash.hexdigest()

def get_login_count(username):
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()
    cursor.execute("SELECT logins FROM LoginDetails WHERE username=?", (username,))
    login_count = cursor.fetchone()
    conn.close()
    if login_count:
        return login_count[0]
    return None

def update_login_count(db_path, username):
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()
    cursor.execute("SELECT logins FROM LoginDetails WHERE username=?", (username,))
    login_count = cursor.fetchone()
    new_login_count = int(login_count[0]) + 1
    cursor.execute("UPDATE LoginDetails SET logins=? WHERE username=?", (new_login_count, username))
    conn.commit()
    conn.close()
    return None

@app.route('/', methods=["GET","POST"])
def index():
    if not session.get('logged_in'):
        return redirect(url_for("login"))
    marks_lost = {}
    careless = 0
    unattempted = 0
    total = 0
    maximum_total = 0
    indiv_qn_marks = []
    username = session.get('username')
    results = get_subtable_info("school.db", username)
    for result in results:
        topic = result[1]
        details = result[2:]
        qn_mark = []
        for i in range(0, len(details) ,3):
            maximum = details[i]
            scored = details[i+1]
            comment = details[i+2]
            maximum_total += maximum
            total += scored
            qn_mark.append(scored)
            if comment != None:
                if comment == "careless":
                    careless += (maximum - scored)
                else:
                    unattempted += maximum
            else:
                if scored < maximum:
                    if topic not in marks_lost.keys():
                        marks_lost[topic] = (maximum - scored)
                    else:
                        marks_lost[topic] += (maximum - scored)
        indiv_qn_marks.append(qn_mark)
    indiv_qn_scores = [sum(mark) for mark in indiv_qn_marks]
    marks_lost = dict(list(sorted(marks_lost.items(), key=lambda item: item[1], reverse=True)))
    if len(marks_lost) > 5:
        marks_lost = marks_lost[:5]
    return render_template("index.html",marks_lost=marks_lost,careless=careless,unattempted=unattempted,total=total,maximum_total=maximum_total,indiv_qn_marks=indiv_qn_marks,indiv_qn_scores=indiv_qn_scores)

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = hash_password(password)
        if any(x is None for x in [username, password]):
            print("Missing password or username")
            return render_template("login.html")
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        check_query = cursor.execute("SELECT passkey FROM LoginDetails WHERE username=?", (username,))
        matching_password = cursor.fetchone()
        conn.close()

        if matching_password is None:
            return render_template("login.html")
        stored_password = matching_password[0]
        if hashed_password != stored_password:
            return render_template("login.html")
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route('/reset_password', methods=["GET","POST"])
def reset():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password1")
        confirm_password = request.form.get("password2")
        if any(x is None for x in [username, password, confirm_password]):
            print("Missing password or username")
            return render_template("reset.html")
        if password != confirm_password:
            return render_template("reset.html")
        hashed_password = hash_password(password)
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE LoginDetails SET passkey=? WHERE username=?", 
                   (hashed_password, username))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))
    return render_template("reset.html")

@app.route("/logout", methods=["GET","POST"])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5012, debug=True)

