from flask import Flask, render_template, request, session, redirect, url_for
import json
import hashlib
#from flask import *
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from datetime import datetime
import random
import sqlite3
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'djtengaknaga'
socketio = SocketIO(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users (hasz TEXT, username TEXT, mail TEXT, score INTEGER, sloty TEXT)')
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
        
        hsh = hashlib.sha256(haslo.encode()).hexdigest()
        
        if sign_in!=False:
            #hsh = hash(haslo+mail)
            print(f"[<- sign in ->] {name} {mail} {haslo} [<->] {hsh}")
            if(czy_mail(mail)==True):
                return render_template("glow.html", error="ten mail juz jest zajęty", name=name)
            elif(czy_nu(name)==True):
                return render_template("glow.html", error="ten nazwa uzytkownika juz jest zajęty", mail=mail)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (hasz, username, mail, score, sloty) VALUES (?, ?, ?, ?, ?)",
               (hsh, name, mail, 20, "000",))
            conn.commit()
            conn.close()

        elif log_in!=False:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("select * FROM users WHERE hasz = ? AND username = ? AND mail = ?",
               (hsh, name, mail))
            result = cursor.fetchone()
            conn.commit()
            conn.close()
            if(not result):
                return render_template("glow.html", error="złe nazwa mail haslo")
            

        session["name"]=name
        session["key"]=hsh
        return redirect(url_for("gamba"))
    
    return render_template("glow.html")

@app.route("/gamba", methods=["POST", "GET"])
def gamba():
    key = session.get("key")
    logout = request.form.get("logout", False)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE hasz = ?',(key,))
    player_data = cursor.fetchone()
    if(not player_data):
        return redirect(url_for("home"))
    player_score = player_data[3]
    name = player_data[1]
    conn.close()


    if request.method == "POST":
        if logout!=False:
            print(f"logout {name}")
            return redirect(url_for("home"))
        

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages')
    tmes = cursor.fetchall()
    conn.close()
    return render_template("gamba.html", name=name, tmes=tmes, player_score=player_score)

@socketio.on("new-message")
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
    socketio.emit("message", content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on('connect')
def handle_connect():
    join_room(request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    leave_room(request.sid)

@socketio.on("gamba")
def nowa_gamba():
        conn = get_db_connection()
        cursor = conn.cursor()
        hsh = session.get("key")
        name = session.get("name")
        cursor.execute("SELECT score, sloty FROM users WHERE hasz = ?", (hsh,))
        row = cursor.fetchone()
        if row:
            score_db=row[0]
            gstr = row[1]
            if(score_db<=0):
                print(f"no credits {name}")
                return
        else:
            return
        
        print(f"spin name: {name} [<->credits<===>] {score_db}")
        cursor.execute("UPDATE users SET score = score - 1 WHERE hasz = ?", (hsh,))

        data = {
            "rng1": random.randrange(0,9),
            "rng2": random.randrange(0,9),
            "rng3": random.randrange(0,9),
            "score": score_db,
            "score_after": 69
        }

        it1 = int(gstr[0])
        it2 = int(gstr[1])
        it3 = int(gstr[2])
        it1=(it1 + data["rng1"]) % 9
        it2=(it2 + data["rng2"]) % 9
        it3=(it3 + data["rng3"]) % 9
        nowe_ustawienie = str(it1) + str(it2) + str(it3)
        print(f"gamba: {nowe_ustawienie}")
        cursor.execute("UPDATE users SET sloty = ?",(nowe_ustawienie,))

        if(it1==it2 and it2==it3):
            #jeśli komuś sie chce dla każdego rodzaju inny wynik to tutaj ify trzeba dać============================================
            data["score_after"] = score_db + 10
            cursor.execute("UPDATE users SET score = score + 11 WHERE hasz = ?", (hsh,))
            print(f"fat W [>>] {session.get("name")}")
        else:
            data["score_after"] = data["score"] - 1
        conn.commit()
        conn.close()
        emit("spin", data, room=request.sid)


if __name__=="__main__":
    socketio.run(app, debug=True)