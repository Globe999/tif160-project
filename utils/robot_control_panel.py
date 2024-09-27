import tkinter as tk
from tkinter import ttk

from main.kinematics.inverse_kinematics_dummy import dumb_but_optimized_inverse_kinematics
from utils.serial_communication import ArduinoSerial

class ControlPanel(tk.Tk):
    def __init__(self, arduino: ArduinoSerial = None):
        super().__init__()
        self.title("Robot Control Panel")
        self.geometry("1280x300")
        self.buttons = []
        self.columns_frame = ttk.Frame(self)
        self.columns_frame.pack(padx=10, pady=10)

        if arduino is None:
            self.arduino = ArduinoSerial()
        else:
            self.arduino = arduino
        self.values = [tk.IntVar(value=self.arduino.servos[i].position) for i in range(6)]
        
        for i in range(6):
            self.create_column(i)
        
        self.create_controls()
        self.enable_buttons()

    def create_column(self, col_index):
        frame = ttk.Frame(self.columns_frame)
        frame.grid(row=0, column=col_index, padx=10)

        label = ttk.Label(frame, text=f"Servo {self.arduino.servos[col_index].name}")
        label.pack(side=tk.TOP)

        plus_100_button = ttk.Button(frame, text="+100", command=lambda: self.increment(col_index, 100))
        plus_100_button.pack(side=tk.TOP)

        plus_10_button = ttk.Button(frame, text="+10", command=lambda: self.increment(col_index, 10))
        plus_10_button.pack(side=tk.TOP)

        label_value = ttk.Label(frame, textvariable=self.values[col_index])
        label_value.pack(side=tk.TOP)

        minus_10_button = ttk.Button(frame, text="-10", command=lambda: self.decrement(col_index, 10))
        minus_10_button.pack(side=tk.TOP)

        minus_100_button = ttk.Button(frame, text="-100", command=lambda: self.decrement(col_index, 100))
        minus_100_button.pack(side=tk.TOP)
        
        self.buttons.append(plus_100_button)
        self.buttons.append(plus_10_button)
        self.buttons.append(minus_10_button)
        self.buttons.append(minus_100_button)

    def create_controls(self):
        controls_frame = ttk.Frame(self)
        controls_frame.pack(padx=10, pady=10)

        # Angle controls
        angle_frame = ttk.Frame(controls_frame)
        angle_frame.grid(row=0, column=0, padx=10)

        ttk.Label(angle_frame, text="BODY Angle:").grid(row=0, column=0)
        self.body_angle_entry = ttk.Entry(angle_frame)
        self.body_angle_entry.grid(row=0, column=1)

        ttk.Label(angle_frame, text="SHOULDER Angle:").grid(row=1, column=0)
        self.shoulder_angle_entry = ttk.Entry(angle_frame)
        self.shoulder_angle_entry.grid(row=1, column=1)

        ttk.Label(angle_frame, text="ELBOW Angle:").grid(row=2, column=0)
        self.elbow_angle_entry = ttk.Entry(angle_frame)
        self.elbow_angle_entry.grid(row=2, column=1)

        angle_button = ttk.Button(angle_frame, text="Set Angles", command=self.set_angles)
        angle_button.grid(row=3, columnspan=2)
        self.buttons.append(angle_button)

        # Kinematics controls
        kinematics_frame = ttk.Frame(controls_frame)
        kinematics_frame.grid(row=0, column=1, padx=10)

        ttk.Label(kinematics_frame, text="X:").grid(row=0, column=0)
        self.x_entry = ttk.Entry(kinematics_frame)
        self.x_entry.grid(row=0, column=1)

        ttk.Label(kinematics_frame, text="Y:").grid(row=1, column=0)
        self.y_entry = ttk.Entry(kinematics_frame)
        self.y_entry.grid(row=1, column=1)

        ttk.Label(kinematics_frame, text="Z:").grid(row=2, column=0)
        self.z_entry = ttk.Entry(kinematics_frame)
        self.z_entry.grid(row=2, column=1)

        kinematics_button = ttk.Button(kinematics_frame, text="Calculate Inverse Kinematics", command=self.call_inverse_kinematics)
        kinematics_button.grid(row=3, columnspan=2)
        self.buttons.append(kinematics_button)
        
        gripper_frame = ttk.Frame(controls_frame)
        gripper_frame.grid(row=0, column=2, padx=10)

        open_gripper_button = ttk.Button(gripper_frame, text="Open Gripper", command=self.open_gripper)
        open_gripper_button.grid(row=0, column=0, pady=5)
        self.buttons.append(open_gripper_button)

        close_gripper_button = ttk.Button(gripper_frame, text="Close Gripper", command=self.close_gripper)
        close_gripper_button.grid(row=1, column=0, pady=5)
        self.buttons.append(close_gripper_button)
        


    def open_gripper(self):
        # Implement the logic to open the gripper
        self.arduino.open_gripper()

    def close_gripper(self):
        # Implement the logic to close the gripper
        self.arduino.close_gripper()
    def set_angles(self):
        body_angle = float(self.body_angle_entry.get())
        shoulder_angle = float(self.shoulder_angle_entry.get())
        elbow_angle = float(self.elbow_angle_entry.get())

        self.arduino.servos[self.arduino.BODY].angle = body_angle
        self.arduino.servos[self.arduino.SHOULDER].angle = shoulder_angle
        self.arduino.servos[self.arduino.ELBOW].angle = elbow_angle

        print("Body - Angle ", self.arduino.servos[self.arduino.BODY].angle, "Pos:", self.arduino.servos[self.arduino.BODY].position)
        print("Shoulder - Angle ", self.arduino.servos[self.arduino.SHOULDER].angle, "Pos:", self.arduino.servos[self.arduino.SHOULDER].position)
        print("Elbow - Angle ", self.arduino.servos[self.arduino.ELBOW].angle, "Pos:", self.arduino.servos[self.arduino.ELBOW].position)
        
        self.update_labels()
        self.disable_buttons()
        self.arduino.send_to_arduino(wait_for_reply=True)
        self.enable_buttons()

    def call_inverse_kinematics(self):
        x = float(self.x_entry.get())
        y = float(self.y_entry.get())
        z = float(self.z_entry.get())
        print("Got x, y, z:", x, y, z)
        theta1, theta2, theta3 = dumb_but_optimized_inverse_kinematics(x, y, z)

        print(theta1, theta2, theta3)
        
        self.arduino.servos[self.arduino.BODY].angle = float(theta1)
        self.arduino.servos[self.arduino.SHOULDER].angle = float(theta2)
        self.arduino.servos[self.arduino.ELBOW].angle = float(theta3)
        
        print("Body - Angle ", self.arduino.servos[self.arduino.BODY].angle, "Pos:", self.arduino.servos[self.arduino.BODY].position)
        print("Shoulder - Angle ", self.arduino.servos[self.arduino.SHOULDER].angle, "Pos:", self.arduino.servos[self.arduino.SHOULDER].position)
        print("Elbow - Angle ", self.arduino.servos[self.arduino.ELBOW].angle, "Pos:", self.arduino.servos[self.arduino.ELBOW].position)
        self.update_labels()
        self.disable_buttons()
        self.arduino.send_to_arduino(wait_for_reply=True)
        self.enable_buttons()
        
        
    def update_labels(self):
        for i in range(6):
            self.values[i].set(self.arduino.servos[i].position)
        print("Labels updated")


    def increment(self, col_index, amount):
        new_value = self.arduino.servos[col_index].position + amount
        self.values[col_index].set(new_value)
        self.arduino.servos[col_index].position = new_value
        self.update_labels()
        self.disable_buttons()
        self.arduino.send_to_arduino(wait_for_reply=True)
        self.enable_buttons()
        


    def decrement(self, col_index, amount):
        # new_value = self.values[col_index].get() - amount
        new_value = self.arduino.servos[col_index].position - amount
        self.values[col_index].set(new_value)
        self.arduino.servos[col_index].position = new_value
        
        self.update_labels()
        self.disable_buttons()
        self.arduino.send_to_arduino(wait_for_reply=True)
        self.enable_buttons()

    def disable_buttons(self):
        for button in self.buttons:
            button["state"] = "disabled"
            

    def enable_buttons(self):
        for button in self.buttons:
            button["state"] = "normal"



if __name__ == "__main__":
    app = ControlPanel()
    app.mainloop()