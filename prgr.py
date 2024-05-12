from flask import Flask, render_template, request, session, redirect, url_for
#from flask import *
from flask_socketio import SocketIO, join_room, leave_room, send
from datetime import datetime
import random
import sqlite3
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = get_db_connection()
    #conn.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS users (hasz INTEGER PRIMARY KEY, username TEXT NOT NULL, mail TEXT NOT NULL, score INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS messages (username TEXT, message TEXT, time TEXT)')
    conn.commit()
    conn.close()

def drop_db():
    conn = get_db_connection()
    conn.execute('DROP TABLE messages')
    conn.execute('DROP TABLE users')
    conn.commit()
    conn.close()

create_db()
drop_db()
create_db()


def czy_mail(mail):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?",
        (mail,))
    row = cursor.fetchone()
    conn.close()
    print(f"czy mail: {row}")
    if row:
        return(True)
    else:
        return(False)
    
def czy_nu(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?",
        (name,))
    row = cursor.fetchone()
    conn.close()
    print(f"czy name: {row}")
    if row:
        return(True)
    else:
        return(False)


@app.route('/', methods=["POST", "GET"])
def home():
    #if 'name' in session and 'mail' in session:
    #    return render_template('glow.htm', name=session['name'], mail=session['mail'])
    #else:
    #    return render_template("glow.html")

    if request.method == "POST":
        name = request.form.get("name")
        haslo = request.form.get("haslo")
        mail = request.form.get("mail")
        sign_in = request.form.get("sign_in", False)
        log_in = request.form.get("log_in", False)


        if not name:
            return render_template("glow.html", error="niema imienia napisz imie ok?", name=name, mail=mail)
        if not haslo:
            return render_template("glow.html", error="niema hasło napisz hasło ok?", name=name, mail=mail)
        if not mail:
            return render_template("glow.html", error="niema maila napisz dik ok?", name=name)
        
        
        if sign_in!=False:
            hsh = hash(haslo+mail)
            print(f"[<- sign in ->] {name} {mail} {haslo} [<->] {hsh}")
            if(czy_mail(mail)==True):
                return render_template("glow.html", error="ten mail juz jest zajęty", name=name)
            elif(czy_nu(name)==True):
                return render_template("glow.html", error="ten nazwa uzytkownika juz jest zajęty", mail=mail)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (hasz, username, mail, score) VALUES (?, ?, ?, ?)",
               (hsh, name, mail, 100))
            conn.commit()
            conn.close()
            #return render_template("gamba.html", name=name, hsh=hsh)

        elif log_in!=False:
            hsh = hash(haslo+mail)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("select * FROM users WHERE hasz = ? AND username = ? AND mail = ?",
               (hsh, name, mail))
            result = cursor.fetchone()
            conn.commit()
            conn.close()
            if(not result):
                return render_template("glow.html", error="złe nazwa mail haslo")
            

        session["mail"]=mail
        session["name"]=name
        return redirect(url_for("gamba"))

    return render_template("glow.html")

@app.route("/gamba", methods=["POST", "GET"])
def gamba():
    logout = request.form.get("logout", False)
    name = session.get("name")

    if request.method == "POST":
        if logout!=False:
            return redirect(url_for("home"))


    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages')
    tmes = cursor.fetchall()
    conn.close()
    return render_template("gamba.html", name=name, tmes=tmes)

@socketio.on("message")
def message(data):
    current_time = datetime.now()
    mes_time = current_time.strftime("%H:%M")

    content = {
        "name": session.get("name"),
        "message": data["data"],
        "time": mes_time
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, message, time) VALUES (?, ?, ?)",
        (session.get("name"), data["data"], mes_time))
    conn.commit()
    conn.close()

    send(content)
    print(f"{session.get('name')} said: {data['data']}")

if __name__=="__main__":
    socketio.run(app, debug=True)