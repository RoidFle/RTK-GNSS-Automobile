import socket
import RPi.GPIO as GPIO
import time
import sys
import serial

# sys.path.append('/home/gunpi5/Project')
# from py_qmc5883l import QMC5883L

# Server setup
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5000       # Port TCP Server

# GPIO Pin setup for motors
ENA = 12  # PWM0 (GPIO 12)
ENB = 13  # PWM1 (GPIO 13)
IN1, IN2 = 17, 22  # ทิศทางมอเตอร์ซ้าย
IN3, IN4 = 23, 24  # ทิศทางมอเตอร์ขวา

# # I2C setup for compass
# I2C_BUS = 1
# DEVICE_ADDRESS = 0x0D
# sensor = QMC5883L(I2C_BUS, DEVICE_ADDRESS)
# sensor.calibration = [
#     [1.0, 0.0, 0.0],  #x
#     [0.0, 1.0, 0.0],  #y
#     [0.0, 0.0, 1.0]   #z
# ]

# Motor control setup
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([ENA, IN1, IN2, ENB, IN3, IN4], GPIO.OUT)
    left_pwm = GPIO.PWM(ENA, 100)  # 100 Hz frequency
    right_pwm = GPIO.PWM(ENB, 100)  # 100 Hz frequency
    left_pwm.start(0)  # Start with 0% duty cycle
    right_pwm.start(0)  # Start with 0% duty cycle
    return left_pwm, right_pwm

left_pwm, right_pwm = setup_gpio()

# Motor control functions
def move_forward(speed=100):
    print("Moving forward")
    GPIO.output([IN1, IN3], GPIO.HIGH)
    GPIO.output([IN2, IN4], GPIO.LOW)
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)
    #time.sleep(1)
    #stop()

def move_backward(speed=100):
    print("Moving backward")
    GPIO.output([IN1, IN3], GPIO.LOW)
    GPIO.output([IN2, IN4], GPIO.HIGH)
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)
    # time.sleep(3)
    # stop()

def turn_left(speed=100):
    print("Moving left")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)
    # stop()

def turn_right(speed=100):
    print("Moving right")
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)
    # stop()

def stop():
    print("Stop Moving")
    left_pwm.ChangeDutyCycle(0)
    right_pwm.ChangeDutyCycle(0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

# # Compass setup (QMC5883L)
# def degrees_to_heading(degrees):
#     if degrees < 0:
#         degrees += 360
#     headings = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
#     idx = round(degrees / 45) % 8
#     return headings[idx]

# # GPS class
# class GPS:
#     def __init__(self):
#         self.latitude = 0.0
#         self.longitude = 0.0

#     def read_serial_data(self):
#         try:
#             with serial.Serial('/dev/ttyUSB0', 9600, timeout=None) as ser:
#                 while True:
#                     if ser.in_waiting > 0:
#                         line = ser.readline().decode("utf-8").strip()
#                         if not line.startswith('$GPRMC'): continue
#                         data = line.split(",")
#                         if len(data) < 7: continue
#                         lat = self._convert_to_degrees(data[3], data[4] == 'S')
#                         lon = self._convert_to_degrees(data[5], data[6] == 'W')
#                         return lat, lon
#         except serial.SerialException as e:
#             print(f"GPS error: {e}")
#             return None, None

#     def _convert_to_degrees(self, nmea, is_negative):
#         if len(nmea) < 4: return 0.0
#         degrees = float(nmea[:2 if len(nmea) == 9 else 3])
#         minutes = float(nmea[2:]) / 60
#         return (degrees + minutes) * (-1 if is_negative else 1)

# gps = GPS()

# TCP/IP control
def handle_control(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"Client {addr} disconnected.")
                    break
                command = data.decode('utf-8').strip()

                # Handle movement commands
                if command == 'forward':
                    move_forward()
                elif command == 'backward':
                    move_backward()
                elif command == 'left':
                    turn_left()
                elif command == 'right':
                    turn_right()
                elif command == 'stop':
                    stop()
            #     # Handle GPS request
            #     if command == 'get_coordinates':
            #         lat, lon = gps.read_serial_data()
            #         if lat and lon:
            #             conn.sendall(f"{lat},{lon}".encode('utf-8'))
            #         else:
            #             conn.sendall(b"GPS error")
            #     # Handle compass request
            #     elif command == 'get_compass':
            #         try:
            #             bearing = sensor.get_bearing()
            #             #heading = degrees_to_heading(bearing)
            #             conn.sendall(f"{bearing}".encode('utf-8'))
            #         except Exception as e:
            #             print(f"Compass error: {e}")
            #             conn.sendall(b"Compass error")
            except Exception as e:
                print(f"Command handling error: {e}")
                break

# Start the server
def start_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 5000))
            s.listen()
            print(f"Server listening on {HOST}:{PORT}")
            while True:
                conn, addr = s.accept()
                handle_control(conn, addr)
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        GPIO.cleanup()

# Main execution
if __name__ == "__main__":
    start_server()