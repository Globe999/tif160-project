from dataclasses import dataclass
import time
from typing import List
import numpy as np
from inverse_kinematics import (
    dumb_but_optimized_inverse_kinematics,
    forward_kinematics,
)
from audio_interface import AudioInterface
from vision import Camera, CameraDetection
from utils.serial_communication import ArduinoSerial
import cv2


@dataclass
class Position:
    x: float
    y: float
    z: float


class Hubert:
    def __init__(self, mock=False, camera_index=1):
        self._arduino = ArduinoSerial(mock=mock)
        self._angles = np.array([0, 0, 0])
        self._voice = AudioInterface()
        self.position = np.array([0.1, -0.1, 0.3])

        self.static_positions = {
            "1": Position(x=0.14, y=-0.085, z=0.02),
            "2": Position(x=0.13, y=0.08, z=0.02),
            "dropoff": Position(x=0.3, y=0, z=0.02),
        }
        self.sort_mode = None
        self.sort_order = None

    @property
    def angles(self):
        return self._angles

    @angles.setter
    def angles(self, angles):
        self._angles = np.array(angles)
        self._arduino.set_angles(self._angles)
        self._arduino.send_to_arduino(wait_for_reply=True)

    def set_sort_mode(self):
        # TODO:Replace this with sort modes recieved from the camera detections
        available_sort_modes = ["shape", "color", "size"]
        self.sort_mode = self._voice.get_sort_mode(available_sort_modes)

    def set_sort_order(self):
        self.sort_order = self._voice.get_sort_order(self.sort_mode)

    def say(self, text):
        self._voice.output_audio(text)

    def update_position(self, x, y, z):
        self.position = np.array([x, y, z])
        self.angles = self.inverse_kinematics(x, y, z)

    def update_angles(self, theta1, theta2, theta3):
        self.angles = theta1, theta2, theta3
        self.position = self.forward_kinematics(theta1, theta2, theta3)

    def set_camera_position(self):
        self._arduino.set_camera_position()

    def action_pick_up(self, x, y, z) -> bool:
        # print("Picking up object at", x, y, z)
        theta1, theta2, theta3 = self.inverse_kinematics(x, y, z)
        print("Calculated angles", theta1, theta2, theta3)

        # print("Moving to pick up object")
        # Ensure we are not close to ground level.

        self.angles = (theta1, 120, -85)

        # print(self.angles)
        # print("Lowering arm")
        # Lower arm
        self._arduino.open_gripper()
        self.angles = (self.angles[0], theta2 - 5, theta3)
        # print("Opening gripper")
        # self.angles = (self.angles[0], theta2 - 5, self.angles[2])
        # Close gripper
        time.sleep(2)
        self._arduino.close_gripper()
        # self.angles = (self.angles[0], 65, -80)

        # # self.angles = (self.angles[0], 65, self.angles[2])
        self.angles = (self.angles[0], self.angles[1] + 10, self.angles[2])
        self.angles = (self.angles[0], self.angles[1], -60)
        self.angles = (self.angles[0], 65, self.angles[2])
        self.open_gripper()
        self.close_gripper()
        # Raise arm
        # print("Here1")
        self.angles = (self.angles[0], 120, -85)
        # self.angles = (self.angles[0], self.angles[1], -85)

        return True

    def action_drop_off(self, idx: int, position: int):
        drop_off_pos = [(0.18, 0.15, 0.03), (0.165, 0.155, 0.06), (0.14, 0.1, 0.12)]

        x, y, z = drop_off_pos[idx]
        theta1, theta2, theta3 = self.inverse_kinematics(x, y, z)
        if position == 0:
            # print("hello")
            theta1 = 66
        if position == 1:
            theta1 = 30
        if position == 2:
            theta1 = -10

        # print("Dropping off object at ", x, y, z)
        # print("At positon",position)
        print("Calculated dropoff angles", theta1, theta2, theta3)

        # print("Moving to drop off object")
        # Ensure we are not close to ground level.
        self.angles = (theta1, 120, -85)

        # print(self.angles)
        # print("Lowering arm")
        # Lower arm
        self.angles = (self.angles[0], theta2, theta3)
        # self.angles = (self.angles[0], theta2, self.angles[2])
        # self.angles = (self.angles[0], self.angles[1], theta3)
        # print("Opening gripper")

        self._arduino.open_gripper()
        # Close gripper

        # Raise arm
        self.angles = (self.angles[0], 120, -85)
        # self.angles = (self.angles[0], self.angles[1], -85)
        self._arduino.close_gripper()

        return True

    def inverse_kinematics(self, x, y, z):
        return dumb_but_optimized_inverse_kinematics(x, y, z)

    def forward_kinematics(self, theta1, theta2, theta3):
        return forward_kinematics(theta1, theta2, theta3)

    def close_gripper(self):
        self._arduino.close_gripper()

    def open_gripper(self):
        self._arduino.open_gripper()

    def detect_objects(self, camera: Camera) -> List[CameraDetection]:
        self.set_camera_position()
        camera_detections = []
        # for i in [-40]:
        for i in np.arange(-40, 40, 10, dtype=int):
            self.update_angles(i, 90, -85)
            time.sleep(1)
            frame = camera.grab_frame()
            camera_detections.extend(
                camera.get_detected_objects_from_nn(frame=frame, angle=i)
            )
        cv2.destroyAllWindows()
        return camera.merge_objects(camera_detections, distance_threshold=0.08)

    def get_sorted_objects(
        self,
        objects: List[CameraDetection],
    ) -> List[List[CameraDetection]]:
        # Create rank mappings for each sort mode (primary, secondary, etc.)
        ranks = [
            {value: i for i, value in enumerate(order_list)}
            for order_list in self.sort_order
        ]
        # Sort_mode = ["shape", "color"]
        # self.hubert.sort_order = [["hexagon", "cylinder", "star"], ["red", "green","blue"]]

        sorted_lists = []  # ist to hold sorted lists for each sort mode

        for order in self.sort_order[0]:

            # Filter out all objects not containing order
            filtered_objects = filter(
                lambda x: getattr(x, self.sort_mode[0]) == order, objects
            )
            if len(self.sort_mode) > 1:
                sorted_lists.append(
                    sorted(
                        filtered_objects,
                        key=lambda x: ranks[1].get(
                            getattr(x, self.sort_mode[1]), float("inf")
                        ),
                    )
                )
        return sorted_lists

        # Sort objects based on each sort mode independently
        # for i in range(len(self.sort_mode)):
        #     sorted_objects = sorted(
        #         objects,
        #         key=lambda x: (
        #             ranks[i].get(
        #                 getattr(x, self.sort_mode[i]), float("inf")
        #             )  # Sort based on the current sort mode (shape, color, etc.)
        #         )
        #     )
        #     sorted_lists.append(sorted_objects)  # Append each sorted list to the result

        # return sorted_lists

        # Sort based on primary and secondary modes (tuple sorting)
        # sorted_objects = sorted(
        #     objects,
        #     key=lambda x: (
        #         ranks[0].get(
        #             getattr(x, self.sort_mode[0]), float("inf")
        #         ),  # Primary sort mode (e.g., shape)
        #         ranks[1].get(
        #             getattr(x, self.sort_mode[1]), float("inf")
        #         ),  # Secondary sort mode (e.g., color)
        #     ),
        # )
        return_list = []
        order_list = []
        o_idx = 0

        return return_list


if __name__ == "__main__":
    hubert = Hubert()
    hubert.action_pick_up(0.22, -0.05, 0.06)
    hubert.action_drop_off(0.22, 0.11, 0.04)
    hubert.action_pick_up(0.20, -0.05, 0.04)
    hubert.action_drop_off(0.20, 0.10, 0.08)
    # hubert.action_pick_up(0.22, -0.11, 0.05)
    # hubert.action_drop_off(0.22, 0.11, 0.08)
