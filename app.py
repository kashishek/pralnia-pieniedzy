from flask import Flask, render_template, url_for
import random

app = Flask(__name__)

@app.route('/')
def index():
        dik="L"
        rand1=random.randrange(0,9)
        rand2=random.randrange(0,9)
        rand3=random.randrange(0,9)
        if(rand1==rand2 and rand2==rand3):
                dik="W"
        gowno=rand1+rand2+rand3
        return render_template('sloty.html', rand1=rand1, rand2=rand2, rand3=rand3, gowno=gowno, dik=dik)

if __name__ == "__main__":
        app.run(debug=True)