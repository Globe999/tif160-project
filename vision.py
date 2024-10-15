from dataclasses import dataclass
from pathlib import Path
import queue
import threading
import time
from typing import List
import cvzone
import cv2
import math
import numpy as np
from scipy import ndimage as ndi
from skimage import feature
from ultralytics import YOLO


classNames = [
    "red hexagon",
    "red cube",
    "red star",
    "red cylinder",
    "yellow hexagon",
    "yellow cube",
    "yellow star",
    "yellow cylinder",
    "green hexagon",
    "green cube",
    "green star",
    "green cylinder",
    "blue hexagon",
    "blue cube",
    "blue star",
    "blue cylinder",
    "white hexagon",
    "white cube",
    "white star",
    "white cylinder",
]


@dataclass
class CameraDetection:
    shape: str
    confidence: float
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
        self.model = YOLO(
            Path().cwd() / "neural_network" / "weights" / "best_100_epochs.pt"
        )
        self.frame_queue = queue.Queue(maxsize=10)
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def _capture_frames(self):
        cap = cv2.VideoCapture(self.index)
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Error: Could not open image.")
                continue
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            time.sleep(0.01)  # Add a small delay to avoid busy-waiting

    def grab_frame(self):
        retries = 20
        while retries > 0:
            if not self.frame_queue.empty():
                return self.frame_queue.get()
            retries -= 1
            time.sleep(0.1)  # Wait for a short time before retrying
        raise Exception("Error: No frames available.")

    def run_object_detection(self, frame=None):
        if frame is None:
            frame = self.grab_frame()
        results = self.model(
            frame,
            stream=False,
        )

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1
                cvzone.cornerRect(frame, (x1, y1, w, h))

                conf = math.ceil((box.conf[0] * 100)) / 100

                cls = box.cls[0]
                name = classNames[int(cls)]

                cvzone.putTextRect(
                    frame,
                    f"{name} " f"{conf}",
                    (max(0, x1), max(35, y1)),
                    scale=0.5,
                    thickness=1,
                )
        return frame

    def get_detected_objects(self, angle: int, frame=None) -> List[CameraDetection]:
        if frame is None:
            frame = self.grab_frame()

        results = []
        # Apply median filter to reduce noise
        median_frame = cv2.GaussianBlur(frame, (5, 5), 0)

        # Convert the frame to HSV color space for color-based foreground masking
        # and Define color ranges for white, red, blue, and green
        hsv = cv2.cvtColor(median_frame, cv2.COLOR_BGR2HSV)
        color_ranges = {
            "white": ((0, 0, 200), (180, 20, 255)),
            "red": ((0, 90, 80), (180, 255, 255)),
            "blue": ((100, 120, 70), (140, 255, 255)),
            "green": ((40, 50, 50), (90, 255, 255)),
        }

        mask_bright = cv2.inRange(hsv, (0, 0, 140), (180, 255, 255))
        masks = {}
        for color, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, lower, upper)
            if color != "white":  # Apply brightness filter to all non-white
                mask = cv2.bitwise_and(mask, mask_bright)
            masks[color] = mask
            # cv2.imshow(f"{color.capitalize()} Mask", mask)

        # Sharpen red mask specifically
        kernel_sharpening = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

        masks["red"] = cv2.filter2D(masks["red"], -1, kernel_sharpening)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        # Reduce noise with morphological operations
        for color, mask in masks.items():
            # cv2.imshow(f"{color} Mask", mask)

            # Opening to remove small noise
            masks[color] = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
            # Closing to fill small holes in the object
            masks[color] = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            # Visualize each color mask
            # cv2.imshow(f"{color} Mask", masks[color])

        # for color, mask in masks.items():
        #     cv2.imshow(f"{color} Mask", mask)  # Visualize each mask

        # Combine all masks to create a foreground mask
        combined_mask = np.zeros_like(masks["white"])
        for color in ["white", "red", "blue", "green"]:
            combined_mask = cv2.bitwise_or(combined_mask, masks[color])

            # cv2.imshow(
            #     "Combined Mask", combined_mask
            # )  # Add this after combining all color masks

        # Apply the mask to the frame to remove the background
        foreground = cv2.bitwise_and(frame, frame, mask=combined_mask)

        # Apply Canny edge detection to the foreground
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        im_noisy = ndi.gaussian_filter(gray_image, 4)
        edges = feature.canny(im_noisy, sigma=3.5)
        edges_display = (edges * 255).astype(np.uint8)
        # cv2.imshow("Canny Edges", edges_display)

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
                    shape = "hexagon"
                elif vertices == 4:
                    aspect_ratio = float(w) / h
                    shape = "cube" if 0.9 < aspect_ratio < 1.2 else "rectangle"
                elif vertices > 0:
                    area = cv2.contourArea(contour)
                    perimeter = cv2.arcLength(contour, True)
                    circularity = (4 * np.pi * area) / (perimeter**2)
                    if circularity > 0.8:
                        shape = "cylinder"
                    else:
                        shape = "star_prism"
                else:
                    if vertices > 8:
                        shape = "star_prism"

                # Detect color in the bounding box
                max_coverage = 0
                for color, mask in masks.items():
                    mask_region = mask[y : y + h, x : x + w]
                    non_zero_pixels = cv2.countNonZero(mask_region)
                    coverage = non_zero_pixels / mask_region.size
                    if coverage > max_coverage:
                        max_coverage = coverage
                        shape_color = color

                # Draw the contour on the color foreground (in blue) and label it
                cv2.drawContours(foreground, [contour], -1, (255, 0, 0), 2)
                cv2.putText(
                    foreground,
                    f"{shape_color} {shape} ",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                )

                x = x / self.width - 0.5
                y = -1 * (y / self.height - 0.5)
                w = w / self.width
                h = h / self.height
                entry = CameraDetection(
                    shape=shape,
                    x=x + w / 2,
                    y=y - h / 2,
                    z=0,
                    size=w * h,
                    color=shape_color,
                    global_x=0,
                    global_y=0,
                    global_z=0,
                    angle=angle,
                )
                results.append(entry)
        cv2.imshow("Detected Objects", foreground)

        print(f"GOT {len(results)} DETECTIONS")
        if cv2.waitKey(1) & 0xFF == ord("q"):
            pass
        return self.get_global_position(results, camera_angle=angle)

        ##### HELLO

    def get_detected_objects_from_nn(
        self, angle: int, frame=None
    ) -> List[CameraDetection]:
        frame = self.grab_frame()
        if frame is None:
            frame = self.grab_frame()

        results = self.model(frame, stream=True)
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                if box.conf[0] < 0.8:
                    continue

                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1

                cvzone.cornerRect(frame, (x1, y1, w, h))

                conf = math.ceil((box.conf[0] * 100)) / 100

                cls = box.cls[0]
                name = classNames[int(cls)]

                cvzone.putTextRect(
                    frame,
                    f"{name} " f"{conf}",
                    (max(0, x1), max(35, y1)),
                    scale=0.5,
                    thickness=1,
                )

                cls = box.cls[0]
                classification = classNames[int(cls)].split()
                color = classification[0]
                shape = classification[1]

                x = x1 / self.width - 0.5
                y = -1 * (y1 / self.height - 0.5)
                w = w / self.width
                h = h / self.height
                entry = CameraDetection(
                    shape=shape,
                    confidence=conf,
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
                detections.append(entry)
        cv2.imshow("frame", frame)
        cv2.waitKey(1)
        print(f"Angle: {angle}")

        for detection in detections:
            print(
                f"Shape: {detection.shape}, Color: {detection.color}\n x: {detection.x}, y: {detection.y}"
            )
        return self.get_global_position(detections, camera_angle=angle)

    def get_global_position(self, objects: List[CameraDetection], camera_angle: int):

        length_per_pixel_x = 0.071 * 2
        length_per_pixel_y = 0.098 * 2
        mid_x_pos = 0.132
        # length_per_pixel_x = 0.098 * 2
        # length_per_pixel_y = 0.098 * 2
        for object in objects:
            object.global_y = np.sin(np.deg2rad(camera_angle)) * mid_x_pos + (
                -1 * object.x * length_per_pixel_x * np.cos(np.deg2rad(camera_angle))
                + object.y * length_per_pixel_y * np.sin(np.deg2rad(camera_angle))
            )
            object.global_x = (
                np.cos(np.deg2rad(camera_angle)) * mid_x_pos
                + object.y * length_per_pixel_y * np.cos(np.deg2rad(camera_angle))
                + object.x * length_per_pixel_x * np.sin(np.deg2rad(camera_angle))
            )
            print(
                f"Object with shape {object.shape} at x: {object.x}, y: {object.y} and angle {camera_angle}\n has global x: {object.global_x}, global y: {object.global_y}"
            )

        return objects

    def merge_objects(
        self, camera_detections: List[CameraDetection], distance_threshold
    ):

        merged_points = []

        while camera_detections:
            point = camera_detections.pop(0)
            cluster = [point]
            idx_to_remove = []
            for idx, other_point in enumerate(camera_detections):
                dist = np.sqrt(
                    (point.global_x - other_point.global_x) ** 2
                    + (point.global_y - other_point.global_y) ** 2
                )
                if (dist <= distance_threshold) and (point.color == other_point.color):
                    cluster.append(other_point)
                    idx_to_remove.append(idx)

            # Merge all points in the cluster into a single point (average of the cluster)
            if len(cluster) > 1:
                best_shape_index = np.argmax([p.confidence for p in cluster])
                avg_x = sum(p.global_x for p in cluster) / len(cluster)
                avg_y = sum(p.global_y for p in cluster) / len(cluster)
                cluster[0].global_x = avg_x
                cluster[0].global_y = avg_y
                cluster[0].shape = cluster[best_shape_index].shape
                merged_points.append(cluster[0])
            else:
                merged_points.append(point)
            for idx in sorted(idx_to_remove, reverse=True):
                camera_detections.pop(idx)

        return merged_points


# # Capture frame-by-frame

# if frame is None:
#     print("Error: Could not open image.")
# else:
#     # Apply median filter to reduce noise
#     median_frame = cv2.GaussianBlur(frame, (5, 5), 0)

#     # Convert the frame to HSV color space
#     hsv = cv2.cvtColor(median_frame, cv2.COLOR_BGR2HSV)

#     # Define color ranges for white, red, blue, and green
#     color_ranges = {
#         "white": ((0, 0, 200), (180, 25, 255)),
#         "red": ((0, 100, 80), (10, 255, 255)),
#         #'red2': ((170, 120, 70), (180, 255, 255)),
#         "blue": ((100, 150, 70), (140, 255, 255)),
#         "green": ((40, 50, 50), (90, 255, 255)),
#     }

#     mask_bright = cv2.inRange(hsv, (0, 0, 140), (180, 255, 255))

#     # Create masks for each color
#     masks = {}
#     for color, (lower, upper) in color_ranges.items():
#         mask = cv2.inRange(hsv, lower, upper)
#         if color != "white":  # Apply brightness filter to all non-white
#             mask = cv2.bitwise_and(mask, mask_bright)
#         masks[color] = mask
#     #  Combine red masks for full red detection
#     # masks['red'] = cv2.bitwise_or(masks['red1'], masks['red2'])

#     # Sharpen red mask specifically
#     kernel_sharpening = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

#     masks["red"] = cv2.filter2D(masks["red"], -1, kernel_sharpening)
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

#     # Define kernels for morphological operations
#     # kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
#     # kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))

#     # Reduce noise with morphological operations
#     for color, mask in masks.items():
#         # Opening to remove small noise
#         masks[color] = cv2.morphologyEx(
#             mask, cv2.MORPH_OPEN, kernel, iterations=2
#         )
#         # Closing to fill small holes in the object
#         masks[color] = cv2.morphologyEx(
#             mask, cv2.MORPH_CLOSE, kernel, iterations=2
#         )

#     # Combine all masks to create a foreground mask
#     combined_mask = np.zeros_like(masks["white"])
#     for color in ["white", "red", "blue", "green"]:
#         combined_mask = cv2.bitwise_or(combined_mask, masks[color])
#     # Apply the mask to the frame to remove the background
#     foreground = cv2.bitwise_and(frame, frame, mask=combined_mask)

#     # Apply Canny edge detection to the foreground
#     edges = cv2.Canny(foreground, 120, 200)

#     # Find contours for each color mask
#     contours_data = {}
#     for color, mask in masks.items():
#         contours, _ = cv2.findContours(
#             mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
#         )
#         contours_data[color] = contours

#     # Process and draw contours
#     for color, contours in contours_data.items():
#         for contour in contours:
#             if cv2.contourArea(contour) > 2000:
#                 x, y, w, h = cv2.boundingRect(contour)

#                 x = x / self.width - 0.5
#                 y = -1 * (y / self.height - 0.5)
#                 w = w / self.width
#                 h = h / self.height

#                 # Approximate the contour to reduce the number of vertices
#                 epsilon = 0.04 * cv2.arcLength(contour, True)
#                 approx = cv2.approxPolyDP(contour, epsilon, True)
#                 vertices = len(approx)

#                 # Shape classification
#                 shape = "Unknown"
#                 if vertices == 6:
#                     shape = "Hexagon"
#                 elif vertices == 4:
#                     aspect_ratio = float(w) / h
#                     shape = "Cube" if 0.9 < aspect_ratio < 1.2 else "Rectangle"
#                 elif vertices > 20:
#                     area = cv2.contourArea(contour)
#                     perimeter = cv2.arcLength(contour, True)
#                     circularity = (4 * np.pi * area) / (perimeter**2)
#                     if (
#                         circularity > 0.8
#                     ):  # Adjust circularity threshold as needed
#                         shape = "Cylinder"
#                     else:
#                         shape = "Star Prism"
#                 else:
#                     if vertices > 8:
#                         shape = (
#                             "Star Prism"  # Check for irregular star-like shapes
#                         )
#                 entry = CameraDetection(
#                     shape=shape,
#                     x=x + w / 2,
#                     y=y - h / 2,
#                     z=0,
#                     size=w * h,
#                     color=color,
#                     global_x=0,
#                     global_y=0,
#                     global_z=0,
#                     angle=angle,
#                 )
#                 results.append(entry)


if __name__ == "__main__":
    camera = Camera()

    camera.run_object_detection()
