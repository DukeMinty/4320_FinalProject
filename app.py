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

def calculate_total_revenue(chart):
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    
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

def get_reservations():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()
    return reservations

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/admin', methods=('GET', 'POST'))
def admin():

    chart = None
    sales = None
    reservations = None
    logged_in = False

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admins = get_admins()
        for admin in admins:
            if admin['username'] == username and admin['password'] == password:
                chart = get_chart()
                sales = calculate_total_revenue(chart)
                reservations = get_reservations()
                logged_in = True
            
        if not logged_in:
            flash('Incorrect username or password.')

    return render_template('admin.html', chart=chart, sales=sales, reservations=reservations)

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

app.run()