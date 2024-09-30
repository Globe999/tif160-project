import numpy as np
from main.kinematics.inverse_kinematics_dummy import (
    dumb_but_optimized_inverse_kinematics,
)
from utils.robot_control_panel import ControlPanel
from utils.serial_communication import ArduinoSerial


class Hubert:
    def __init__(self):
        self.arduino = ArduinoSerial()
        self.control_panel = ControlPanel(self.arduino)
        self.position = np.array([0.1, -0.1, 0.3])
        self._angles = np.array([0, 0, 0])

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
        self.angles = self.arduino.inverse_kinematics(x, y, z)
        self.control_panel.update_values(self.angles)

    def update_angles(self, theta1, theta2, theta3):
        self.angles = theta1, theta2, theta3
        self.position = self.arduino.forward_kinematics(theta1, theta2, theta3)
        self.control_panel.update_values(self.angles)

    def action_pick_up(self, x, y, z) -> bool:
        print("Picking up object at", x, y, z)
        theta1, theta2, theta3 = dumb_but_optimized_inverse_kinematics(x, y, z)
        print("Calculated angles", theta1, theta2, theta3)

        print("Moving to pick up object")
        # Ensure we are not close to ground level.
        self.angles = (theta1, 85, -85)

        print(self.angles)
        print("Lowering arm")
        # Lower arm
        self.angles = (self.angles[0], self.angles[1], theta3)
        print("Opening gripper")
        self.arduino.open_gripper()
        self.angles = (self.angles[0], theta2, self.angles[2])
        # Close gripper
        self.arduino.close_gripper()

        # Raise arm
        self.angles = (self.angles[0], 90, -85)

        return True

    def action_drop_off(self, x, y, z):
        print("Dropping off object at", x, y, z)
        theta1, theta2, theta3 = dumb_but_optimized_inverse_kinematics(x, y, z)
        print("Calculated angles", theta1, theta2, theta3)

        print("Moving to drop off object")
        # Ensure we are not close to ground level.
        self.angles = (theta1, 85, -85)

        print(self.angles)
        print("Lowering arm")
        # Lower arm
        self.angles = (self.angles[0], self.angles[1], theta3)
        print("Opening gripper")
        self.angles = (self.angles[0], theta2, self.angles[2])
        self.arduino.open_gripper()
        # Close gripper

        # Raise arm
        self.angles = (self.angles[0], 90, -85)
        self.arduino.close_gripper()

        return True


if __name__ == "__main__":
    hubert = Hubert()
    print("HELLO")
    hubert.action_pick_up(0.16, -0.11, 0.136)
    hubert.action_drop_off(0.16, 0.11, 0.136)
