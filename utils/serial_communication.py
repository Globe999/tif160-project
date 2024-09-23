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
    def __init__(self, port: str = "/dev/ttyACM0", baud:int = 57600) -> None:
        self.serPort = port
        self.baud = baud
        self.body = Servo(1700, 560, 2330)
        self.camera_pan = Servo(1500, 550, 2340)
        self.camera_tilt = Servo(2000, 950, 2400)
        self.shoulder = Servo(2300, 750, 2300)
        self.elbow = Servo(1650, 550,2400)
        self.gripper = Servo(1600, 550, 2150)
        self.ser = None
        self.start_marker = 60 # ASCII '<'
        self.end_marker = 62 # ASCII '>'
        self.connect()
        
    def connect(self):
        self.ser = serial.Serial(self.serPort, self.baud)
        print("Serial port " + self.serPort + " opened  Baudrate " + str(self.baud))

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial port " + self.serPort + " closed")
            
            
    def send_to_arduino(self, wait_for_reply = False):
        sendStr = f"{chr(self.start_marker)}{self.shoulder.position:04d},{self.elbow.position:04d},{self.gripper.position:04d},{self.camera_pan.position:04d},{self.camera_tilt.position:04d},{self.body.position:04d}{chr(self.end_marker)}"
        print(self.start_marker)
        print(f"Sent from PC -- {sendStr}")
        self.ser.write(sendStr.encode())
        
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
        byteCount = -1  # to allow for the fact that the last increment will be one too many

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
# Function Definitions

# def sendToArduino(sendStr):
#     ser.write(sendStr.encode())  # Encode the string to bytes

# def recvFromArduino():
#     global startMarker, endMarker

#     ck = ""
#     x = b"z"  # any value that is not an end- or startMarker
#     byteCount = -1  # to allow for the fact that the last increment will be one too many

#     # wait for the start character
#     while ord(x) != startMarker:
#         x = ser.read()

#     # save data until the end marker is found
#     while ord(x) != endMarker:
#         if ord(x) != startMarker:
#             ck = ck + x.decode()  # Decode bytes to string
#             byteCount += 1
#         x = ser.read()

#     return ck

# def waitForArduino():
#     global startMarker, endMarker

#     msg = ""
#     while msg.find("Arduino is ready") == -1:
#         while ser.inWaiting() == 0:
#             pass

#         msg = recvFromArduino()
#         print(msg)

# def runTest(td):
#     numLoops = len(td)
#     waitingForReply = False

#     n = 0
#     while n < numLoops:
#         teststr = td[n]

#         if not waitingForReply:
#             sendToArduino(teststr)
#             print("Sent from PC -- LOOP NUM " + str(n) + " TEST STR " + teststr)
#             waitingForReply = True

#         if waitingForReply:
#             while ser.inWaiting() == 0:
#                 pass

#             dataRecvd = recvFromArduino()
#             print("Reply Received  " + dataRecvd)
#             n += 1
#             waitingForReply = False

#             print("===========")
#         time.sleep(5)
#         print("Loop: " + str(n))

# THE DEMO PROGRAM STARTS HERE

# NOTE the user must ensure that the serial port and baudrate are correct
serPort = "/dev/ttyACM0"
baudRate = 57600
# ser = serial.Serial(serPort, baudRate)
# print("Serial port " + serPort + " opened  Baudrate " + str(baudRate))

startMarker = 60  # ASCII '<'
endMarker = 62    # ASCII '>'

arduino = ArduinoSerial()

arduino.wait_for_arduino()

arduino.send_to_arduino(wait_for_reply=True)

for i in range(10):
    arduino.shoulder.position -= 100
    arduino.send_to_arduino(wait_for_reply=True)
    time.sleep(1)
arduino.close()