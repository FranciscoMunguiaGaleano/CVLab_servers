# quantos_server.py
from flask import Flask, jsonify, request
from pylabware import QuantosQB1
import time

app = Flask(__name__)

# Serial port for your Quantos device
QUANTOS_PORT = "/dev/dispenser_of_solids"
# ---- Initialize Quantos as a global variable ----
quantos: QuantosQB1 = None

def init_quantos():
    global quantos
    if quantos is None:
        quantos = QuantosQB1(device_name="QUANTOS", connection_mode="serial", port=QUANTOS_PORT)
        try:
            print("Connecting to the Quantos - opening doors")
            #side = quantos.open_side_door()
            #time.sleep(1)
            #front = quantos.open_front_door()
            #time.sleep(3)
            side = quantos.close_side_door()
            time.sleep(1)
            pin = quantos.unlock_dosing_head_pin()
            time.sleep(1)
            front = quantos.close_front_door()
            time.sleep(3)
            if side["success"] and front["success"] and pin["success"]:
                print("Quantos connected")
        except Exception as e:
            print("Quantos not connected:", e)

# Call this once before the first request

@app.route("/status", methods=["GET"])
def status():
    try:
        connected = quantos.is_connected()
        return jsonify({"connected": connected})
    except Exception as e:
        return jsonify({"connected": False, "error": str(e)}), 500

@app.route("/dispense", methods=["POST"])
def dispense():
    """
    Dispense a sample.
    Expects JSON:
    {
        "sample_id": "Sample1",
        "mass": 50.0,
        "tolerance": 1.0,          # optional
        "algorithm": "standard",    # optional, "standard" or "advanced"
        "tapper_intensity": 50,     # optional
        "tapper_duration": 3        # optional
    }
    """
    data = request.json
    try:
        sample_id = data["sample_id"]
        mass = float(data["mass"])
        tolerance = float(data.get("tolerance", 1.0))
        algorithm = data.get("algorithm", "standard")
        tapper_intensity = int(data.get("tapper_intensity", 50))
        tapper_duration = int(data.get("tapper_duration", 3))

        # Set up the dispenser
        quantos.set_sample_id(sample_id)
        quantos.set_target_mass(mass)
        quantos.set_tolerance_value(tolerance)

        if algorithm == "standard":
            quantos.set_algorithm_standard()
        else:
            quantos.set_algorithm_advanced()

        quantos.set_tapper_intensity(tapper_intensity)
        quantos.set_tapper_duration(tapper_duration)
        quantos.set_tapping_before_dosing()

        # Start dosing
        dosing_reply = quantos.start_dosing()

        # Wait a little if needed, or polling can be added here
        time.sleep(1)

        # Fetch sample data after dosing
        sample_data = quantos.get_sample_data()

        return jsonify({
            "dosing_reply": dosing_reply,
            "sample_data": sample_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/open_front_door", methods=["POST"])
def open_front_door():
    try:
        result = quantos.open_front_door()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/close_front_door", methods=["POST"])
def close_front_door():
    try:
        result = quantos.close_front_door()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/open_side_door", methods=["POST"])
def open_side_door():
    try:
        result = quantos.open_side_door()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/close_side_door", methods=["POST"])
def close_side_door():
    try:
        result = quantos.close_side_door()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/unlock_dosing_head", methods=["POST"])
def unlock_dosing_head():
    try:
        result = quantos.unlock_dosing_head_pin()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/lock_dosing_head", methods=["POST"])
def lock_dosing_head():
    try:
        result = quantos.lock_dosing_head_pin()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get_sample_data", methods=["GET"])
def get_sample_data():
    try:
        result = quantos.get_sample_data()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/tare_balance", methods=["POST"])
def tare_balance():
    try:
        result = quantos.tare()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/set_target_mass", methods=["POST"])
def set_target_mass():
    try:
        data = request.json
        mass = data.get("mass")
        result = quantos.set_target_mass(mass)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    init_quantos()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False)
