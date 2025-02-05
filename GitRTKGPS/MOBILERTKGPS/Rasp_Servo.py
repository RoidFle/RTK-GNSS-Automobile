import RPi.GPIO as GPIO
from time import sleep
import socket

# Server setup
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5000       # Port TCP Server


# Pin and PWM Configuration
SERVO_PIN = 33 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz PWM frequency
servo_pwm.start(0)

def SetAngle(angle):
    duty = angle / 18 + 2  # Convert angle to duty cycle
    GPIO.output(SERVO_PIN, True)
    servo_pwm.ChangeDutyCycle(duty)
    sleep(0.5)  # Allow time for the servo to move
    GPIO.output(SERVO_PIN, False)  # Optionally turn off the signal


def turn_forward(speed=100):
    SetAngle(90)

def turn_left(speed=100):
    SetAngle(0)

def turn_right(speed=100):
    SetAngle(180)


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
                    turn_forward()
                elif command == 'left':
                    turn_left()
                elif command == 'right':
                    turn_right()

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