from flask import Flask, request, render_template
import time
import datetime
#import sys
import board
import adafruit_dht
import sqlite3
import serial

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio = False)

app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging

ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

power_key = 6
rec_buff = ''
time_count = 0

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/live_tracking")
def get_gps_data(command,back,timeout):
    command = 'AT+CGPSINFO'
    back = '+CGPSINFO: '
    timeout = 1
    rec_buff = ''
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01)
        rec_buff = ser.read(ser.inWaiting())
    if rec_buff != '':
        if back not in rec_buff.decode():
            print(command + ' Error')
            print(command + ' back:\t' + rec_buff.decode())
            return 0
        else:
            global GPSDATA
            
            GPSDATA = str(rec_buff.decode())
            start_index = GPSDATA.find(':') + 2
            Cleaned = GPSDATA[start_index:]
            #print(rec_buff.decode())
            Lat = Cleaned[:2]
            SmallLat = Cleaned[2:11]
            NorthOrSouth = Cleaned[12]
            #print(Lat, SmallLat, NorthOrSouth)
            #print(isinstance(Lat, str))
            
            Long = Cleaned[14:17]
            SmallLong = ''.join(filter(lambda x: x.isdigit() or x == '.', Cleaned[17:26]))
            EastOrWest = Cleaned[27]
            #print(Long, SmallLong, EastOrWest)
            
            FinalLong = float(Long) + (float(SmallLong)/60)
            FinalLat = float(Lat) + (float(SmallLat)/60)
            if EastOrWest == 'W': FinalLong = -FinalLong
            if NorthOrSouth == 'S': FinalLat = -FinalLat
	    
            return 1
    else:
        print('GPS is not ready')
        return 0

@app.route("/lab_temp")
def lab_temp():
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        return render_template("lab_temp.html",temp=temperature_c,hum=humidity)
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        return render_template("no_sensor.html")
    except Exception as error:
        dhtDevice.exit()
        raise error

@app.route("/lab_env_db", methods=['GET']) 
def lab_env_db():
	temperatures, humidities, from_date_str, to_date_str = get_records()
	return render_template(	"lab_env_db.html", 	temp 			= temperatures,
							hum 			= humidities,
							from_date 		= from_date_str, 
							to_date 		= to_date_str,
							temp_items 		= len(temperatures),
							hum_items 		= len(humidities))
	
def get_records():
	from_date_str 	= request.args.get('from',time.strftime("%Y-%m-%d 00:00")) #Get the from date value from the URL
	to_date_str 	= request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
	range_h_form	= request.args.get('range_h','');  #This will return a string, if field range_h exists in the request

	range_h_int 	= "nan"  #initialise this variable with not a number

	try: 
		range_h_int	= int(range_h_form)
	except:
		print ("range_h_form not a number")

	if not validate_date(from_date_str):			# Validate date before sending it to the DB
		from_date_str 	= time.strftime("%Y-%m-%d 00:00")
	if not validate_date(to_date_str):
		to_date_str 	= time.strftime("%Y-%m-%d %H:%M")		# Validate date before sending it to the DB

		# If range_h is defined, we don't need the from and to times
	if isinstance(range_h_int,int):	
		time_now		= datetime.datetime.now()
		time_from 		= time_now - datetime.timedelta(hours = range_h_int)
		time_to   		= time_now
		from_date_str   = time_from.strftime("%Y-%m-%d %H:%M")
		to_date_str	    = time_to.strftime("%Y-%m-%d %H:%M")
	
	conn=sqlite3.connect('/var/www/lab_app/lab_app.db')
	curs=conn.cursor()
	curs.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
	temperatures 	= curs.fetchall()
	curs.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
	humidities 		= curs.fetchall()
	conn.close()
	return [temperatures, humidities, from_date_str, to_date_str]

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
