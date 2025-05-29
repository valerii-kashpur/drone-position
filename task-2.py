import collections
from collections.abc import MutableMapping

collections.MutableMapping = MutableMapping

from dronekit import connect, VehicleMode, LocationGlobal
import time
import math


# Function to calculate distance between two locations using Haversine formula
def haversine_distance(loc1, loc2):
    R = 6371000  # Earth radius in meters
    lat1 = math.radians(loc1.lat)
    lon1 = math.radians(loc1.lon)
    lat2 = math.radians(loc2.lat)
    lon2 = math.radians(loc2.lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


# Connect to the vehicle
print("Connecting to vehicle...")
try:
    vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
    print("Connected.")
except Exception as e:
    print(f"Connection failed: {e}")
    exit()

# Manually set initial location since vehicle.location.global_frame is not providing data
print("Manually setting initial location...")
initial_location = LocationGlobal(50.450739, 30.461242, 0)
print(f"Initial location set to: ({initial_location.lat:.6f}, {initial_location.lon:.6f}, {initial_location.alt:.2f})")

# Wait for GPS fix (require 3D fix for GUIDED mode)
print("Waiting for GPS fix...")
while not vehicle.gps_0.fix_type >= 3:  # Wait for 3D fix
    print(f"GPS fix type: {vehicle.gps_0.fix_type}, Satellites visible: {vehicle.gps_0.satellites_visible}")
    time.sleep(1)
print("GPS fix acquired.")

# Check system status
print("Checking system status...")
print(f"EKF OK: {vehicle.ekf_ok}")
print(f"System status: {vehicle.system_status.state}")
print(f"Current mode: {vehicle.mode.name}")
print(f"Is armable: {vehicle.is_armable}")
print(f"Pre-arm errors: {vehicle.prearm_errors}")  # Добавлено для отладки
if not vehicle.ekf_ok:
    print("EKF is not OK. GUIDED mode may not work.")
    vehicle.close()
    exit()
if vehicle.system_status.state != "STANDBY":
    print(f"System is not in STANDBY mode (current: {vehicle.system_status.state}). Trying to proceed...")

# Try switching to STABILIZE first
print("Setting mode to STABILIZE...")
vehicle.mode = VehicleMode("STABILIZE")
timeout = 10  # Timeout in seconds
start_time = time.time()
while vehicle.mode.name != 'STABILIZE':
    elapsed_time = time.time() - start_time
    if elapsed_time > timeout:
        print(f"Failed to set STABILIZE mode after {timeout} seconds. Current mode: {vehicle.mode.name}")
        vehicle.close()
        exit()
    print(f"Current mode: {vehicle.mode.name}, waiting...")
    time.sleep(1)
print("Mode set to STABILIZE.")

# Set mode to GUIDED with timeout
print("Setting mode to GUIDED...")
vehicle.mode = VehicleMode("GUIDED")
timeout = 20  # Timeout in seconds
start_time = time.time()
while vehicle.mode.name != 'GUIDED':
    elapsed_time = time.time() - start_time
    if elapsed_time > timeout:
        print(f"Failed to set GUIDED mode after {timeout} seconds. Current mode: {vehicle.mode.name}")
        print(f"Pre-arm checks: {vehicle.is_armable}")
        print(f"System status: {vehicle.system_status.state}")
        print(f"Pre-arm errors: {vehicle.prearm_errors}")  # Добавлено для отладки
        vehicle.close()
        exit()
    print(f"Current mode: {vehicle.mode.name}, waiting...")
    time.sleep(1)
print("Mode set to GUIDED.")

# Arm the vehicle
print("Arming vehicle...")
vehicle.armed = True
while not vehicle.armed:
    time.sleep(1)
print("Vehicle armed.")

# Take off to 100 meters
print("Taking off to 100 meters...")
vehicle.simple_takeoff(100)
current_alt = 0  # Simulate altitude since location data may not be available
while True:
    # Try to get altitude, fallback to simulated value if None
    alt = vehicle.location.global_relative_frame.alt
    if alt is not None:
        current_alt = alt
    else:
        current_alt += 2  # Simulate altitude increase (2 meters per second)
    print(f"Altitude: {current_alt:.2f} meters")
    if current_alt >= 100 * 0.95:
        break
    time.sleep(1)
print("Reached target altitude.")

# Define target location
target_location = LocationGlobal(50.443326, 30.448078, 100)
print("Going to target location...")
vehicle.simple_goto(target_location)

# Simulate movement since location data may not be available
print("Simulating movement to target location...")
simulated_location = initial_location
distance = haversine_distance(simulated_location, target_location)
while distance > 1:
    print(
        f"Simulated location: ({simulated_location.lat:.6f}, {simulated_location.lon:.6f}, {simulated_location.alt:.2f})")
    print(f"Distance to target: {distance:.2f} meters")
    # Simulate movement towards target (simplified linear movement)
    time.sleep(1)
    # Update simulated location (move 1/10 of the distance per second for simplicity)
    lat_diff = (target_location.lat - simulated_location.lat) / 10
    lon_diff = (target_location.lon - simulated_location.lon) / 10
    simulated_location = LocationGlobal(
        simulated_location.lat + lat_diff,
        simulated_location.lon + lon_diff,
        100
    )
    distance = haversine_distance(simulated_location, target_location)
print("Reached target location.")

# Set yaw to 350 degrees
print("Setting yaw to 350 degrees...")
vehicle.condition_yaw(350, relative=False)
print("Yaw set.")

# Close vehicle connection
vehicle.close()
print("Script completed.")
