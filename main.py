import os
import random
from typing import List

import sys

import cv2
import numpy as np

# from main.hubert import Hubert
from hubert import Hubert
from vision import Camera, CameraDetection


# def get_sorted_objects(sort_mode, order, objects) -> List[CameraDetection]:
#     # Magic
#     rank = {value: i for i, value in enumerate(order)}
#     sorted_objects = sorted(
#         objects, key=lambda x: rank.get(getattr(x, sort_mode), float("inf"))
#     )

#     # Remove all objects not in order
#     return_list = []
#     order_list = []
#     o_idx = 0

#     for obj in sorted_objects:
#         if getattr(obj, sort_mode) == order[o_idx]:
#             order_list.append(obj)
#         else:
#             if order_list:
#                 return_list.append(order_list)
#                 order_list = []
#             o_idx += 1
#             if o_idx >= len(order):
#                 break
#             order_list.append(obj)
#     if order_list:
#         return_list.append(order_list)
#     return return_list

from typing import List


def get_sorted_objects(
    sort_modes: List[str], order: List[List[str]], objects: List["CameraDetection"]
) -> List["CameraDetection"]:
    # Create rank mappings for each sort mode (primary and secondary)
    ranks = [{value: i for i, value in enumerate(order_list)} for order_list in order]

    # Sort based on primary and secondary modes (tuple sorting)
    sorted_objects = sorted(
        objects,
        key=lambda x: (
            ranks[0].get(
                getattr(x, sort_modes[0]), float("inf")
            ),  # Primary sort mode (shape)
            ranks[1].get(
                getattr(x, sort_modes[1]), float("inf")
            ),  # Secondary sort mode (color)
        ),
    )

    # Remove all objects not in order and group them by the primary sort mode
    return_list = []
    order_list = []
    o_idx = 0

    for obj in sorted_objects:
        if getattr(obj, sort_modes[0]) == order[0][o_idx]:
            order_list.append(obj)
        else:
            if order_list:
                return_list.append(order_list)
                order_list = []
            o_idx += 1
            if o_idx >= len(order[0]):
                break
            order_list.append(obj)

    if order_list:
        return_list.append(order_list)

    return return_list


def mock_get_objects() -> List[CameraDetection]:
    # Mock data generation
    types = ["circle", "square", "triangle"]
    colors = ["red", "green", "blue"]

    mock_data = []

    random.seed(8)

    for _ in range(20):
        detection = CameraDetection(
            shape=random.choice(types),
            x=random.uniform(0.0, 100.0),
            y=random.uniform(0.0, 100.0),
            z=random.uniform(0.0, 100.0),
            size=random.randint(1, 10),
            color=random.choice(colors),
            confidence=0.8,
            global_x=1,
            global_y=1,
            global_z=1,
            angle=40,
        )
        mock_data.append(detection)

    return mock_data


def main():

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    hubert = Hubert()
    hubert.set_camera_position()
    # control_panel = ControlPanel(hubert)

    # control_panel.mainloop()
    camera = Camera(index=2)  # Use the correct index

    camera_detections: List[CameraDetection] = hubert.detect_objects(camera)

    print(camera_detections)
    # camera_detections = camera.merge_objects(camera_detections, threshold=0.02)

    mode = ["shape", "color"]
    # mode = AudioInterface.get_mode()

    order = [["hexagon", "cylinder", "star"], ["red", "green"]]
    # order = ["red", "green", "blue", "white"]
    # order = AudioInterface.get_command(mode)

    sorted_objects = get_sorted_objects(mode, order, camera_detections)
    print(sorted_objects)

    for position, objects in enumerate(sorted_objects):
        for idx, obj in enumerate(objects):
            print(f"Pos: {position}, Idx:{idx}, Color: {obj.color}, Shape: {obj.shape}")
            print(f"x:{obj.global_x:.5f}\t y:{obj.global_y:.5f}\tz:{obj.global_z:.5f}")

    # height = 0.04
    for position, objects in enumerate(sorted_objects):
        for idx, obj in enumerate(objects):
            hubert.action_pick_up(obj.global_x, obj.global_y, obj.global_z + 0.02)
            hubert.action_drop_off(idx=idx, position=position)
            height += 0.04


# 0.18, 0.15, 0.03
# 0.165, 0.155, 0.06
# 0.14, 0.1, 0.12

if __name__ == "__main__":
    main()
