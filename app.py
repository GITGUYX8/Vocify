from flask import Flask, render_template, request, send_from_directory
import os
import cv2
import time

app = Flask(__name__, static_folder='static', template_folder='templates')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/camera')
def camera_page():
    return render_template('controller.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    file = request.files['file']
    file.save(os.path.join(UPLOAD_FOLDER, 'received_audio.webm'))
    return 'Uploaded'

@app.route('/capture', methods=['POST'])
def capture_photo():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap = cv2.VideoCapture(0)

# Try these settings (values range from 0.0 to 1.0 or 0 to 255 depending on camera)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.6)
    cap.set(cv2.CAP_PROP_CONTRAST, 0.6)
    cap.set(cv2.CAP_PROP_EXPOSURE, -4)  # Lower values = brighter (can vary by camera)

    cap.release()
    if ret:
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'captured_photo.jpg'), frame)
        return 'Photo captured'
    return 'Failed to capture photo'

@app.route('/record', methods=['POST'])
def record_video():
    cap = cv2.VideoCapture(0)
    out_path = os.path.join(UPLOAD_FOLDER, 'captured_video.mp4v')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(out_path, fourcc, 20.0, (640, 480))
    start = time.time()

    while int(time.time() - start) < 5:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    return ' 5-second video recorded'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
