from flask import Flask, request, redirect, render_template
import sqlite3
import os

# Creates app
app = Flask(__name__)

# Connects app to the database
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    amount REAL,
                    category TEXT,
                    date TEXT
                )''')
    conn.commit()
    conn.close()
    print('connection loaded')


@app.route('/test')
def test():
    print("test route hit")
    return "Server is working!"

# Uses POST requests to send expense data
@app.route('/add', methods=['POST'])
def add_expense():
    # Get form data
    name = request.form['name']
    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']
    # Connect to DB, inserts into table
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (name, amount, category, date) VALUES (?, ?, ?, ?)",
          (name, amount, category, date))
    
    conn.commit()
    conn.close()
    print('form request and sending')
    return redirect('/')

# Returns data from HTML to homepage route
@app.route('/')
def index():
    print('indexed')
    return render_template('index.html')

# Runs app
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
    print('app running')