from flask import Flask, render_template
import threading
import RPi.GPIO as GPIO
import serial
import sqlite3
import time

app = Flask(__name__)
app.debug = True

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/gps', methods=['GET'])
def get_coordinates():
    conn = sqlite3.connect('/var/www/lab_app/gps_app.db')  # change this to your database path
    curs = conn.cursor()
    curs.execute("SELECT * FROM coordinates")
    rows = curs.fetchall()
    conn.close()

    # Convert the data to a list of dictionaries for easy JSON conversion
    coordinates = [{"rDatetime": row[0], "sensorID": row[1], "latitude": row[2], "longitude": row[3]} for row in rows]

    return render_template('coordinates.html', coordinates=coordinates)

# @app.route('/live_location', methods=['GET'])
# def get_coordinates():
#     conn = sqlite3.connect('/var/www/lab_app/gps_app.db')  # change this to your database path
#     curs = conn.cursor()
#     curs.execute("SELECT * FROM coordinates ORDER BY rDatetime DESC LIMIT 1")
#     row = curs.fetchone()
#     conn.close()
# 
#     # Convert the data to a dictionary for easy JSON conversion
#     coordinate = {"rDatetime": row[0], "sensorID": row[1], "latitude": row[2], "longitude": row[3]}
# 
#     return render_template('live.html', coordinate=coordinate)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)