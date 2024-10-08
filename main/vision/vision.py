from dataclasses import dataclass
from typing import List

import cv2
import numpy as np


@dataclass
class CameraDetection:
    shape: str
    x: float
    y: float
    z: float
    size: int
    color: str


class Camera:

    def __init__(self) -> None:
        self.cap = cv2.VideoCapture(2)
        self.color_ranges = {
            "white": ((0, 0, 200), (180, 25, 255)),
            "red": ((0, 100, 80), (10, 255, 255)),
            #'red2': ((170, 120, 70), (180, 255, 255)),
            "blue": ((100, 150, 70), (140, 255, 255)),
            "green": ((40, 50, 50), (90, 255, 255)),
        }

    def grab_frame(self):
        _, frame = self.cap.read()

        if frame is None:
            raise Exception("Error: Could not open image.")

        return frame

    def get_detected_objects(self, frame=None) -> List[CameraDetection]:
        if frame is None:
            frame = self.grab_frame()

        results = []
        median_frame = cv2.GaussianBlur(frame, (5, 5), 0)

        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(median_frame, cv2.COLOR_BGR2HSV)

        mask_bright = cv2.inRange(hsv, (0, 0, 140), (180, 255, 255))

        # Create masks for each color
        masks = {}
        for color, (lower, upper) in self.color_ranges.items():
            mask = cv2.inRange(hsv, lower, upper)
            if color != "white":  # Apply brightness filter to all non-white
                mask = cv2.bitwise_and(mask, mask_bright)
            masks[color] = mask

        # Sharpen red mask specifically
        kernel_sharpening = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        masks["red"] = cv2.filter2D(masks["red"], -1, kernel_sharpening)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        contours_data = {}
        for color, mask in masks.items():
            # Apply dilation and erosion
            dilated = cv2.dilate(mask, kernel, iterations=2)
            eroded = cv2.erode(dilated, kernel, iterations=2)

            # Find contours
            contours, _ = cv2.findContours(
                eroded, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
            )

            filtered_contours = []
            for contour in contours:
                approx_contour = cv2.approxPolyDP(contour, 10, True)
                hull = cv2.convexHull(approx_contour)

                if 3 <= len(hull) <= 10:  # Example range for minEdges and maxEdges
                    filtered_contours.append(hull)

            contours_data[color] = filtered_contours

        combined_mask = np.zeros_like(masks["white"])

        for key in self.color_ranges.keys():
            combined_mask = cv2.bitwise_or(combined_mask, masks[key])

        foreground = cv2.bitwise_and(frame, frame, mask=combined_mask)

        # Apply Canny edge detection to the foreground
        edges = cv2.Canny(frame, 500, 500, apertureSize=3, L2gradient=True)

        cv2.imshow("Edges", edges)

        for color, contours in contours_data.items():

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)

        # for color, contours in contours_data.items():
        #     for contour in contours:
        #         if cv2.contourArea(contour) > 2000:
        #             x, y, w, h = cv2.boundingRect(contour)

        #             # Approximate the contour to reduce the number of vertices
        #             epsilon = 0.04 * cv2.arcLength(contour, True)
        #             approx = cv2.approxPolyDP(contour, epsilon, True)
        #             vertices = len(approx)

        #             # Shape classification
        #             shape = "unknown"
        #             if vertices == 6:
        #                 shape = "hexagon"
        #             elif vertices == 4:
        #                 aspect_ratio = float(w) / h
        #                 shape = "cube" if 0.9 < aspect_ratio < 1.2 else "rectangle"
        #             elif vertices > 20:
        #                 area = cv2.contourArea(contour)
        #                 perimeter = cv2.arcLength(contour, True)
        #                 circularity = (4 * np.pi * area) / (perimeter**2)
        #                 if circularity > 0.8:  # Adjust circularity threshold as needed
        #                     shape = "cylinder"
        #                 else:
        #                     shape = "star"
        #             else:
        #                 if vertices > 8:
        #                     shape = "star"  # Check for irregular star-like shapes

        #             # Draw the shape and label it
        #             cv2.drawContours(foreground, [contour], -1, (0, 255, 0), 2)
        #             cv2.putText(
        #                 foreground,
        #                 f"{color} {shape}",
        #                 (x, y - 10),
        #                 cv2.FONT_HERSHEY_SIMPLEX,
        #                 0.5,
        #                 (255, 255, 255),
        #                 2,
        #             )
        #             entry = CameraDetection(
        #                 shape=shape,
        #                 x=x + w / 2,
        #                 y=y + h / 2,
        #                 z=0,
        #                 size=w * h,
        #                 color=color,
        #             )
        #             results.append(entry)
        cv2.imshow("Foreground", foreground)
        if cv2.waitKey(100000) & 0xFF == ord("q"):
            pass
        return results

    def get_position(self, pixel_pos_x, pixel_pos_y, camera_angle):

        mid_y_pos = 0.132
        length_per_pixel_y = 0.071 / 240
        length_per_pixel_x = 0.098 / 320
        x_pos = np.sin(camera_angle) * mid_y_pos + pixel_pos_x * length_per_pixel_x
        y_pos = np.cos(camera_angle) * mid_y_pos + pixel_pos_y * length_per_pixel_y

        return x_pos, y_pos


cam = Camera()
x, y = cam.get_position(0, 0, np.pi / 4)

print(x, y)
