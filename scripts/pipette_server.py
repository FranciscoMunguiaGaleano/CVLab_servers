from flask import Flask, request, jsonify
import serial
import time
import re

app = Flask(__name__)

GRBL_PORT = '/dev/CVLabpipette'
BAUD_RATE = 115200


def connect_grbl():
    """Try to open the serial connection"""
    try:
        s = serial.Serial(GRBL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # wait for GRBL to initialize
        s.flushInput()
        print("✅ Connected to GRBL")
        return s
    except Exception as e:
        print(f"⚠️ Could not connect: {e}")
        return None


grbl = connect_grbl()


def send_command(cmd):
    global grbl
    if not grbl:
        grbl = connect_grbl()
        if not grbl:
            return "Serial connection failed"

    try:
        line = cmd.strip() + '\n'  # remove extra spaces + add newline
        grbl.write(line.encode('utf-8'))
        grbl.flush()
        time.sleep(0.1)  # small delay
        resp = grbl.readline().decode('utf-8').strip()
        return resp
    except Exception as e:
        return str(e)



def get_status_line():
    """Query GRBL for current status line"""
    global grbl
    try:
        grbl.write(b'?')
        grbl.flush()
        time.sleep(0.1)
        resp = grbl.readline().decode('utf-8').strip()
        return resp
    except Exception as e:
        return str(e)


def parse_position(status_line):
    """Extract state, MPos, WPos from GRBL status line"""
    # Match state at start, then MPos and WPos
    state_match = re.match(r"<([A-Za-z]+)", status_line)
    state = state_match.group(1) if state_match else "Unknown"

    # Match MPos
    mpos_match = re.search(r"MPos:([-0-9.]+),([-0-9.]+),([-0-9.]+)", status_line)
    mpos = {}
    if mpos_match:
        mpos = {
            "X": float(mpos_match.group(1)),
            "Y": float(mpos_match.group(2)),
            "Z": float(mpos_match.group(3))
        }

    # Match WPos
    wpos_match = re.search(r"WPos:([-0-9.]+),([-0-9.]+),([-0-9.]+)", status_line)
    wpos = {}
    if wpos_match:
        wpos = {
            "X": float(wpos_match.group(1)),
            "Y": float(wpos_match.group(2)),
            "Z": float(wpos_match.group(3))
        }

    # Match limits
    lim_match = re.search(r"Lim:([0-1]{3})", status_line)
    limits = {}
    if lim_match:
        bits = lim_match.group(1)
        limits = {"X": int(bits[0]), "Y": int(bits[1]), "Z": int(bits[2])}

    return {"state": state, "MPos": mpos, "WPos": wpos, "Limits": limits, "raw": status_line}



@app.route('/send_gcode', methods=['POST'])
def send_gcode():
    data = request.get_json()
    if not data or 'gcode' not in data:
        return jsonify({"error": "Missing 'gcode' in request"}), 400

    response = send_command(data['gcode'])
    return jsonify({"sent": data['gcode'], "response": response})


@app.route('/unlock', methods=['POST'])
def unlock():
    response = send_command('$X')
    return jsonify({"sent": "$X", "response": response})


@app.route('/home', methods=['POST'])
def home():
    response = send_command('$H')
    return jsonify({"sent": "$H", "response": response})


@app.route('/settings', methods=['GET'])
def settings():
    response = send_command('$$')
    return jsonify({"sent": "$$", "response": response})


@app.route('/status', methods=['GET'])
def status():
    response = get_status_line()
    return jsonify({"sent": "?", "response": response})


@app.route('/position', methods=['GET'])
def position():
    """Return parsed GRBL state and XYZ position"""
    status_line = get_status_line()
    parsed = parse_position(status_line)
    return jsonify(parsed)


@app.route('/sleep', methods=['POST'])
def sleep():
    """Put GRBL into low-power sleep mode"""
    response = send_command('$SLP')
    return jsonify({"sent": "$SLP", "response": response})


@app.route('/reset', methods=['POST'])
def reset():
    """Soft reset GRBL (Ctrl-X)"""
    global grbl
    if not grbl:
        return jsonify({"error": "Not connected"}), 500

    try:
        grbl.write(b'\x18')  # Ctrl-X
        grbl.flush()
        time.sleep(2)
        grbl.flushInput()
        return jsonify({"sent": "Ctrl-X", "response": "GRBL reset"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/wait_until_idle', methods=['GET'])
def wait_until_idle():
    """Poll GRBL until it is truly idle or timeout"""
    timeout = float(request.args.get('timeout', 60))  # longer timeout
    poll_interval = 0.2

    start_time = time.time()
    while time.time() - start_time < timeout:
        status_line = get_status_line()
        parsed = parse_position(status_line)
        state = parsed.get("state", "")
        
        # If Idle, return immediately
        if state == "Idle":
            pos = parsed.get("WPos", parsed.get("MPos", {}))
            human_pos = {axis: round(value, 3) for axis, value in pos.items()}
            return jsonify({"status": "Idle", "position": human_pos})
        
        # Optional: also check if homing finished
        if state in ["Homing", "Run"]:  
            # Check WPos or MPos to see if machine is at target?
            pass

        time.sleep(poll_interval)

    return jsonify({"status": "Timeout", "message": "Still not idle after timeout"}), 408




@app.route('/jog', methods=['POST'])
def jog():
    """
    Jog mode: move incrementally or to absolute positions
    Example JSON:
      { "x": 10, "y": 0, "z": 0, "f": 500, "relative": true }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    x = data.get('x', 0)
    y = data.get('y', 0)
    z = data.get('z', 0)
    f = data.get('f', 200)
    relative = data.get('relative', True)

    mode = "G91" if relative else "G90"
    # Always in mm (G21)
    jog_cmd = f"$J={mode} G21 X{x} Y{y} Z{z} F{f}"

    response = send_command(jog_cmd)
    return jsonify({"sent": jog_cmd, "response": response})


@app.route('/')
def index():
    return "✅ GRBL Flask server ready with jog, wait, sleep, reset, position, etc!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
