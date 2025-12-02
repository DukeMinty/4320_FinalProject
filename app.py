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

def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

def calculate_total_revenue(chart):
    cost_matrix = get_cost_matrix()
    total_cost = 0
    for i in range(12):
        for j in range(4):
            if chart[i][j] == 'X':
                total_cost += cost_matrix[i][j]
    return total_cost

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
    sales = None

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
            sales = calculate_total_revenue(chart)

    return render_template('admin.html', chart=chart, sales=sales)

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

app.run()