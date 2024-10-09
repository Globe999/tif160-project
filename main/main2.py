import os
import random
from typing import List

import sys

import cv2
import numpy as np

# from main.hubert import Hubert
from main.hubert import Hubert
from speech.speech_to_instructions import AudioInterface
from utils.robot_control_panel import ControlPanel
from vision.vision import Camera, CameraDetection


def get_sorted_objects(sort_mode, order, objects) -> List[CameraDetection]:
    # Magic
    rank = {value: i for i, value in enumerate(order)}
    sorted_objects = sorted(
        objects, key=lambda x: rank.get(getattr(x, sort_mode), float("inf"))
    )

    # Remove all objects not in order
    sorted_objects = [obj for obj in sorted_objects if getattr(obj, sort_mode) in order]

    return sorted_objects


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
    camera_detections = camera.merge_objects(camera_detections, 0.05)  # 5cm threshold

    mode = "color"
    # mode = AudioInterface.get_mode()

    order = ["red", "green", "blue"]
    # order = AudioInterface.get_command(mode)

    sorted_objects = get_sorted_objects(mode, order, camera_detections)
    print(sorted_objects)

    for idx, obj in enumerate(sorted_objects):
        print(f"Idx:{idx}, Color: {obj.color}, Shap: {obj.shape}")
        print(f"x:{obj.global_x:.5f}\t y:{obj.global_y:.5f}\tz:{obj.global_z:.5f}")
    for object in sorted_objects:
        hubert.action_pick_up(object.global_x, object.global_y, object.global_z + 0.02)
        hubert.action_drop_off(0.22, 0.22, 0.04)

    # # Filter the detections to find the green object
    # green_objects = [obj for obj in res if obj.color == "red"]

    # if green_objects:
    #     # Pick up the first green object found
    #     green_object = green_objects[0]
    #     print(
    #         f"Found green object at \nx:{green_object.x},\ny:{green_object.y},\nz:{green_object.z}"
    #     )
    #     hubert.action_pick_up(green_object.x, green_object.y, green_object.z + 0.02)
    #     hubert.action_drop_off(0.22, 0.22, 0.04)
    # else:
    #     print("No green objects found.")

    # mock_data = mock_get_objects()

    # available_sort_modes = ["shape", "color", "size"]

    # available_colors = list({x.color for x in mock_data})
    # available_shapes = list({x.shape for x in mock_data})
    # available_sizes = list({x.size for x in mock_data})

    # audio_interface = AudioInterface()

    # mode = audio_interface.get_mode(available_sort_modes)

    # order = audio_interface.get_command(mode)

    # # sort_mode = "color"
    # # order = ["red", "green"]

    # new_list = get_sorted_objects(mode, order, mock_data)
    # for i, (old, new) in enumerate(zip(mock_data, new_list)):
    #     print(f"{i}: {getattr(old,mode)} -> {getattr(new,mode)}")

    # sort_mode, order = get_instructions()
    # objects = camera.get_objects()


if __name__ == "__main__":
    main()
