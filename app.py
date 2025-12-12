import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort
##Some of these imports may be unecessary

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

def get_db_connection(): 
    conn = sqlite3.connect('reservations.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_reservations():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()
    return reservations

def get_admins():
    conn = get_db_connection()
    admins = conn.execute('SELECT * FROM admins').fetchall()
    conn.close()
    return admins

def get_chart():
    reservations = get_reservations()
    chart = [['O' for _ in range(4)] for _ in range(12)]
    for id in reservations:
        row_num = id['seatRow']
        col_num = id['seatColumn']
        chart[row_num][col_num] = 'X'
    return chart

def calculate_total_revenue(chart):
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    total_cost = 0
    for i in range(12):
        for j in range(4):
            if chart[i][j] == 'X':
                total_cost += cost_matrix[i][j]
    return total_cost

def delete_reservation(reservation_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
    conn.commit()
    conn.close()

#main menu page
@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        choice = request.form.get('choice')

        if not choice:
            flash("Please select an option.")
        elif choice == 'admin':
            return redirect(url_for('admin'))
        elif choice == 'reserve':
            return redirect(url_for('reservations'))
        else:
            flash("Invalid selection.")
    return render_template('index.html')

@app.route('/admin', methods=('GET', 'POST'))
def admin():

    chart = None
    sales = None
    reservations = None
    logged_in = False

    #delete reservation
    if request.method == 'POST' and 'delete_reservation' in request.form:
        reservation_id = request.form['delete_reservation']
        delete_reservation(reservation_id)
        flash(f'The reservation has been deleted.')

    #login admin
    if request.method == 'POST' and 'login' in request.form:
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

@app.route('/reservations', methods=('GET', 'POST'))
def reservations():
    conn = get_db_connection()

    # Add a new reservation
    if request.method == 'POST' and 'first_name' in request.form:
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        seat_row = request.form['seat_row']
        seat_column = request.form['seat_column']

        # Validate missing fields
        if not first_name or not last_name or not seat_row or not seat_column:
            flash('Please fill out all fields.')
            reservations_list = get_reservations()
            return render_template('reservations.html', reservations=reservations_list)

        seat_row = int(seat_row)
        seat_column = int(seat_column)

        # Check if the seat is already taken
        existing = conn.execute(
            'SELECT * FROM reservations WHERE seatRow = ? AND seatColumn = ?',
            (seat_row, seat_column)
        ).fetchone()

        if existing:
            flash('That seat is already taken. Please choose a different one.')
            reservations_list = get_reservations()
            return render_template('reservations.html', reservations=reservations_list)

        # Insert the reservation if everything is valid
        conn.execute(
            'INSERT INTO reservations (firstName, lastName, seatRow, seatColumn) VALUES (?, ?, ?, ?)',
            (first_name, last_name, seat_row, seat_column)
        )
        conn.commit()
        flash('Reservation successfully created!')

    # Delete a reservation
    if request.method == 'POST' and 'delete_reservation' in request.form:
        reservation_id = request.form['delete_reservation']
        delete_reservation(reservation_id)

    # Fetch all reservations to display on the page
    reservations_list = get_reservations()

    return render_template('reservations.html', reservations=reservations_list)



app.run()
