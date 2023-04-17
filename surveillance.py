import cv2
import time
import datetime
from picamera2 import Picamera2

# Configure Camera
piCam = Picamera2() # Create picamera object
piCam.preview_configuration.main.size=(640,480) # Setting up camera configuration
piCam.preview_configuration.controls.FrameRate = 20
piCam.preview_configuration.main.format="RGB888"
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start() # Start camera

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml") # Add facial detection
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml") # Add full body detection

detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 10

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

while True:
    frame = piCam.capture_array() # Grab frame
    
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) # Convert image to grayscale
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    bodies = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) + len(bodies) > 0: # Face or body is in frame
        if detection: # If detecting something, keep recording
            timer_started = False
        else: # IF not recording, start a new video
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            out = cv2.VideoWriter(f"{current_time}.mp4", fourcc, 20.0, (640, 480))
            print("Started recording.")
    elif detection: # No longer detecting a face or body
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                print("Stopped recording.")
        else:
            timer_started = True
            detection_stopped_time = time.time()
    
    if detection:    
        out.write(frame) # Write frame to video if face or body is in frame
    
    for (x, y, width, height) in faces:
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3) # Draw rectangle around face in frame
    
    cv2.imshow("piCam", frame) # Display frame
    
    if cv2.waitKey(1) == ord('q'): # Press q to terminate
        break

out.release()
cv2.destroyAllWindows()