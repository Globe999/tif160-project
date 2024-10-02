import cv2
import numpy as np

# Lower bounds for colors in HSV
lower = {
    "red": ([166, 84, 141]),
    "green": ([50, 50, 120]),
    "blue": ([97, 100, 117]),
    "white": ([0, 0, 200]),
}

# Upper bounds for colors in HSV
upper = {
    "red": ([186, 255, 255]),
    "green": ([70, 255, 255]),
    "blue": ([117, 255, 255]),
    "white": ([180, 30, 255]),
}

# Color in BGR
colors = {
    "red": (0, 0, 255),
    "green": (0, 255, 0),
    "blue": (255, 0, 0),
    "white": (255, 255, 255),
}

# Start video capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()  # Read frames from video
    if not ret:
        break  # Exit loop if reading is not successful

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)  # Gaussian blur to reduce noise
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)  # Convert to HSV format

    combined_mask = np.zeros_like(frame[:, :, 0])  # Mask Generation

    mlist = []  # Masks
    clist = []  # Contours
    ks = []  # Color Keys

    for key in lower.keys():
        L_limit = np.array(lower[key])  # Lower limit for the color
        U_limit = np.array(upper[key])  # Upper limit for the color

        mask = cv2.inRange(hsv, L_limit, U_limit)  # Create a binary mask
        mask = cv2.morphologyEx(
            mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)
        )  # Remove noise
        mask = cv2.dilate(
            mask, np.ones((3, 3), np.uint8), iterations=1
        )  # Dilate the mask

        combined_mask = cv2.bitwise_or(
            combined_mask, mask
        )  # Combine masks of all colors

        cnts, _ = cv2.findContours(
            mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if cnts:
            clist.append(cnts[-1])  # Get the largest contour
            ks.append(key)  # Store the color key

    # Draw contours and labels in the original frame
    for i, cnt in enumerate(clist):
        approx = cv2.approxPolyDP(
            cnt, 0.02 * cv2.arcLength(cnt, True), True
        )  # Approximate the contour shape

        # Draw the contour on the frame
        cv2.drawContours(
            frame, [cnt], -1, colors[ks[i]], 2
        )  # Draw the contour with the color corresponding to the detected shape

        # Calculate the area and perimeter for circularity check
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        circularity = (4 * np.pi * area) / (perimeter**2) if perimeter > 0 else 0

        # Calculate the aspect ratio
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h if h > 0 else 0

        # Check for shape
        # Triangle
        # if len(approx) == 3:
        #     cv2.putText(frame, ks[i] + " Triangle", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors[ks[i]], 2)

        # Square
        if len(approx) == 4:
            x2, y2 = (
                approx.ravel()[2],
                approx.ravel()[3],
            )  # x2, y2 coordinates from approx
            x4, y4 = (
                approx.ravel()[6],
                approx.ravel()[7],
            )  # x4, y4 coordinates from approx
            side1 = abs(x2 - x)
            side2 = abs(y4 - y)

            if abs(side1 - side2) <= 2:  # Check if the sides are approximately equal
                cv2.putText(
                    frame,
                    ks[i] + " Square",
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    colors[ks[i]],
                    2,
                )

        # Hexagon
        elif len(approx) == 6:  # 6 sides
            if (
                circularity < 0.8 and aspect_ratio > 0.8
            ):  # Prevent confusion with circles
                cv2.putText(
                    frame,
                    ks[i] + " Hexagon",
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    colors[ks[i]],
                    2,
                )

        # Star
        elif len(approx) == 12:  # 12 sides
            cv2.putText(
                frame,
                ks[i] + " Star",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                colors[ks[i]],
                2,
            )

        # Circle
        elif circularity >= 0.8 and len(approx) > 8:
            cv2.putText(
                frame,
                ks[i] + " Circle",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                colors[ks[i]],
                2,
            )

    # Display live video with classifications
    cv2.imshow("Frame", frame)

    # Display combined binary mask with all colors
    cv2.imshow("Combined Mask", combined_mask)

    # ESC key to exit
    if cv2.waitKey(1) == 27:
        break

# Close all Windows
cap.release()
cv2.destroyAllWindows()
