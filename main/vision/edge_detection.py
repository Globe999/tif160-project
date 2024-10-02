import cv2
import imutils
from imutils import contours
import numpy as np
import random


class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, frame):
        # Converting the frame to Gray Scale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Removing Gaussian Noise
        blur = cv2.GaussianBlur(gray, (3, 3), 0)

        # Applying inverse binary due to white background and adapting thresholding for better results
        thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 205, 1
        )

        # Finding contours with simple retrieval (no hierarchy) and simple/compressed end points
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # An empty list to store filtered contours
        filtered = []

        # Looping over all found contours
        for c in contours:
            # If it has significant area, add to list
            if cv2.contourArea(c) < 1000:
                continue
            filtered.append(c)

        # Initialize an equally shaped image
        objects = np.zeros([frame.shape[0], frame.shape[1], 3], "uint8")

        # Looping over filtered contours
        for c in filtered:
            # Select a random color to draw the contour
            col = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            # Draw the contour on the image with above color
            cv2.drawContours(objects, [c], -1, col, -1)
            # Fetch contour area
            area = cv2.contourArea(c)
            # Fetch the perimeter
            p = cv2.arcLength(c, True)
            print(area, p)

        return objects


def main():
    # Open a connection to the video feed (0 is the default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video feed.")
        return

    shape_detector = ShapeDetector()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        orig = frame.copy()
        # Display the resulting frame
        cv2.imshow("Video Feed", frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edgeMap = imutils.auto_canny(gray)
        # cv2.imshow("Original", logo)

        cnts = cv2.findContours(
            edgeMap.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cnts = imutils.grab_contours(cnts)

        # loop over the (unsorted) contours and label them
        for i, c in enumerate(cnts):
            if cv2.contourArea(c) == 0:
                continue
            orig = contours.label_contour(orig, c, i, color=(240, 0, 159))

        # show the original image
        cv2.imshow("Original", orig)

        # loop over the sorting methods
        for method in (
            "left-to-right",
            "right-to-left",
            "top-to-bottom",
            "bottom-to-top",
        ):
            # sort the contours
            (cnts, boundingBoxes) = contours.sort_contours(cnts, method=method)
            clone = frame.copy()

            # loop over the sorted contours and label them
            for i, c in enumerate(cnts):
                if cv2.contourArea(c) == 0:
                    continue
                sortedImage = contours.label_contour(clone, c, i, color=(240, 0, 159))

            # show the sorted contour image
            cv2.imshow(method, sortedImage)

        cv2.imshow("Automatic Edge Map", edgeMap)

        # Detect shapes in the frame
        objects = shape_detector.detect(frame)
        cv2.imshow("Detected Shapes", objects)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
