from dataclasses import dataclass
import time
from typing import List
import numpy as np
from main.kinematics.inverse_kinematics_dummy import (
    dumb_but_optimized_inverse_kinematics,
    forward_kinematics,
)
from main.vision.vision import Camera, CameraDetection
from utils.serial_communication import ArduinoSerial


@dataclass
class Position:
    x: float
    y: float
    z: float


class Hubert:
    def __init__(self):
        self.arduino = ArduinoSerial()
        self.position = np.array([0.1, -0.1, 0.3])
        self._angles = np.array([0, 0, 0])

        self.positions = {
            "1": Position(x=0.14, y=-0.085, z=0.02),
            "2": Position(x=0.13, y=0.08, z=0.02),
            "dropoff": Position(x=0.3, y=0, z=0.02),
        }

    @property
    def angles(self):
        return self._angles

    @angles.setter
    def angles(self, angles):
        self._angles = np.array(angles)
        self.arduino.set_angles(self._angles)
        self.arduino.send_to_arduino(wait_for_reply=True)

    def update_position(self, x, y, z):
        self.position = np.array([x, y, z])
        self.angles = self.inverse_kinematics(x, y, z)

    def update_angles(self, theta1, theta2, theta3):
        self.angles = theta1, theta2, theta3
        self.position = self.forward_kinematics(theta1, theta2, theta3)

    def set_camera_position(self):
        self.arduino.set_camera_position()

    def action_pick_up(self, x, y, z) -> bool:
        print("Picking up object at", x, y, z)
        theta1, theta2, theta3 = self.inverse_kinematics(x, y, z)
        print("Calculated angles", theta1, theta2, theta3)

        print("Moving to pick up object")
        # Ensure we are not close to ground level.
        self.angles = (theta1, 90, -85)

        print(self.angles)
        print("Lowering arm")
        # Lower arm
        self.angles = (self.angles[0], self.angles[1], theta3)
        print("Opening gripper")
        self.arduino.open_gripper()
        self.angles = (self.angles[0] - 5, theta2 - 4, self.angles[2] - 4)
        # Close gripper
        time.sleep(2)
        self.arduino.close_gripper()

        # Raise arm
        print("Here1")
        self.angles = (self.angles[0], 90, self.angles[2])
        print("Here2")
        self.angles = (self.angles[0], self.angles[1], -85)

        return True

    def action_drop_off(self, x, y, z):
        print("Dropping off object at", x, y, z)
        theta1, theta2, theta3 = self.inverse_kinematics(x, y, z)
        print("Calculated angles", theta1, theta2, theta3)

        print("Moving to drop off object")
        # Ensure we are not close to ground level.
        self.angles = (theta1, 90, -85)

        print(self.angles)
        print("Lowering arm")
        # Lower arm
        self.angles = (self.angles[0], self.angles[1], theta3)
        self.angles = (self.angles[0], theta2, self.angles[2])
        print("Opening gripper")

        self.arduino.open_gripper()
        # Close gripper

        # Raise arm
        self.angles = (self.angles[0], 90, self.angles[2])
        self.angles = (self.angles[0], self.angles[1], -85)
        self.arduino.close_gripper()

        return True

    def inverse_kinematics(self, x, y, z):
        return dumb_but_optimized_inverse_kinematics(x, y, z)

    def forward_kinematics(self, theta1, theta2, theta3):
        return forward_kinematics(theta1, theta2, theta3)

    def close_gripper(self):
        self.arduino.close_gripper()

    def open_gripper(self):
        self.arduino.open_gripper()

    def detect_objects(self, camera: Camera) -> List[CameraDetection]:
        self.set_camera_position()
        camera_detections = []
        for i in np.arange(-70, 70, 20, dtype=int):
            self.update_angles(i, 90, -85)
            camera_detections.extend(camera.get_detected_objects(angle=i))

        return camera_detections


if __name__ == "__main__":
    hubert = Hubert()
    hubert.action_pick_up(0.22, -0.05, 0.06)
    hubert.action_drop_off(0.22, 0.11, 0.04)
    hubert.action_pick_up(0.20, -0.05, 0.04)
    hubert.action_drop_off(0.20, 0.10, 0.08)
    # hubert.action_pick_up(0.22, -0.11, 0.05)
    # hubert.action_drop_off(0.22, 0.11, 0.08)
