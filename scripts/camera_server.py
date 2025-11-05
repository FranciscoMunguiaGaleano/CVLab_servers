from flask import Flask, Response, jsonify
import cv2
import threading

app = Flask(__name__)

# Open the default camera
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise RuntimeError("⚠️ Could not open camera")

# Global variable to hold the latest frame
latest_frame = None
lock = threading.Lock()

def capture_frames():
    """Background thread to continuously read frames from camera"""
    global latest_frame
    while True:
        success, frame = camera.read()
        if success:
            with lock:
                latest_frame = frame

# Start the background thread
threading.Thread(target=capture_frames, daemon=True).start()

def get_frame():
    """Return the latest frame as JPEG bytes"""
    global latest_frame
    with lock:
        if latest_frame is None:
            raise RuntimeError("⚠️ No frame captured yet")
        _, jpeg = cv2.imencode('.jpg', latest_frame)
        return jpeg.tobytes()

@app.route('/')
def index():
    return "✅ Camera Flask server running — use /capture to get an image"

@app.route('/capture', methods=['GET'])
def capture():
    """Capture and return latest frame as JPEG"""
    try:
        frame = get_frame()
        return Response(frame, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    ok = camera.isOpened()
    return jsonify({"camera_ready": ok})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True, use_reloader=False)
