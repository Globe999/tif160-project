import os
import random
from typing import List

import sys

import cv2

# from main.hubert import Hubert
from speech.speech_to_instructions import AudioInterface
from utils.robot_control_panel import ControlPanel
from vision.vision import Camera, CameraDetection


def get_sorted_objects(sort_mode, order, objects):
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

    # hubert = Hubert()

    # control_panel = ControlPanel(hubert)

    # control_panel.mainloop()
    camera = Camera(index=2)  # Use the correct index

    print("Here")
    for i in np.arange(-70,70,5):
    result = camera.get_detected_objects()

    print(result)
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
