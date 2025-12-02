import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort
import chart
##Some of these imports may be unecessary

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

def get_db_connection(): 
    conn = sqlite3.connect('reservations.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_chart():
    return chart.make_chart()

def get_admins():
    conn = get_db_connection()
    admins = conn.execute('SELECT * FROM admins').fetchall()
    conn.close()
    return admins

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/admin', methods=('GET', 'POST'))
def admin():

    chart = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if admin is None:
            flash('Invalid credentials. Please try again.')
        else:
            chart = get_chart()

    return render_template('admin.html', chart=chart)

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

app.run()