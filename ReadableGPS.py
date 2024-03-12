#!/usr/bin/python
import RPi.GPIO as GPIO
import serial
import time
ser = serial.Serial("/dev/ttyS0", 115200)
ser.flushInput()

def send_at(command, back, timeout):
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01)
        return ser.read(ser.inWaiting()).decode()
    return ""

def convert_coordinates(coordinate_str):
    # Extract numerical part and direction part
    parts = coordinate_str.split('.')
    degrees = int(parts[0][:-2])
    minutes = float('0.' + parts[0][-2:] + '.' + parts[1])
    direction = coordinate_str[-1]
    return degrees, minutes, direction

def get_gps_position():
    print('Start GPS session...')
    send_at('AT+CGPS=0', 'OK', 1)
    send_at('AT+CGPS=1', 'OK', 1)
    time.sleep(2)
    while True:
        response = send_at('AT+CGPSINFO', '+CGPSINFO: ', 1)
        if '+CGPSINFO: ' in response:
            parts = response.split(',')
            if len(parts) >= 5 and parts[3] != '':
                latitude_degrees, latitude_minutes, lat_direction = convert_coordinates(parts[3])
                longitude_degrees, longitude_minutes, long_direction = convert_coordinates(parts[4])
                print(f"{latitude_degrees}°{latitude_minutes:.1f}'{lat_direction} {longitude_degrees}°{longitude_minutes:.1f}'{long_direction}")
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
