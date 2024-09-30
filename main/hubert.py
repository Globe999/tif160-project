import numpy as np
from utils.robot_control_panel import ControlPanel
from utils.serial_communication import ArduinoSerial


class Hubert:
    def __init__(self):
        self.arduino = ArduinoSerial()
        self.control_panel = ControlPanel(self.arduino)
        self.position = np.array([0.1, -0.1, 0.3])
        self.angles = np.array([0, 0, 0])

    def update_position(self, x, y, z):
        self.position = np.array([x, y, z])
        self.angles = self.arduino.inverse_kinematics(x, y, z)
        self.control_panel.update_values(self.angles)
        
    def update_angles(self, theta1,theta2,theta3):
        self.angles = np.array([theta1,theta2,theta3])
        self.position = self.arduino.forward_kinematics(theta1,theta2,theta3)
        self.control_panel.update_values(self.angles)


if __name__ == "__main__":
    main()
