from flask import Flask, jsonify
import os
import platform
import subprocess

app = Flask(__name__)

def is_linux():
    return platform.system() == "Linux"

def is_windows():
    return platform.system() == "Windows"

@app.route('/')
def index():
    return "✅ Flask control server running. Use /shutdown or /reboot endpoints."

@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        if is_windows():
            subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        elif is_linux():
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        else:
            return jsonify({"error": "Unsupported OS"}), 400
        return jsonify({"status": "Shutting down"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reboot', methods=['POST'])
def reboot():
    try:
        if is_windows():
            subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
        elif is_linux():
            subprocess.run(["sudo", "reboot"], check=True)
        else:
            return jsonify({"error": "Unsupported OS"}), 400
        return jsonify({"status": "Rebooting"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Only bind to localhost for safety
    app.run(host='localhost', port=5003)
