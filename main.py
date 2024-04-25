from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)



rooms={}
def generate_code(dlugosc):
    while True:
        code=""
        for _ in range(dlugosc):
            code+=random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code

@app.route('/', methods=["POST", "GET"])
#@app.route('/')
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="niema imienia napisz imie ok?", code=code, name=name)
        
        if join!=False and not code:
            return render_template("home.html", error="niema code napisz room_code ok?", code=code, name=name)

        room = code
        if create!=False:
            room = generate_code(4)
            rooms[room] = {"members":0, "messeges": []}
        elif code not in rooms:
            return render_template("home.html", error="zły kodzik do pokoju?", code=code, name=name)

        session["room"]=room
        session["name"]=name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    return render_template("room.html")

if __name__=="__main__":
    socketio.run(app, debug=True)