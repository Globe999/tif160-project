import cv2
import numpy as np
from dataclasses import dataclass
from scipy import ndimage as ndi
from skimage import feature
from typing import List


@dataclass
class CameraDetection:
    shape: str
    x: float
    y: float
    z: float
    size: int
    color: str


# image_path = r"D:\Hiomanoid Robots\Project\final\main\vision\test1.jpg"
# frame = cv2.imread(image_path)

video_path = r"D:\Hiomanoid Robots\Project\final\main\vision\output3.mp4"  # Make sure the path is correct for your video file

# Open a connection to the camera (0 is usually the default camera)

results = []


cap = cv2.VideoCapture(2)
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if frame is None:
        print("Error: Could not open image.")
    else:
        # Apply median filter to reduce noise
        median_frame = cv2.GaussianBlur(frame, (5, 5), 0)

        # Convert the frame to HSV color space for color-based foreground masking
        # and Define color ranges for white, red, blue, and green
        hsv = cv2.cvtColor(median_frame, cv2.COLOR_BGR2HSV)
        color_ranges = {
            "white": ((0, 0, 200), (180, 25, 255)),
            "red": ((0, 100, 80), (20, 255, 255)),
            "blue": ((100, 150, 70), (140, 255, 255)),
            "green": ((40, 50, 50), (90, 255, 255)),
        }

        mask_bright = cv2.inRange(hsv, (0, 0, 140), (180, 255, 255))

        masks = {}
        for color, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, lower, upper)
            if color != "white":  # Apply brightness filter to all non-white
                mask = cv2.bitwise_and(mask, mask_bright)
            masks[color] = mask
            cv2.imshow(f"{color.capitalize()} Mask", mask)

        # Create color masks
        # masks = {}
        # for color, (lower, upper) in color_ranges.items():
        #     mask = cv2.inRange(hsv, lower, upper)
        #     masks[color] = mask
        #     # Display each color mask in a separate window
        #     cv2.imshow(f"{color.capitalize()} Mask", mask)
        #  Combine red masks for full red detection
        # masks['red'] = cv2.bitwise_or(masks['red1'], masks['red2'])

        # Sharpen red mask specifically
        kernel_sharpening = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

        masks["red"] = cv2.filter2D(masks["red"], -1, kernel_sharpening)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        # Define kernels for morphological operations
        # kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        # kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))

        # Reduce noise with morphological operations
        for color, mask in masks.items():
            cv2.imshow(f"{color} Mask", mask)

            # Opening to remove small noise
            masks[color] = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
            # Closing to fill small holes in the object
            masks[color] = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            # Visualize each color mask
            cv2.imshow(f"{color} Mask", masks[color])

        for color, mask in masks.items():
            cv2.imshow(f"{color} Mask", mask)  # Visualize each mask

        # Combine all masks to create a foreground mask
        combined_mask = np.zeros_like(masks["white"])
        for color in ["white", "red", "blue", "green"]:
            combined_mask = cv2.bitwise_or(combined_mask, masks[color])

            cv2.imshow(
                "Combined Mask", combined_mask
            )  # Add this after combining all color masks

        # Apply the mask to the frame to remove the background
        foreground = cv2.bitwise_and(frame, frame, mask=combined_mask)

        # Apply Canny edge detection to the foreground
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        im_noisy = ndi.gaussian_filter(gray_image, 4)
        edges = feature.canny(im_noisy, sigma=3)
        edges_display = (edges * 255).astype(np.uint8)
        cv2.imshow("Canny Edges", edges_display)

        # Find contours in the Canny edge-detected image
        canny_contours, _ = cv2.findContours(
            edges_display, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Draw the Canny contours (on the color foreground)
        for contour in canny_contours:
            if cv2.contourArea(contour) > 2000:  # Filter by area to avoid small noise
                x, y, w, h = cv2.boundingRect(contour)

                # Approximate the contour to reduce the number of vertices
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                vertices = len(approx)

                # Shape classification based on the contour vertices
                shape = "Unknown"
                if vertices == 6:
                    shape = "Hexagon"
                elif vertices == 4:
                    aspect_ratio = float(w) / h
                    shape = "Cube" if 0.9 < aspect_ratio < 1.2 else "Rectangle"
                elif vertices > 0:
                    area = cv2.contourArea(contour)
                    perimeter = cv2.arcLength(contour, True)
                    circularity = (4 * np.pi * area) / (perimeter**2)
                    if circularity > 0.8:
                        shape = "Cylinder"
                    else:
                        shape = "Star Prism"
                else:
                    if vertices > 8:
                        shape = "Star Prism"

                # Draw the contour on the color foreground (in blue) and label it
                cv2.drawContours(
                    foreground, [contour], -1, (255, 0, 0), 2
                )  # Blue color for Canny contours
                cv2.putText(
                    foreground,
                    f"{shape}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                )
                entry = CameraDetection(
                    shape=shape, x=x + w / 2, y=y + h / 2, z=0, size=w * h, color=color
                )
                results.append(entry)
        cv2.imshow("Foreground with Canny Contours", foreground)

        # entry = CameraDetection(
        #     shape=shape,
        #     x=x + w / 2,
        #     y=y + h / 2,
        #     z=0,
        #     size=w * h,
        #     color=color,
        # )
        # results.append(entry)
        # Display the result
        cv2.imshow("Detected Shapes", foreground)
        print(results)
        results = []
        if cv2.waitKey(100) & 0xFF == ord("q"):
            pass

cv2.destroyAllWindows()
