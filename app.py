#from flask import Flask
from flask import *
import sqlite3
 
app = Flask(__name__)

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create the messages table in the database
def create_table():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT)')
    conn.commit()
    conn.close()


# Route for the home page
@app.route('/')


def home():
    create_table()
    # Fetch all messages from the database
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages').fetchall()
    conn.close()
    return render_template('index.html', messages=messages)

# Route for submitting the form
@app.route('/submit', methods=['POST'])
def submit():
    # Get the text input from the form
    message = request.form['message']
    
    # Save the message to the database
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (message) VALUES (?)', (message,))
    conn.commit()
    conn.close()

    # Redirect back to the home page
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Create the SQLite database if it doesn't exist
    #conn = sqlite3.connect('database.db')
    #conn.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT)')
    #conn.close()


    create_table()
    # Run the app
    app.run(debug=True)