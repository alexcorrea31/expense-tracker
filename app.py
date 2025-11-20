from flask import Flask, request, redirect, render_template, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2
import os
from psycopg2.extras import RealDictCursor
from psycopg2 import IntegrityError

# Creates app
app = Flask(__name__)
app.secret_key = "key"

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# PostgreSQL connection helper
def get_connection():
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)

# Loading users from Database
@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'])
    return None

# Class to represent logged in users
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

#Routes user to home
@app.route('/home')
def home():
    return render_template('home.html')
        
# Register, Login, and Logout routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except IntegrityError:
            conn.rollback()
            flash('Username already exists.')
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            user_obj = User(id=user['id'], username=user['username'], password=user['password'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Connects app to the database + makes tables
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            name TEXT,
            amount REAL,
            category TEXT,
            date TEXT,
            user_id INTEGER REFERENCES users(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ PostgreSQL tables ensured in Neon.")



@app.route('/test')
def test():
    print("test route hit")
    return "Server is working!"

# Uses POST requests to send expense data
@app.route('/add', methods=['POST'])
@login_required
def add_expense():
    # Get form data
    name = request.form['name']
    amount = float(request.form['amount'])
    category = request.form['category']
    date = request.form['date']
    # Connect to DB, inserts into table
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (name, amount, category, date, user_id) VALUES (%s, %s, %s, %s, %s)",
               (name, amount, category, date, current_user.id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')

#redirects unlogged users to home
@app.route('/')
def root():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('home'))

# Returns data from HTML to homepage route
@app.route('/dashboard')
@login_required
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (current_user.id,))
    expenses = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', expenses=expenses)

# Runs app
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)
    print('app running')