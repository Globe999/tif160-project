import time
import numpy as np
import cv2 as cv

# Open the camera
cap = cv.VideoCapture(1)
if not cap.isOpened():
    print("Cannot open camera")
    exit()


today = time.strftime("%Y-%m-%d-%H-%M-%S")

# Get the width and height of the frames
frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*"mp4v")  # Codec for MP4
out = cv.VideoWriter(f"{today}.mp4", fourcc, 20.0, (frame_width, frame_height))

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Write the frame into the file 'output.mp4'
    out.write(frame)

    # Display the resulting frame
    cv.imshow("frame", frame)
    if cv.waitKey(1) == ord("q"):
        break

# When everything done, release the capture and writer
cap.release()
out.release()
cv.destroyAllWindows()
