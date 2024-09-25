import tkinter as tk
from tkinter import ttk

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

    def increment(self, col_index, amount):
        new_value = self.values[col_index].get() + amount
        self.values[col_index].set(new_value)
        self.arduino.servos[col_index].position = new_value
        self.disable_buttons()
        self.arduino.send_to_arduino(wait_for_reply=True)
        self.enable_buttons()
        


    def decrement(self, col_index, amount):
        new_value = self.values[col_index].get() - amount
        self.values[col_index].set(new_value)
        self.arduino.servos[col_index].position = new_value
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