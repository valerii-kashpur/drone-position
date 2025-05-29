# Adapted script to run in Mission Planner's Scripts tab with AltHold mode
import clr
import MissionPlanner
clr.AddReference("MissionPlanner")
clr.AddReference("MissionPlanner.Utilities")
clr.AddReference("MAVLink")
import math
import System
import MAVLink

# Function to calculate distance between two locations using Haversine formula
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

# Print function for logging in Mission Planner
def log(message):
    print(message)

# Main script
log("Starting script...")

# Set initial home position (latitude 50.450739, longitude 30.461242, altitude 0, heading 0)
log("Setting initial home position...")
MainV2.comPort.doCommand(MAVLink.MAV_CMD.DO_SET_HOME, 0, 0, 0, 0, 50.450739, 30.461242, 0)
System.Threading.Thread.Sleep(2000)  # Wait for the command to process
log("Initial home position set.")

# Set mode to AltHold for takeoff
log("Setting mode to ALTHOLD...")
cs.mode = "ALTHOLD"
while cs.mode != "ALTHOLD":
    System.Threading.Thread.Sleep(1000)
log("Mode set to ALTHOLD.")

# Arm the vehicle
log("Arming vehicle...")
MainV2.comPort.doARM(True)
while not cs.armed:
    System.Threading.Thread.Sleep(1000)
log("Vehicle armed.")

# Take off to 100 meters in AltHold mode using MAV_CMD_TAKEOFF
log("Taking off to 100 meters in ALTHOLD...")
MainV2.comPort.doCommand(MAVLink.MAV_CMD.TAKEOFF, 0, 0, 0, 0, 0, 0, 100)  # Takeoff to 100m

# Wait until altitude is reached
target_alt = 100
while True:
    current_alt = cs.alt
    log("Altitude: " + str(current_alt) + " meters")
    if current_alt >= target_alt * 0.95:
        break
    System.Threading.Thread.Sleep(1000)
log("Reached target altitude.")

# Switch to GUIDED mode for navigation to target location
log("Switching to GUIDED mode for navigation...")
cs.mode = "GUIDED"
while cs.mode != "GUIDED":
    System.Threading.Thread.Sleep(1000)
log("Mode set to GUIDED.")

# Define target location
target_lat = 50.443326
target_lon = 30.448078
target_alt = 100

# Go to target location
log("Going to target location...")
MainV2.comPort.doCommand(MAVLink.MAV_CMD.NAV_WAYPOINT, 0, 0, 0, 0, target_lat, target_lon, target_alt)

# Wait until target is reached
while True:
    current_lat = cs.lat
    current_lon = cs.lng
    distance = haversine_distance(current_lat, current_lon, target_lat, target_lon)
    log("Distance to target: " + str(distance) + " meters")
    if distance < 1:
        break
    System.Threading.Thread.Sleep(1000)
log("Reached target location.")

# Switch back to AltHold mode for yaw adjustment
log("Switching back to ALTHOLD mode...")
cs.mode = "ALTHOLD"
while cs.mode != "ALTHOLD":
    System.Threading.Thread.Sleep(1000)
log("Mode set to ALTHOLD.")

# Set yaw to 350 degrees
log("Setting yaw to 350 degrees...")
MainV2.comPort.doCommand(MAVLink.MAV_CMD.CONDITION_YAW, 0, 350, 0, 0, 0, 0, 0)
System.Threading.Thread.Sleep(5000)  # Wait for yaw to stabilize
log("Yaw set.")

log("Script completed.")