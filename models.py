from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def remove_microseconds():
    return datetime.now().replace(microsecond=0)

class Reservations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passengerName = db.Column(db.String(255), nullable=False)
    seatRow = db.Column(db.Integer, nullable=False)
    seatColumn = db.Column(db.Integer, nullable=False)
    eTicketNumber = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, default=remove_microseconds, nullable=False)

class Admins(db.Model):
    username = db.Column(db.Text, primary_key=True)
    password = db.Column(db.Text, nullable=False)