import requests
import time
from pylabware import C3000SyringePump

API_URL = "http://localhost:5001"  # Replace with your server’s IP if remote


# --- Configuration ---
PUMP_PORT = "/dev/dispenser_of_liquids"        
SWITCH_ADDRESS = "0"
SYRINGE_SIZE = "12.5mL"
VALVE_TYPE = "6PORT_DISTR"
WASTE_PORT = "O3"
WATER_PORT = "I2"

pump: C3000SyringePump = None

def get(endpoint):
    url = f"{API_URL}{endpoint}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        response_json = res.json()
        print(f"[GET] {endpoint} -> {response_json}")
        return response_json
    except Exception as e:
        print(f"[GET] {endpoint} failed:", e)
        return None

def post(endpoint, data=None):
    url = f"{API_URL}{endpoint}"
    try:
        res = requests.post(url, json=data)
        res.raise_for_status()
        response_json = res.json()
        print(f"[POST] {endpoint} -> {response_json}")
        return response_json
    except Exception as e:
        print(f"[POST] {endpoint} failed:", e)
        return None


def single_dispense(volume=500,couser_port="I1",detination_port="O1"):
    payload = {"volume": volume, "source_port": "I1", "destination_port": "O1"}
    r = requests.post(f"{API_URL}/dispense", json=payload)
    print("Dispense:", r.json())

if __name__ == "__main__":
	get("/status")
	get("/get_valve_pos")
	post("/set_waste_port", data={"waste_port": "O4"})
	volume = 2000
	post("/dispense",data={"volume": volume, "source_port": "I2", "destination_port": "O3"})

