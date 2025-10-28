import requests
import time

ROBOT_URL = "http://localhost:5000"
PIPETTE_URL = "http://localhost:5001"
MACHINE_URL = "http://localhost:5002"
BASE_URL = "http://localhost:5003"

import requests

def post(URL, endpoint, data=None):
    """Helper for POST requests"""
    url = f"{URL}{endpoint}"
    res = requests.post(url, json=data)
    try:
        response_json = res.json()
        print(f"[POST] {endpoint} ->", response_json)
        return response_json
    except requests.exceptions.JSONDecodeError:
        # If response is empty or not JSON, just print raw text or status
        print(f"[POST] {endpoint} -> Non-JSON response or server shutdown.")
        print("Status code:", res.status_code)
        print("Response text:", res.text)
        return None


def get(URL, endpoint):
    """Helper for GET requests"""
    url = f"{URL}{endpoint}"
    res = requests.get(url)
    print(f"[GET] {endpoint} ->", res.json())
    return res.json()

if __name__ == "__main__":
    post(BASE_URL, "/reboot")
    input() 
    ###MACHINE#####
    print("=== Starting GRBL ElectroChemister control demo ===")
    # 1 Unlock (clear alarm lock)
    post(MACHINE_URL, "/unlock")
    time.sleep(1)
    # 2 Home the robot
    post(MACHINE_URL, "/home")
    print("Homing... waiting until idle")
    get(MACHINE_URL, "/wait_until_idle")  # Wait for homing to finish
    time.sleep(1)
    # 3 Send a G-code move
    post(MACHINE_URL, "/send_gcode", {"gcode": "G90"})
    time.sleep(2)
    post(MACHINE_URL, "/send_gcode", {"gcode": "G21"})
    time.sleep(2)
    post(MACHINE_URL, "/send_gcode", {"gcode": "G10 L20 P1 X0 Y0 Z0"})
    time.sleep(2)
    post(MACHINE_URL, "/send_gcode", {"gcode": "G1 X25 Z10 F500"})
    get(MACHINE_URL, "/wait_until_idle")
    # 4 Read current position
    get(MACHINE_URL, "/position")
    # 5 Sleep the system
    post(MACHINE_URL, "/sleep")
    print("Done! The pipette is now asleep.")
    input("=== Sequence complete ===")
	###PIPETTE#####
    print("=== Starting GRBL pipette control demo ===")
    # 1 Unlock (clear alarm lock)
    post(PIPETTE_URL,"/unlock")
    time.sleep(1)
    # 2 Home the robot
    post(PIPETTE_URL,"/home")
    print("Homing... waiting until idle")
    get(PIPETTE_URL,"/wait_until_idle")  # Wait for homing to finish
    time.sleep(1)
    # 3 Send a G-code move (absolute move to X=50mm)
    post(PIPETTE_URL,"/send_gcode", {"gcode": "G90"})   # Absolute mode
    time.sleep(2)
    post(PIPETTE_URL,"/send_gcode",{"gcode": "G21"}) # set to mm
    time.sleep(2)
    post(PIPETTE_URL,"/send_gcode", {"gcode": "G10 L20 P1 X0 Y0 Z0"})
    time.sleep(2)
    post(PIPETTE_URL,"/send_gcode", {"gcode": "G1 X25 Z10 F500"})
    get(PIPETTE_URL,"/wait_until_idle")  # Wait until finished moving
    # 4 Read current position
    get(PIPETTE_URL,"/position")
    # 5 Sleep the system (motors off)
    post(PIPETTE_URL,"/sleep")
    print("Done! The pipette is now asleep.")
    input("=== Sequence complete ===")
###ROBOT###
    print("=== Starting GRBL robot control demo ===")
    # 1 Unlock (clear alarm lock)
    post(ROBOT_URL,"/unlock")
    time.sleep(1)
    # 2 Home the robot
    post(ROBOT_URL,"/home")
    print("Homing... waiting until idle")
    get(ROBOT_URL,"/wait_until_idle")  # Wait for homing to finish
    time.sleep(1)
    # 3 Send a G-code move (absolute move to X=50mm)
    post(ROBOT_URL,"/send_gcode", {"gcode": "G90"})   # Absolute mode
    time.sleep(2)
    post(ROBOT_URL,"/send_gcode",{"gcode": "G21"}) # set to mm
    time.sleep(2)
    post(ROBOT_URL,"/send_gcode", {"gcode": "G10 L20 P1 X0 Y0 Z0"})
    time.sleep(2)
    post(ROBOT_URL, "/send_gcode", {"gcode": "G1 X25 Y25 Z10 F500"})
    get(ROBOT_URL, "/wait_until_idle")  # Wait until finished moving
    # 4 Read current position
    get(ROBOT_URL, "/position")
    # 5 Sleep the system (motors off)
    post(ROBOT_URL, "/sleep")
    print("Done! The robot is now asleep.")
    print("=== Sequence complete ===")
   
    #print(res.json())





