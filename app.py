import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort
from models import db, Admins, Reservations
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

# set up SQLAlchemy
db_path = os.path.join(os.path.dirname(__file__), 'reservations.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db.init_app(app)

with app.app_context():
    db.create_all()

def get_reservations():
    return Reservations.query.all()

def get_admins():
    return Admins.query.all()

def get_chart():
    reservations = get_reservations()
    chart = [['O' for _ in range(4)] for _ in range(12)]
    for r in reservations:
        row_num = r.seatRow
        col_num = r.seatColumn
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
    reservation = Reservations.query.get(reservation_id)
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
        return True
    
    return False


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
            if admin.username == username and admin.password == password:
                chart = get_chart()
                sales = calculate_total_revenue(chart)
                reservations = get_reservations()
                logged_in = True
            
        if not logged_in:
            flash('Incorrect username or password.')

    return render_template('admin.html', chart=chart, sales=sales, reservations=reservations)

# verify seat availability - returns False if unavailable, otherwise returns True
def check_seat_availability(chart, row, seat):
    if chart[row][seat] == 'X':
        return False
    else:
        return True

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
    name = first_name + last_name
    eTicketNumber = generate_reservation_code(name)   # create eTicketNumber 

    # reformat name for database
    name = first_name + " " + last_name

    # create reservation
    new_reservation = Reservations(
        passengerName=name,
        seatRow=row,
        seatColumn=seat,
        eTicketNumber=eTicketNumber
    )

    # add reservation to database
    db.session.add(new_reservation)
    db.session.commit()


    # display reservation details in console
    print("-" *50)
    print(f"Success! The following reservation has been added:\n")
    print(f"Passenger name: {new_reservation.passengerName}")
    print(f"Row {new_reservation.seatRow}, Seat {new_reservation.seatColumn}")
    print(f"eTicketNumber: {new_reservation.eTicketNumber}")
    print("-" *50)

    return eTicketNumber

# collect form input: first name, last name, row, seat
@app.route('/reservations', methods=('GET', 'POST'))
def reservations():
    new_reservation_msg = None
    chart = get_chart()

    # Add a new reservation
    if request.method == 'POST' and 'first_name' in request.form:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        seat_row = int(request.form['seat_row'])
        seat_column = int(request.form['seat_column'])

        # check seat availability -- if available, proceed with the reservation
        seat_availability = check_seat_availability(chart, seat_row, seat_column)
        if seat_availability == False:
            flash(f"Error: the selected seat (Row {seat_row}, Seat {seat_column}) is not available. Please choose another seat and try again.")
        else: 
            reservation_code = add_reservation(first_name, last_name, seat_row, seat_column)
            new_reservation_msg = f"Congratulations {first_name}! Row {seat_row}, Seat {seat_column} is now reserved for you. Enjoy your trip! \nYour eTicket Number is {reservation_code}"
            chart = get_chart() # update seating chart

    # Delete a reservation
    if request.method == 'POST' and 'delete_reservation' in request.form:
        reservation_id = request.form['delete_reservation']
        delete_reservation(reservation_id)

    # Fetch all reservations to display on the page
    reservations_list = get_reservations()

    return render_template('reservations.html', reservations=reservations_list, new_reservation_msg=new_reservation_msg, chart=chart)

app.run()
