#!/usr/bin/python
import RPi.GPIO as GPIO
import serial
import time
ser = serial.Serial("/dev/ttyS0",115200)
ser.flushInput()

def send_at(command,back,timeout):
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01)
        return ser.read(ser.inWaiting()).decode()
    return ""

def get_gps_position():
    print('Start GPS session...')
    send_at('AT+CGPS=0','OK',1)
    send_at('AT+CGPS=1','OK',1)
    time.sleep(2)
    while True:
        response = send_at('AT+CGPSINFO','+CGPSINFO: ',1)
        if '+CGPSINFO: ' in response:
            parts = response.split(',')
            if len(parts) >= 4 and parts[3] != '':
                latitude = float(parts[3])
                longitude = float(parts[4])
                lat_direction = 'N' if latitude >= 0 else 'S'
                long_direction = 'E' if longitude >= 0 else 'W'
                lat_degrees = abs(int(latitude))
                long_degrees = abs(int(longitude))
                lat_minutes = (latitude - lat_degrees) * 60
                long_minutes = (longitude - long_degrees) * 60
                print(f"{lat_degrees}°{lat_minutes:.1f}'{lat_direction} {long_degrees}°{long_minutes:.1f}'{long_direction}")
                break
        elif 'ERROR' in response:
            print('GPS error')
            break
        time.sleep(1.5)

try:
    get_gps_position()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    ser.close()
