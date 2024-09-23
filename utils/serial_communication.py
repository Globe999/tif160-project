import atexit
from dataclasses import dataclass
import serial
import time


@dataclass
class Servo:
    position: int
    min: int
    max: int


class ArduinoSerial:
    def __init__(self, port: str = "/dev/ttyACM0", baud: int = 57600) -> None:
        self.serPort = port
        self.baud = baud
        self.BODY = 0
        self.CAMERA_PAN = 1
        self.CAMERA_TILT = 2
        self.SHOULDER = 3
        self.ELBOW = 4
        self.GRIPPER = 5

        self.servos = [
            Servo(1700, 560, 2330),
            Servo(1500, 550, 2340),
            Servo(2000, 950, 2400),
            Servo(2300, 750, 2300),
            Servo(1650, 550, 2400),
            Servo(1600, 550, 2150),
        ]
        self.ser = None
        self.start_marker = 60  # ASCII '<'
        self.end_marker = 62  # ASCII '>'
        self.connect()

    def connect(self):
        self.ser = serial.Serial(self.serPort, self.baud)
        print("Serial port " + self.serPort + " opened  Baudrate " + str(self.baud))

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial port " + self.serPort + " closed")

    def send_to_arduino(self, wait_for_reply=False):
        send_str = chr(self.start_marker)
        servo_positions = ",".join([f"{servo.position:04d}" for servo in self.servos])
        send_str += servo_positions
        send_str += chr(self.end_marker)
        
        print(self.start_marker)
        print(f"Sent from PC -- {send_str}")
        self.ser.write(send_str.encode())

        if wait_for_reply:
            while self.ser.inWaiting() == 0:
                pass

            dataRecvd = self.recv_from_arduino()
            print("Reply Received  " + dataRecvd)
            return dataRecvd
        else:
            return True

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
        msg = ""
        while msg.find("Arduino is ready") == -1:
            while self.ser.inWaiting() == 0:
                pass

            msg = self.recv_from_arduino()
            print(msg)


arduino = ArduinoSerial()

arduino.wait_for_arduino()

arduino.send_to_arduino(wait_for_reply=True)

for i in range(10):
    arduino.servos[arduino.SHOULDER].position -= 100
    arduino.send_to_arduino(wait_for_reply=True)
    time.sleep(1)
arduino.close()
