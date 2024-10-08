import numpy as np
import cv2 as cv

cap = cv.VideoCapture(2)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Get the dimensions of the frame
    height, width, _ = frame.shape

    # Calculate the center of the frame
    center_y, center_x = height // 2, width // 2

    for i in range(center_y - 3, center_y + 4):
        for j in range(center_x - 3, center_x + 4):
            frame[i, j] = [0, 255, 0]  # BGR format for green

    # Our operations on the frame come here
    # gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Display the resulting frame
    cv.imshow("frame", frame)
    if cv.waitKey(1) == ord("q"):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
