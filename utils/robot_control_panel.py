import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import threading
from main.hubert import Hubert
from main.vision.vision import Camera


class ControlPanel(tk.Tk):
    def __init__(self, hubert: Hubert = None):
        super().__init__()
        self.title("Robot Control Panel")
        self.geometry("1280x800")
        self.buttons = []
        self.servo_frame = ttk.Frame(self)
        self.servo_frame.pack(side=tk.LEFT, padx=10, pady=5)
        self.camera = Camera(2)
        if hubert is None:
            self.hubert = Hubert()
        else:
            self.hubert = hubert

        self.create_servo_controls()
        self.create_controls()
        self.create_info_panel()
        self.create_video_feed()
        self.update_info_panel()
        self.enable_buttons()
        self.update_video_feed()

    def create_servo_controls(self):
        for col_index, servo in enumerate(self.hubert._arduino.servos):
            frame = ttk.Frame(self.servo_frame)
            frame.pack(pady=10)

            label = ttk.Label(frame, text=f"Servo {servo.name}")
            label.grid(row=0, column=0, columnspan=5, pady=(0, 1))

            for idx, value in enumerate([-100, -10, 10, 100]):
                button = ttk.Button(
                    frame,
                    text=f"{value}",
                    command=lambda idx=col_index, val=value: self.increment(idx, val),
                )
                button.grid(row=1, column=idx, padx=5)
                self.buttons.append(button)

    def create_info_panel(self):
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(side=tk.TOP, padx=10, pady=5)

        # XYZ coordinates
        ttk.Label(self.info_frame, text="Current XYZ Coordinates:").grid(
            row=0, column=0, columnspan=2
        )
        ttk.Label(self.info_frame, text="X:").grid(row=1, column=0)
        self.current_x_label = ttk.Label(self.info_frame, text="0")
        self.current_x_label.grid(row=1, column=1)

        ttk.Label(self.info_frame, text=f"Y:").grid(row=2, column=0)
        self.current_y_label = ttk.Label(self.info_frame, text="0")
        self.current_y_label.grid(row=2, column=1)

        ttk.Label(self.info_frame, text="Z:").grid(row=3, column=0)
        self.current_z_label = ttk.Label(self.info_frame, text="0")
        self.current_z_label.grid(row=3, column=1)

        # Angles
        ttk.Label(self.info_frame, text="Current Angles:").grid(
            row=4, column=0, columnspan=2
        )
        ttk.Label(self.info_frame, text="Body:").grid(row=5, column=0)
        self.current_body_angle_label = ttk.Label(self.info_frame, text="0")
        self.current_body_angle_label.grid(row=5, column=1)

        ttk.Label(self.info_frame, text="Shoulder:").grid(row=6, column=0)
        self.current_shoulder_angle_label = ttk.Label(self.info_frame, text="0")
        self.current_shoulder_angle_label.grid(row=6, column=1)

        ttk.Label(self.info_frame, text="Elbow:").grid(row=7, column=0)
        self.current_elbow_angle_label = ttk.Label(self.info_frame, text="0")
        self.current_elbow_angle_label.grid(row=7, column=1)

        # Servo positions
        ttk.Label(self.info_frame, text="Current Servo Positions:").grid(
            row=8, column=0, columnspan=2
        )
        self.current_servo_labels = []
        for i, servo in enumerate(self.hubert._arduino.servos):
            ttk.Label(self.info_frame, text=f"Servo {servo.name}:").grid(
                row=9 + i, column=0
            )
            label = ttk.Label(self.info_frame, text="0")
            label.grid(row=9 + i, column=1)
            self.current_servo_labels.append(label)

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

        angle_button = ttk.Button(
            angle_frame,
            text="Set Angles",
            command=self.set_angles,
        )
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

        kinematics_button = ttk.Button(
            kinematics_frame,
            text="Calculate Inverse Kinematics",
            command=self.set_position,
        )
        kinematics_button.grid(row=3, columnspan=2)
        self.buttons.append(kinematics_button)

        gripper_frame = ttk.Frame(controls_frame)
        gripper_frame.grid(row=0, column=2, padx=10)

        open_gripper_button = ttk.Button(
            gripper_frame,
            text="Open Gripper",
            command=self.open_gripper,
        )
        open_gripper_button.grid(row=0, column=0, pady=5)
        self.buttons.append(open_gripper_button)

        close_gripper_button = ttk.Button(
            gripper_frame,
            text="Close Gripper",
            command=self.close_gripper,
        )
        close_gripper_button.grid(row=1, column=0, pady=5)
        self.buttons.append(close_gripper_button)

        detect_objects_button = ttk.Button(
            controls_frame,
            text="Detect Objects",
            command=self.detect_objects,
        )
        detect_objects_button.grid(row=1, column=2, padx=10, pady=5)
        self.buttons.append(detect_objects_button)

    def create_video_feed(self):
        self.video_frame = ttk.Frame(self)
        self.video_frame.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)
        self.canvas = tk.Canvas(self.video_frame, width=640, height=480)
        self.canvas.pack()

    def update_video_feed(self):
        frame = self.camera.grab_frame()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
        self.canvas.image = image
        self.after(1, self.update_video_feed)

    def open_gripper(self):
        self.hubert.open_gripper()
        self.update_info_panel()

    def close_gripper(self):
        self.hubert.close_gripper()
        self.update_info_panel()

    def update_info_panel(self):
        self.current_x_label.config(text=f"{self.hubert.position[0]:.3f}")
        self.current_y_label.config(text=f"{self.hubert.position[1]:.3f}")
        self.current_z_label.config(text=f"{self.hubert.position[2]:.3f}")

        self.current_body_angle_label.config(text=f"{self.hubert.angles[0]:.3f}")
        self.current_shoulder_angle_label.config(text=f"{self.hubert.angles[1]:.3f}")
        self.current_elbow_angle_label.config(text=f"{self.hubert.angles[2]:.3f}")

        for i, servo in enumerate(self.hubert._arduino.servos):
            self.current_servo_labels[i].config(text=f"{servo.position}")

    def set_angles(self):
        body_angle = float(self.body_angle_entry.get())
        shoulder_angle = float(self.shoulder_angle_entry.get())
        elbow_angle = float(self.elbow_angle_entry.get())

        self.disable_buttons()
        self.hubert.update_angles(body_angle, shoulder_angle, elbow_angle)
        self.update_info_panel()
        self.enable_buttons()

    def set_position(self):
        x = float(self.x_entry.get())
        y = float(self.y_entry.get())
        z = float(self.z_entry.get())

        self.disable_buttons()
        self.hubert.update_position(x, y, z)
        self.enable_buttons()
        self.update_info_panel()

    def increment(self, col_index, amount):
        self.hubert._arduino.servos[col_index].increment_position(amount)
        self.disable_buttons()
        self.hubert._arduino.send_to_arduino(wait_for_reply=True)
        self.enable_buttons()

    def disable_buttons(self):
        for button in self.buttons:
            button["state"] = "disabled"

    def enable_buttons(self):
        for button in self.buttons:
            button["state"] = "normal"

    def detect_objects(self):
        self.hubert.detect_objects(self.camera)
        self.update_info_panel()

    def run_in_thread(self, func, *args):
        thread = threading.Thread(target=func, args=args)
        thread.start()


if __name__ == "__main__":
    app = ControlPanel()
    app.mainloop()
