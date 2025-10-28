# example_quantos_client.py
import requests
import time

BASE_URL = "http://localhost:5000"  # Replace with your Raspberry Pi IP if remote

def post(endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        res = requests.post(url, json=data)
        res.raise_for_status()
        response_json = res.json()
        print(f"[POST] {endpoint} -> {response_json}")
        return response_json
    except Exception as e:
        print(f"[POST] {endpoint} failed:", e)
        return None

def get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        response_json = res.json()
        print(f"[GET] {endpoint} -> {response_json}")
        return response_json
    except Exception as e:
        print(f"[GET] {endpoint} failed:", e)
        return None

if __name__ == "__main__":
    print("=== Quantos API Demo ===")

    input("# 1. Check connection")
    get("/status")
    input()

    input("# 2. Open front and side doors")
    post("/open_side_door")
    time.sleep(3)
    post("/open_front_door")
    time.sleep(2)
    input()

    # 3. Unlock dosing head
    post("/unlock_dosing_head")
    time.sleep(1)

    # 4. Set sample ID and target mass
    #sample_data = {"sample_id": "DemoSample", "mass": 50.0}
    #post("/set_target_mass", {"mass": 50.0})
    #post("/dispense", sample_data)

    # 5. Wait for dosing and get sample data
    #time.sleep(3)  # optional wait
    #get("/get_sample_data")

    # 6. Close doors and lock dosing head
    post("/close_front_door")
    time.sleep(3)
    post("/close_side_door")
    time.sleep(1)
    #post("/lock_dosing_head")
    get("/status")

    print("=== Demo finished ===")
