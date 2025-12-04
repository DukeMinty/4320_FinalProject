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

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')


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

# form input: first name, last name, row, seat
@app.route('/reservations')
def reservations():
    # TODO: add logic to check for valid reservations
    # ex. is there an existing reservation with the given row/seat combo?

    # TODO: replace placeholder data with form input once form is ready
    add_reservation("Bill", "Nye", 6, 2)

    return render_template('reservations.html')

app.run()