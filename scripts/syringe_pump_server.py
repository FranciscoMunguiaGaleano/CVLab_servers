from flask import Flask, jsonify, request
from pylabware import C3000SyringePump
import time

app = Flask(__name__)

# --- Configuration ---
PUMP_PORT = "/dev/dispenser_of_liquids"        
SWITCH_ADDRESS = "0"
SYRINGE_SIZE = "12.5mL"
VALVE_TYPE = "6PORT_DISTR"
WASTE_PORT = "O4"
WATER_PORT = "I2"

pump: C3000SyringePump = None

def init_pump():
    """Initialize and connect to the syringe pump."""
    global pump
    if pump is None:
        pump = C3000SyringePump("CVLabsyringePump",connection_mode="serial", port = PUMP_PORT, address="1", switch_address="0", valve_type=VALVE_TYPE, syringe_size=SYRINGE_SIZE)
        try:
            print("Connecting to C3000 syringe pump...")
            pump.connect()
            time.sleep(0.5)
            pump.is_connected()
            print("Pump connected.")
            time.sleep(0.5)
            print(pump.get_valve_position())
            pump.initialize_device(input_port=int(WASTE_PORT[1]),output_port=int(WASTE_PORT[1]))
            while not pump.is_idle():
                time.sleep(0.1)
            print("C3000 connected and initialized.")
        except Exception as e:
            print("Failed to connect to C3000:", e)

@app.route("/status", methods=["GET"])
def status():
    try:
        connected = pump.is_connected()
        idle = pump.is_idle()
        return jsonify({"connected": connected, "idle": idle})
    except Exception as e:
        return jsonify({"connected": False, "error": str(e)}), 500
        
@app.route("/get_valve_pos", methods=["GET"])
def get_valve_pos():
    try:
        connected = pump.is_connected()
        pos = pump.get_valve_position()
        return jsonify({"connected": connected, "valve_position": pos})
    except Exception as e:
        return jsonify({"connected": False, "error": str(e)}), 500


@app.route("/dispense", methods=["POST"])
def dispense():
    data = request.json
    try:
        volume = float(data["volume"])
        source_port = data.get("source_port", "I1")
        destination_port = data.get("destination_port", "O1")

        pump.dispense(volume, source_port, destination_port)
        return jsonify({
            "success": True,
            "message": f"Dispensed {volume} µL from {source_port} to {destination_port}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/move_home", methods=["POST"])
def move_home():
	try:
		pump.set_valve_position(requested_position=WASTE_PORT)
		time.sleep(0.1)
		pump.move_home()
		while not pump.is_idle():
			time.sleep(0.1)
		return jsonify({"success": True, "message": "Plunger returned home"})
	except Exception as e:
        	return jsonify({"success": False, "error": str(e)}), 500

@app.route("/set_waste_port", methods=["POST"])
def set_waste_port():
	data = request.json
	try:
		WASTE_PORT= data["waste_port"]
		return jsonify({
            "success": True,
            "message": f"Waste port set to {WASTE_PORT}"
        })
	except Exception as e:
		return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    init_pump()
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True,
        use_reloader=False
    )
