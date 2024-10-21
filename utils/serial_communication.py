from dataclasses import dataclass
import os
from typing import List
import numpy as np
import serial
import time


from dataclasses import dataclass

import serial.serialutil


class Servo:
    def __init__(
        self,
        position: int,
        min: int,
        max: int,
        name: str,
        only_positive_angle: bool,
        offset: int,
        inversed: bool,
        angle: int = 0,
    ):
        self._position = position
        self.min = min
        self.max = max
        self.name = name
        self.only_positive_angle = only_positive_angle
        self.offset = offset
        self._inversed = inversed
        self._angle = angle

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        # we want to set position and map the angle to the position
        self._angle = value

        span = (self.max - self.min) / 180

        if not self.only_positive_angle:
            value = value + 90

        pos = span * value + self.min
        if self._inversed:
            half = int((self.max - self.min) / 2 + self.min)

            if pos < half:
                diff = half - pos

                pos = half + diff
            else:
                diff = pos - half
                pos = half - diff

            # if value < half:
            #     value = (half - value) * 2 + value
            # else:
            #     value = value - (value - half) * 2

        self.position = pos

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        # print("RECIEVED POSITION", value)

        if value < self.min:
            print("Warn: Value less than min - ", self.name)
            self._position = self.min + self.offset
        elif value > self.max:
            print("Warn: Value greater than max - ", self.name)
            self._position = self.max + self.offset
        else:
            self._position = int(value) + self.offset

    def increment_position(self, amount):
        new_value = self._position + amount
        if new_value < self.min:
            print("Warn: Value less than min - ", self.name)
            self._position = self.min
        elif new_value > self.max:
            print("Warn: Value greater than max - ", self.name)
            self._position = self.max
        self._position = new_value


class ArduinoSerial:
    def __init__(
        self, port: str = "COM7", baud: int = 57600, mock=False
    ) -> None:
        self.serPort = port
        self.baud = baud
        self.BODY = 0
        self.CAMERA_PAN = 1
        self.CAMERA_TILT = 2
        self.SHOULDER = 3
        self.ELBOW = 4
        self.GRIPPER = 5
        self._gripper_open = False
        self.mock = mock
        self.servos: List[Servo] = [
            Servo(
                position=1700,
                min=560,
                max=2330,
                name="body",
                only_positive_angle=False,
                inversed=True,
                offset=330,
            ),
            Servo(
                position=1450,
                min=550,
                max=2340,
                name="camera_pan",
                only_positive_angle=False,
                inversed=False,
                offset=0,
            ),
            Servo(
                position=1300,
                min=950,
                max=2400,
                name="camera_tilt",
                only_positive_angle=False,
                inversed=False,
                offset=0,
            ),
            Servo(
                position=1500,
                min=650,
                max=2400,
                name="shoulder",
                only_positive_angle=True,
                inversed=True,
                offset=0,
            ),
            Servo(
                position=750,
                min=600,
                max=2300,
                name="elbow",
                only_positive_angle=False,
                inversed=False,
                offset=0,
            ),
            Servo(
                position=1600,
                min=550,
                max=2150,
                name="gripper",
                only_positive_angle=False,
                inversed=False,
                offset=0,
            ),
        ]
        self.position = np.array([0.22, -0.11, 0.20])
        self.ser = None
        self.start_marker = 60  # ASCII '<'
        self.end_marker = 62  # ASCII '>'
        self.connect()
        self.wait_for_arduino()
        self.send_to_arduino(wait_for_reply=True)

    @property
    def gripper_open(self):
        return self._gripper_open

    def open_gripper(self):
        self._gripper_open = True
        self.servos[self.GRIPPER].position = 750
        self.send_to_arduino(wait_for_reply=True)

    def close_gripper(self):
        self._gripper_open = False
        # self.servos[self.GRIPPER].position = 2050
        self.servos[self.GRIPPER].position = 1350
        self.send_to_arduino(wait_for_reply=True)

    def connect(self):

        if os.name == "nt":
            self.serPort = "COM3"

        if not self.mock:
            try:
                self.ser = serial.Serial(self.serPort, self.baud)
            except serial.serialutil.SerialException as e:
                print("Error opening serial port: " + str(e))
                print("Trying other port...")
                self.serPort = "/dev/ttyACM1" if os.name == "posix" else "COM4"
                self.ser = serial.Serial(self.serPort, self.baud)

        print("Serial port " + self.serPort + " opened  Baudrate " + str(self.baud))

    def close(self):
        if self.ser and self.ser.is_open and not self.mock:
            self.ser.close()
            print("Serial port " + self.serPort + " closed")

    def set_camera_position(self):
        self.servos[self.CAMERA_PAN].position = 1450
        self.servos[self.CAMERA_TILT].position = 1300
        self.send_to_arduino(wait_for_reply=True)

    def send_to_arduino(self, wait_for_reply=False):
        send_str = chr(self.start_marker)
        servo_positions = ",".join([f"{servo.position:04d}" for servo in self.servos])
        send_str += servo_positions
        send_str += chr(self.end_marker)
        # print(f"Sent from PC -- {send_str}")
        if self.mock:
            print(f"Emulating serial write - {send_str}")
            time.sleep(1)
            return True
        else:
            self.ser.write(send_str.encode())

        if wait_for_reply:
            while self.ser.inWaiting() == 0:
                pass

            dataRecvd = self.recv_from_arduino()
            # print("Reply Received  " + dataRecvd)
            return dataRecvd
        else:
            return True

    def set_angles(self, angles):
        self.servos[self.BODY].angle = angles[0]
        self.servos[self.SHOULDER].angle = angles[1]
        self.servos[self.ELBOW].angle = angles[2]

    def recv_from_arduino(self):
        ck = ""
        x = b"z"  # any value that is not an end- or startMarker
        byteCount = (
            -1
        )  # to allow for the fact that the last increment will be one too many

        # wait for the start character
        while ord(x) != self.start_marker:
            x = self.ser.read()

        # save data until the end marker is found
        while ord(x) != self.end_marker:
            if ord(x) != self.start_marker:
                ck = ck + x.decode()  # Decode bytes to string
                byteCount += 1
            x = self.ser.read()

        return ck

    def wait_for_arduino(self):
        if self.mock:
            return
        msg = ""
        while msg.find("Arduino is ready") == -1:
            while self.ser.inWaiting() == 0:
                pass

            msg = self.recv_from_arduino()
            # print(msg)


if __name__ == "__main__":
    arduino = ArduinoSerial(mock=True)

    arduino.wait_for_arduino()

    arduino.send_to_arduino(wait_for_reply=True)

    for i in range(10):
        arduino.servos[arduino.SHOULDER].position -= 100
        arduino.send_to_arduino(wait_for_reply=True)
        time.sleep(1)
    arduino.close()
