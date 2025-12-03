import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort
##Some of these imports may be unecessary

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

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

# input: first name, last name, row, seat
# concatenate first + last name? 
# create eTicketNumber 
# create timestamp
@app.route('/reservations')
def reservations():
    name = "Alyssa"               # len < code_str
    # name = "FirstNameTest"        # len > code_str
    # name = "**********"           # len == code_str

    # TODO: revisit -- will both first and last name be used for the code?
    reservation_code = generate_reservation_code(name)
    print(f"\nreservation code: {reservation_code}\n")

    return render_template('reservations.html')

app.run()