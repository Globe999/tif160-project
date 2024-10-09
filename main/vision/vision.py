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
    global_x: float
    global_y: float
    global_z: float
    size: int
    color: str
    angle: int


class Camera:
    def __init__(self, index=2) -> None:
        self.index = index
        self.width = 640
        self.height = 480

    def grab_frame(self):
        cap = cv2.VideoCapture(self.index)
        ret, frame = cap.read()
        if not ret or frame is None:
            raise Exception("Error: Could not open image.")
        return frame

    def get_detected_objects(self, angle: int, frame=None) -> List[CameraDetection]:
        if frame is None:
            frame = self.grab_frame()

        results = []
        # Capture frame-by-frame
        if frame is None:
            print("Error: Could not open image.")
        else:
            # Apply median filter to reduce noise
            median_frame = cv2.GaussianBlur(frame, (5, 5), 0)

            # Convert the frame to HSV color space
            hsv = cv2.cvtColor(median_frame, cv2.COLOR_BGR2HSV)

            # Define color ranges for white, red, blue, and green
            color_ranges = {
                "white": ((0, 0, 200), (180, 25, 255)),
                "red": ((0, 100, 80), (10, 255, 255)),
                #'red2': ((170, 120, 70), (180, 255, 255)),
                "blue": ((100, 150, 70), (140, 255, 255)),
                "green": ((40, 50, 50), (90, 255, 255)),
            }

            mask_bright = cv2.inRange(hsv, (0, 0, 140), (180, 255, 255))

            # Create masks for each color
            masks = {}
            for color, (lower, upper) in color_ranges.items():
                mask = cv2.inRange(hsv, lower, upper)
                if color != "white":  # Apply brightness filter to all non-white
                    mask = cv2.bitwise_and(mask, mask_bright)
                masks[color] = mask
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
                # Opening to remove small noise
                masks[color] = cv2.morphologyEx(
                    mask, cv2.MORPH_OPEN, kernel, iterations=2
                )
                # Closing to fill small holes in the object
                masks[color] = cv2.morphologyEx(
                    mask, cv2.MORPH_CLOSE, kernel, iterations=2
                )

            # Combine all masks to create a foreground mask
            combined_mask = np.zeros_like(masks["white"])
            for color in ["white", "red", "blue", "green"]:
                combined_mask = cv2.bitwise_or(combined_mask, masks[color])
            # Apply the mask to the frame to remove the background
            foreground = cv2.bitwise_and(frame, frame, mask=combined_mask)

            # Apply Canny edge detection to the foreground
            edges = cv2.Canny(foreground, 120, 200)

            # Find contours for each color mask
            contours_data = {}
            for color, mask in masks.items():
                contours, _ = cv2.findContours(
                    mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                contours_data[color] = contours

            # Process and draw contours
            for color, contours in contours_data.items():
                for contour in contours:
                    if cv2.contourArea(contour) > 2000:
                        x, y, w, h = cv2.boundingRect(contour)

                        x = x / self.width - 0.5
                        y = -1 * (y / self.height - 0.5)
                        w = w / self.width
                        h = h / self.height

                        # Approximate the contour to reduce the number of vertices
                        epsilon = 0.04 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        vertices = len(approx)

                        # Shape classification
                        shape = "Unknown"
                        if vertices == 6:
                            shape = "Hexagon"
                        elif vertices == 4:
                            aspect_ratio = float(w) / h
                            shape = "Cube" if 0.9 < aspect_ratio < 1.2 else "Rectangle"
                        elif vertices > 20:
                            area = cv2.contourArea(contour)
                            perimeter = cv2.arcLength(contour, True)
                            circularity = (4 * np.pi * area) / (perimeter**2)
                            if (
                                circularity > 0.8
                            ):  # Adjust circularity threshold as needed
                                shape = "Cylinder"
                            else:
                                shape = "Star Prism"
                        else:
                            if vertices > 8:
                                shape = (
                                    "Star Prism"  # Check for irregular star-like shapes
                                )
                        entry = CameraDetection(
                            shape=shape,
                            x=x + w / 2,
                            y=y - h / 2,
                            z=0,
                            size=w * h,
                            color=color,
                            global_x=0,
                            global_y=0,
                            global_z=0,
                            angle=angle,
                        )
                        results.append(entry)
            return self.get_global_position(results, camera_angle=angle)

    def get_global_position(self, objects: List[CameraDetection], camera_angle: int):

        length_per_pixel_x = 0.071 * 2
        length_per_pixel_y = 0.098 * 2
        mid_x_pos = 0.132
        # length_per_pixel_x = 0.1 * 2
        # length_per_pixel_y = 0.15 * 2
        for object in objects:
            object.global_y = np.sin(np.deg2rad(camera_angle)) * mid_x_pos + (
                object.x * length_per_pixel_x * np.cos(np.deg2rad(camera_angle)) + object.y * length_per_pixel_y * np.sin(np.deg2rad(camera_angle))
            )
            object.global_x = (
                np.cos(np.deg2rad(camera_angle)) * mid_x_pos
                + object.y * length_per_pixel_y * np.cos(np.deg2rad(camera_angle)) - object.x * length_per_pixel_x * np.sin(np.deg2rad(camera_angle))
            )

        return objects
    
    def merge_objects(self,objects:List[CameraDetection],threshold):
        
        merged_points = []

        while objects:
            point = objects.pop(0)
            cluster = [point]
            
            for other_point in objects:
                dist = np.sqrt((point.x - point.x) ** 2 + (other_point.y - other_point.y) ** 2)
                if ((dist <= threshold) and (point.color == other_point.color) and (point.shape == other_point.shape)):
                    cluster.append(other_point)
                    objects.remove(other_point)

            # Merge all points in the cluster into a single point (average of the cluster)
            if len(cluster) > 1:
                avg_x = sum(p.x for p in cluster) / len(cluster)
                avg_y = sum(p.y for p in cluster) / len(cluster)
                cluster[0].x = avg_x
                cluster[0].y = avg_y
                merged_points.append(cluster[0])
            else:
                merged_points.append(point)
        
        return merged_points
            

# cam = Camera()
# x, y = cam.get_position(0, 0, np.pi / 4)

# print(x, y)
