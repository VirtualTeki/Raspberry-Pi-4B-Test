from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import serial
import sqlite3
import datetime
import time

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/gps', methods=['GET'])
def get_coordinates():
    coordinates, from_date_str, to_date_str = fetch_coordinates()
    return render_template('coordinates.html', coordinates=coordinates, from_date=from_date_str, to_date=to_date_str)

def fetch_coordinates():
    from_date_str = request.args.get('from', time.strftime("%Y-%m-%d 00:00"))
    to_date_str = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))
    range_h_form = request.args.get('range_h', '')

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
    return coordinates, from_date_str, to_date_str

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

def fetch_latest_coordinates():
    conn = sqlite3.connect('/var/www/lab_app/gps_app.db')
    curs = conn.cursor()
    curs.execute("SELECT latitude, longitude FROM coordinates ORDER BY rDatetime DESC LIMIT 1")
    latest_coordinate = curs.fetchone()
    conn.close()
    return latest_coordinate

@socketio.on('connect')
def handle_connect():
    latest_coordinate = fetch_latest_coordinates()
    if latest_coordinate:
        emit('new_coordinate', {"latitude": latest_coordinate[0], "longitude": latest_coordinate[1]})

@socketio.on('request_latest_coordinates')
def handle_request_latest_coordinates():
    latest_coordinate = fetch_latest_coordinates()
    if latest_coordinate:
        emit('new_coordinate', {"latitude": latest_coordinate[0], "longitude": latest_coordinate[1]})

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        cleanup()
