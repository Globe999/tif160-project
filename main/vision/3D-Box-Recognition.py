
import numpy as np
import cv2

# Initialize the camera capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
else:
    while True:
        ret, frame = cap.read()

        # Check if the frame is captured correctly
        if not ret or frame is None:
            print("Error: Failed to capture image from camera.")
            break

        # Convert the frame to HSV color space and color ranges for white, red, blue, and green
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        color_ranges = {
            'white': ((0, 0, 200), (180, 25, 255)),
            'red': ((0, 120, 70), (10, 255, 255)),
            'blue': ((100, 150, 0), (140, 255, 255)),
            'green': ((40, 50, 50), (90, 255, 255))
        }

        # Create masks for each color
        masks = {}
        for color, (lower, upper) in color_ranges.items():
            masks[color] = cv2.inRange(hsv, lower, upper)

        # Define kernel for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

        # Reduce noise with erosion and dilation
        for color, mask in masks.items():
            masks[color] = cv2.erode(mask, kernel, iterations=2)
            masks[color] = cv2.dilate(masks[color], kernel, iterations=2)

        # Find contours for each color mask
        contours_data = {}
        for color, mask in masks.items():
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours_data[color] = contours

        # Process each detected contour and draw bounding boxes
        detected_objects = []
        for color, contours in contours_data.items():
            for contour in contours:
                # Filter out small contours to reduce noise
                if cv2.contourArea(contour) > 500:
                    # Get the bounding box coordinates
                    x, y, w, h = cv2.boundingRect(contour)
                    # Draw a rectangle around the detected object
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Get the center of the bounding box
                    x_center = x + w // 2
                    y_center = y + h // 2

                    # Detect shape based on contour approximation
                    shape = "unknown"  
                    epsilon = 0.04 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    vertices = len(approx)

                    # Classify the shape based on the number of vertices
                    if vertices == 4:
                        shape = "Cube"
                    elif vertices == 6:
                        shape = "hexagon"
                    elif vertices == 12:
                        shape = "Star"
                    elif vertices > 12:
                        shape = "cyloinder"

                    # Put text on the frame indicating the color and shape
                    #cv2.putText(frame, f"{color} {shape}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Store detected object data
                    detected_objects.append({
                        'color': color,
                        'shape': shape,
                        'coordinates': (x_center, y_center),
                        'bounding_box': (x, y, w, h)
                    })

        # Display the original frame with detections
        cv2.imshow("Detected Shapes", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()




