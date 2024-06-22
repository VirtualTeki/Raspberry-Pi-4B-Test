import sqlite3
import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

def log_values(sensor_id, lat, long):
    conn=sqlite3.connect('/var/www/lab_app/gps_app.db')  # change this to your database path
    curs=conn.cursor()
    curs.execute("""INSERT INTO coordinates (rDatetime, sensorID, latitude, longitude) values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?), (?))""", (sensor_id, lat, long))
    conn.commit()
    conn.close()

def send_at(command,back,timeout):
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    rec_buff = ''
    if ser.inWaiting():
        time.sleep(0.01)
        rec_buff = ser.read(ser.inWaiting())
    if rec_buff != '':
        if back not in rec_buff.decode():
            return 0, rec_buff
        else:
            GPSDATA = str(rec_buff.decode())
            start_index = GPSDATA.find(':') + 2
            Cleaned = GPSDATA[start_index:]
            
            Lat = Cleaned[:2]
            SmallLat = Cleaned[2:11]
            NorthOrSouth = Cleaned[12]
            
            Long = Cleaned[14:17]
            SmallLong = ''.join(filter(lambda x: x.isdigit() or x == '.', Cleaned[17:26]))
            EastOrWest = Cleaned[27]
            
            FinalLong = float(Long) + (float(SmallLong)/60)
            FinalLat = float(Lat) + (float(SmallLat)/60)
            if EastOrWest == 'W': FinalLong = -FinalLong
            if NorthOrSouth == 'S': FinalLat = -FinalLat
            
            log_values("1", FinalLat, FinalLong)
            #print(FinalLat, FinalLong)

            return 1, rec_buff
    else:
        return 0, rec_buff

def get_gps_position():
    send_at('AT+CGPS=1,1','OK',1)
    time.sleep(2)
    while True:
        answer, rec_buff = send_at('AT+CGPSINFO','+CGPSINFO: ',1)
        if 1 == answer:
            answer = 0
            if ',,,,,,' in rec_buff.decode():
                time.sleep(1)
                continue
        else:
            rec_buff = ''
            send_at('AT+CGPS=0','OK',1)
            return False
        time.sleep(1.5)

try:
    while True:
        get_gps_position()
except KeyboardInterrupt:
    ser.close()
