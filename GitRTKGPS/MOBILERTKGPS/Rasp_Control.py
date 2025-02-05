import socket
import RPi.GPIO as GPIO
import time
import sys
import smbus
import serial



# Server setup
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5000       # Port TCP Server

# GPIO Pin setup for motors
ENA = 12  # PWM0 (GPIO 12)
ENB = 13  # PWM1 (GPIO 13)
IN1, IN2 = 17, 22  # ทิศทางมอเตอร์ซ้าย
IN3, IN4 = 23, 24  # ทิศทางมอเตอร์ขวา

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