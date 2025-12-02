import sqlite3

def get_db_connection(): 
    conn = sqlite3.connect('reservations.db')
    conn.row_factory = sqlite3.Row
    return conn

def make_chart():
    
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()

    chart = [['O' for _ in range(4)] for _ in range(12)]

    for id in reservations:
        row_num = id['seatRow']
        col_num = id['seatColumn']
        chart[row_num][col_num] = 'X'

    return chart