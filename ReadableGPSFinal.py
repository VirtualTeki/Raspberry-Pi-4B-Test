import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

power_key = 6
rec_buff = ''
rec_buff2 = ''
time_count = 0

def send_at(command,back,timeout):
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
            
            print(FinalLat, FinalLong)

            return 1
    else:
        print('GPS is not ready')
        return 0

def get_gps_position():
	rec_null = True
	answer = 0
	print('Start GPS session...')
	rec_buff = ''
	send_at('AT+CGPS=1,1','OK',1)
	time.sleep(2)
	while rec_null:
		answer = send_at('AT+CGPSINFO','+CGPSINFO: ',1)
		if 1 == answer:
			answer = 0
			if ',,,,,,' in rec_buff:
				print('GPS is not ready')
				rec_null = False
				time.sleep(1)
		else:
			print('error %d'%answer)
			rec_buff = ''
			send_at('AT+CGPS=0','OK',1)
			return False
		time.sleep(1.5)

def power_on(power_key):
    print('SIM7600X is starting:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key,GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(20)
    ser.flushInput()
    print('SIM7600x is ready')

def power_down(power_key):
    print('SIM7600X is loging off:')
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(3)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(18)
    print('Goodbye')

power_on(power_key)
while True:

    get_gps_position()


