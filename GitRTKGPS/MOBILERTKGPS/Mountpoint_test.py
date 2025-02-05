import socket
import base64
import serial
import time  # นำเข้า time module เพื่อใช้หน่วงเวลา

# กำหนดประเภทการแก้ไข GPS fix
fix_type = { 
    '0': "Invalid",
    '1': "GPS fix (SPS)",
    '2': "DGPS fix",
    '3': "PPS fix",
    '4': "Real Time Kinematic",
    '5': "Float RTK",
    '6': "Estimated (dead reckoning)",
    '7': "Manual input mode",
    '8': "Simulation mode"
} 

# ฟังก์ชันในการแปลงจากรูปแบบ DDMM.MMMM เป็น Decimal Degree
def convert_to_decimal(degrees_minutes):
    degrees = int(degrees_minutes // 100)  # แยกค่าดีกรี
    minutes = degrees_minutes % 100        # แยกค่านาที
    decimal = degrees + (minutes / 60)     # แปลงเป็นทศนิยม
    return decimal

# เปิด Serial Port สำหรับเชื่อมต่อกับ GPS receiver
ser = serial.Serial('COM7', 9600, timeout=0)

# ตั้งค่าการเชื่อมต่อกับ NTRIP server
server, port, username, password, mountpoint = 'rtk2go.com', 2101, "niawit.ssw@gmail.com", "none", "kanit325"

# เข้ารหัสข้อมูล username:password
pwd = base64.b64encode(f"{username}:{password}".encode()).decode()

# สร้าง HTTP Request Header
header = (
    f"GET /{mountpoint} HTTP/1.1\r\n"
    f"Host: {server}\r\n"
    "Ntrip-Version: Ntrip/2.0\r\n"
    "User-Agent: NTRIP pyUblox/0.0\r\n"
    "Connection: close\r\n"
    f"Authorization: Basic {pwd}\r\n\r\n"
)

# สร้าง socket และเชื่อมต่อไปยัง NTRIP server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server, int(port)))
s.send(header.encode())

# รับการตอบกลับจาก NTRIP server
resp = s.recv(1024)
print("Receiving NTRIP data over enetlk servers")

try:
    while True:
        # อ่านข้อมูลจาก GPS receiver ในรูปแบบ bytes
        RoverMessege = ser.readline()

        # ตรวจสอบว่าเป็นข้อมูล NMEA GGA หรือไม่
        try:
            # ตรวจสอบว่า RoverMessege เป็นข้อมูลที่สามารถใช้ได้หรือไม่
            if RoverMessege:
                # หลีกเลี่ยงการแปลงเป็น string โดยตรง
                if b'GGA' in RoverMessege:  # ตรวจสอบข้อมูล 'GGA' โดยใช้ bytes
                    data = RoverMessege.split(b",")  # ใช้ bytes แทน string
                    if len(data) > 6:
                        # แสดงผลข้อมูลที่ได้จาก GGA ในรูปแบบของตัวเลข
                        try:
                            # แปลงค่าละติจูดและลองจิจูด
                            lat = convert_to_decimal(float(data[2]))
                            lon = convert_to_decimal(float(data[4]))

                            # แสดงผลข้อมูล Fix Type, Latitude, Longitude
                            print(f"Fix Type: {fix_type[data[6].decode()]}, Latitude: {lat}, Longitude: {lon}")
                        except ValueError:
                            print("Error in parsing GGA message values")
        except Exception as e:
            print(f"Error in reading Rover message: {e}")

        # รับข้อมูล RTCM จาก NTRIP server และส่งไปยัง GPS receiver
        data = s.recv(1024)
        if data:
            ser.write(data)  # ส่งข้อมูล RTCM ไปยัง GPS receiver

finally:
    s.close()
    ser.close()
