import cv2
import time

def capture_photo():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("uploads/captured_photo.jpg", frame)
    cam.release()

def record_video():
    cam = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('uploads/captured_video.mp4v', fourcc, 20.0, (640, 480))
    start_time = time.time()
    while time.time() - start_time < 5:
        ret, frame = cam.read()
        if ret:
            out.write(frame)
    cam.release()
    out.release()
