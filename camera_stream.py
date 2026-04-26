#!/usr/bin/env python3
import cv2
import time
import threading
from flask import Flask, Response

app = Flask(__name__)

camera_lock = threading.Lock()
camera = None

def init_camera():
    global camera
    while True:
        with camera_lock:
            cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                camera = cap
                print("✅ Camera ouverte")
                return
        print("⚠️ Camera non disponible, retry dans 2s...")
        time.sleep(2)

def generate():
    global camera
    while True:
        with camera_lock:
            if camera is None or not camera.isOpened():
                time.sleep(0.1)
                continue
            ret, frame = camera.read()
        
        if not ret:
            print("⚠️ Frame perdue, reconnexion...")
            with camera_lock:
                if camera:
                    camera.release()
                camera = None
            init_camera()
            continue

        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               jpeg.tobytes() + b'\r\n')

@app.route('/stream')
def stream():
    return Response(
        generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    init_camera()
    app.run(host='0.0.0.0', port=8080, threaded=True)
