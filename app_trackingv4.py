from flask import Flask, request, render_template
import threading
import RPi.GPIO as GPIO
import serial
import sqlite3
import datetime
import time

app = Flask(__name__)
app.debug = True

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/gps', methods=['GET'])
def get_coordinates():
    from_date_str   = request.args.get('from',time.strftime("%Y-%m-%d %H:%M")) #Get the from date value from the URL
    to_date_str     = request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
    
    if not validate_date(from_date_str):			# Validate date before sending it to the DB
        from_date_str 	= time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str 	= time.strftime("%Y-%m-%d %H:%M")		# Validate date before sending it to the DB

    conn = sqlite3.connect('/var/www/lab_app/gps_app.db')  # change this to your database path
    curs = conn.cursor()
    curs.execute("SELECT * FROM coordinates WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    rows = curs.fetchall()
    conn.close()

    # Convert the data to a list of dictionaries for easy JSON conversion
    coordinates = [{"rDatetime": row[0], "sensorID": row[1], "latitude": row[2], "longitude": row[3]} for row in rows]

    return render_template('coordinates.html', coordinates=coordinates)

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
