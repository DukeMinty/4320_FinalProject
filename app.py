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

def generate_reservation_code(name):
    code_str = "INFOTC4320"
    reservation_code = []

    # compare length of name and code_str
    nameGreater = len(name) > len(code_str)
    
    # for names less than or equal to the code_str length
    if not nameGreater:
        # split code_str at the given name's length
        code_str_subsection = code_str[0:(len(name))]
        code_str_leftover = code_str[(len(name)):]

        # iterate over name length
        for i in range(len(name)):
            reservation_code.append(name[i])
            reservation_code.append(code_str_subsection[i])

        # join characters in list and concatenate the leftover code_str characters
        reservation_code = "".join(reservation_code)
        reservation_code = reservation_code + code_str_leftover
    else:
        # split name at the code_str's length
        name_subsection = name[0:len(code_str)]
        name_leftover = name[len(code_str):]

        # iterate over code_str length
        for i in range(len(code_str)):
            reservation_code.append(name_subsection[i])
            reservation_code.append(code_str[i])

        # join characters in list and concatenate the leftover name characters
        reservation_code = "".join(reservation_code)
        reservation_code = reservation_code + name_leftover  

    return reservation_code

# add a new reservation to the database
def add_reservation(first_name, last_name, row, seat):
    # TODO: revisit -- will both first and last name be used for the code?
    name = first_name + last_name
    eTicketNumber = generate_reservation_code(name)   # create eTicketNumber 

    # reformat name for database
    name = first_name + " " + last_name

    conn = get_db_connection()
    # TODO: add error handling
    conn.execute(
        'INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)',
        (name, row, seat, eTicketNumber)
    )
    conn.commit()

    # retrieve reservation from the database
    new_reservation = conn.execute('SELECT * FROM reservations WHERE seatRow = ? AND seatColumn = ?', (row, seat)).fetchall()

    # display reservation details
    print("-" *50)
    print(f"Success! The following reservation has been added:\n")
    for col in new_reservation:
        print(f"Passenger name: {col['passengerName']}")
        print(f"Row: {col['seatRow']}")
        print(f"Seat: {col['seatColumn']}")
        print(f"eTicketNumber: {col['eTicketNumber']}")
        print(f"Created: {col['created']}")
    print("-" *50)

    conn.close()
    return

# collect form input: first name, last name, row, seat
@app.route('/reservations', methods=('GET', 'POST'))
def reservations():
    conn = get_db_connection()

    # Add a new reservation
    if request.method == 'POST' and 'first_name' in request.form:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        seat_row = int(request.form['seat_row'])
        seat_column = int(request.form['seat_column'])

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
