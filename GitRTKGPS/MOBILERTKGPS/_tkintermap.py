import tkinter as tk
from tkinter import Tk, Canvas
import tkintermapview as TkinterMapView
import threading
import socket
import statistics
from math import cos, sin, radians
import geopy.distance

##Declare###
latitude = None
longitude = None

markers = []
gps = []
movement = {}

HOST = '172.20.10.2' #'10.42.0.1'
PORT = 5000


##################################################################################################################################
                                                    ##TCP/IP Setup##
##################################################################################################################################

def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(command.encode('utf-8'))
        print(f"Sent command: {command}")

        if command == 'get_coordinates'or command == 'get_compass':
            data = s.recv(1024)
            if command == 'get_coordinates':
                coordinates = data.decode('utf-8')
                print(f"Received GPS coordinates: {coordinates}")
                # Split
                lat, lon = map(float, coordinates.split(',')) # lat= coordinate[0] lon= coordinates[1]
                get_gps((lat, lon))
                
            if command == 'get_compass':
                compass = data.decode('utf-8')
                print(f"Received Compass: {compass} Degree")
                update_compass(compass)

def listen_for_input():
    while True:
        key = input(
            "Press a key (w/a/s/d/q) to move, Coordinate (x), Compass(t) ").lower()
        if key in movement:
            continue  # Prevent sending the same command repeatedly

        command = ''
        if key == 'w':
            command = 'forward'
        elif key == 'a':
            command = 'left'
        elif key == 's':
            command = 'backward'
        elif key == 'd':
            command = 'right'
        elif key == 'q':
            command = 'stop'
        elif key == 'x':
            command = 'get_coordinates'
        elif key == 't':
            command = 'get_compass'   
        elif key == 'r':
            command = 'reset_sensor'   
        else:
            continue

        movement[key] = True
        send_command(command)

        input("Press Enter to stop command...")
        stop_command = f"stop_{command}"
        send_command(stop_command)
        del movement[key]

##################################################################################################################################
                                                    ##GPS Setup##
##################################################################################################################################

# GPS Marker Function
def get_gps(coordinates):
    global gps
    # Insert GPS to gps list
    gps.insert(0, coordinates)
    print(f"GPS Markers list: {gps}")
    
    # split lat , lon from coordinates then sent to update_marker_gps function
    lat, lon = coordinates
    update_marker_gps(lat, lon)

def update_marker_gps(lat, lon):
    global gps
    
    # Add Marker on map GPS 
    map_widget.set_marker(lat, lon)
    
    # Pop Newest GPS when > 5 
    if len(gps) > 5:
        gps.pop()
    
    # Draw Path GPS when > 1 
    if len(gps) > 1:
        path_points = [(lat, lon) for lat, lon in gps]  # Set Patch btw points to points
        map_widget.set_path(path_points)


##################################################################################################################################
                                                    ##Distance Calculator##
##################################################################################################################################

# def distance(gps,markers):  #อาจจะเกิด Bug 
#     coords_1 = (16.4720387, 102.8253388) #gps[0]
#     coords_2 = (16.4720515, 102.8256835) #gps]1]
#     print(geopy.distance.geodesic(coords_1, coords_2).km)    

##################################################################################################################################
                                                    ##Widget Setup##
##################################################################################################################################

# Setting GUI
root_tk = tk.Tk()
root_tk.geometry("1200x600")
root_tk.title("RTK GPS")

# Setting location
map_widget = TkinterMapView.TkinterMapView(root_tk, width=600, height=600, corner_radius=0)
map_widget.pack(fill="both", expand=True)
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # Google normal
map_widget.set_position(16.472102, 102.825288)

# Compass widget setup
root = Tk()
root.title("Compass")
canvas = Canvas(root, width=250, height=250, bg="white")
canvas.pack()

# Function to update compass
def update_compass(compass):
    global compass_angle
    try:
        compass_angle = float(compass)  # Convert the compass angle to float
    except ValueError:
        print("Invalid compass value received:", compass)
        return  # Exit if value can't convert to float
    # Draw compass in loop
    root_tk.after(0, draw_compass, compass_angle)

# Updated draw_compass function that runs in the main thread
def draw_compass(angle):
    radius = 60
    # Get canvas size
    canvas_width = int(canvas.cget("width"))
    canvas_height = int(canvas.cget("height"))

    # Calculate center of the compass
    x0, y0 = canvas_width // 2, canvas_height // 2

    canvas.delete("all")  # Clear the canvas
    angle_rad = radians(angle)  # Convert the angle to radians
    x1 = x0 + radius * sin(angle_rad)
    y1 = y0 - radius * cos(angle_rad)

    # Draw the compass circle
    canvas.create_oval(x0-radius, y0-radius, x0+radius, y0+radius, outline="black", width=2)

    # Draw North, South, East, West
    canvas.create_text(x0, y0-radius-10, text="N", fill="black", font=('Arial', 15, 'bold'))  # North
    canvas.create_text(x0, y0+radius+10, text="S", fill="black", font=('Arial', 15, 'bold'))  # South
    canvas.create_text(x0-radius-10, y0, text="W", fill="black", font=('Arial', 15, 'bold'))  # West
    canvas.create_text(x0+radius+10, y0, text="E", fill="black", font=('Arial', 15, 'bold'))  # East
    # Draw line
    canvas.create_line(x0, y0, x1, y1, fill="red", width=2)

##################################################################################################################################
                                                    ##Function Click On Map##
##################################################################################################################################

# Function click
def left_click_event(coordinates_tuple):
    print("Left click event with Coordinates:", coordinates_tuple)

map_widget.add_left_click_map_command(left_click_event)

def add_marker_event1(coords):
    print("Right-click event with Add Marker1:", coords)
    map_widget.set_marker(coords[0], coords[1])
    markers.insert(0, coords) 
    if len(markers) > 1:
        btw = markers[0]
        btw2 = markers[1]
        map_widget.set_path([btw2, btw])
    print("Marker1 list:", markers)    

map_widget.add_right_click_menu_command(label="Add Marker1", command=add_marker_event1, pass_coords=True)

def del_marker():  # Delete all markers
    map_widget.delete_all_marker()
    map_widget.delete_all_path()
    markers.clear()
    print("Clear Done")

map_widget.add_right_click_menu_command(label="Delete Markers", command=del_marker, pass_coords=True)

# Run the input listener in a separate thread
input_thread = threading.Thread(target=listen_for_input)
input_thread.start()

# Start the Tkinter main loop
root_tk.mainloop()
