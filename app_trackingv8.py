from flask import Flask, request, render_template
import datetime
import sqlite3
import time
import math

app = Flask(__name__)
app.debug = True

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/gps', methods=['GET'])
def get_coordinates():
    coordinates, from_date_str, to_date_str, total, page, total_pages = fetch_coordinates()
    return render_template('coordinates.html', coordinates=coordinates, from_date=from_date_str, to_date=to_date_str, total_pages=total_pages, page=page)

def fetch_coordinates():
    from_date_str = request.args.get('from', time.strftime("%Y-%m-%d 00:00"))
    to_date_str = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))
    range_h_form = request.args.get('range_h', '')  # This will return a string, if field range_h exists in the request

    range_h_int = "nan"

    try:
        range_h_int = int(range_h_form)
    except:
        print("range_h_form not a number")

    if not validate_date(from_date_str):
        from_date_str = time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str = time.strftime("%Y-%m-%d %H:%M")

    if isinstance(range_h_int, int):
        time_now = datetime.datetime.now()
        time_from = time_now - datetime.timedelta(hours=range_h_int)
        time_to = time_now
        from_date_str = time_from.strftime("%Y-%m-%d %H:%M")
        to_date_str = time_to.strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect('/var/www/lab_app/gps_app.db')  # change this to your database path
    curs = conn.cursor()
    curs.execute("SELECT * FROM coordinates WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    rows = curs.fetchall()
    conn.close()

    coordinates = [{"rDatetime": row[0], "sensorID": row[1], "latitude": row[2], "longitude": row[3]} for row in rows]
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total = len(coordinates)
    total_pages = math.ceil(total / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    coordinates_paginated = coordinates[start:end]

    return coordinates_paginated, from_date_str, to_date_str, total, page, total_pages

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
