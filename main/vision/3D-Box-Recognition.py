import cv2
import numpy as np

video_path = r'D:\Hiomanoid Robots\Project\final\tif160-project\main\vision\Test.mp4'
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open camera.")
else:
    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            print("Error: Failed to capture image from camera.")
            break

        # Convert the frame to HSV color space and define color ranges for white, red, blue, and green
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        color_ranges = {
            'white': ((0, 0, 200), (180, 25, 255)),
            'red1': ((0, 120, 70), (10, 255, 255)),
            'red2': ((170, 120, 70), (180, 255, 255)),
            'blue': ((100, 150, 0), (140, 255, 255)),
            'green': ((40, 50, 50), (90, 255, 255))
        }

        # Create masks for each color
        masks = {}
        for color, (lower, upper) in color_ranges.items():
            masks[color] = cv2.inRange(hsv, lower, upper)

        # Combine red masks for full red detection
        masks['red'] = cv2.bitwise_or(masks['red1'], masks['red2'])

        # Define kernels for morphological operations
        kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

        # Reduce noise with morphological operations
        for color, mask in masks.items():
            # Opening to remove small noise
            masks[color] = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open, iterations=4)
            # Closing to fill small holes in the object
            masks[color] = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close, iterations=4)
            # Apply median blur for smoothing

        # Combine all masks to create a foreground mask
        combined_mask = np.zeros_like(masks['white'])
        for color in ['white', 'red', 'blue', 'green']:
            combined_mask = cv2.bitwise_or(combined_mask, masks[color])

        # Apply the background mask to the frame to remove the background
        foreground = cv2.bitwise_and(frame, frame, mask=combined_mask)

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
                if cv2.contourArea(contour) > 1000:  
                    # Get the bounding box coordinates
                    x, y, w, h = cv2.boundingRect(contour)
                    # Draw a rectangle around the detected object
                    cv2.rectangle(foreground, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Get the center of the bounding box
                    x_center = x + w // 2
                    y_center = y + h // 2

                    # Detect shape based on contour approximation
                    shape = "unknown"
                    epsilon = 0.02 * cv2.arcLength(contour, True)  # Fine-tuning epsilon
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    vertices = len(approx)

                    # Classify the shape based on the number of vertices and angles
                    if vertices == 10:
                        shape = "Star Prism"
                    elif vertices == 6:
                        shape = "Hexagon"
                    elif vertices == 4:
                        # Check if the shape is a square or rectangle (cube in 2D)
                        aspect_ratio = float(w) / h
                        if 0.8 <= aspect_ratio <= 1.2:
                            shape = "Cube"
                    elif vertices > 8:
                        # Check for convexity defects to identify stars
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        area = cv2.contourArea(contour)
                        if hull_area > 0:
                            solidity = float(area) / hull_area
                            if solidity < 0.9:
                                shape = "Star Prism"
                    elif vertices > 12:
                        # Check for circularity to detect cylinder
                        area = cv2.contourArea(contour)
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter != 0:
                            circularity = 4 * np.pi * (area / (perimeter ** 2))
                            if circularity > 0.8:
                                shape = "Cylinder"
                            else:
                                shape = "Circle"
                    else:
                        shape = "Polygon"

                    # Put text on the frame indicating the color and shape
                    cv2.putText(foreground, f"{color} {shape}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Store detected object data
                    detected_objects.append({
                        'color': color,
                        'shape': shape,
                        'coordinates': (x_center, y_center),
                        'bounding_box': (x, y, w, h)
                    })

        # Display the original frame with detections
        cv2.imshow("Detected Shapes", foreground)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()