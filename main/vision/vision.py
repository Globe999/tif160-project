from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class CameraDetection:
    shape: str
    x: float
    y: float
    z: float
    size: int
    color: str


class Camera:

    def __init__(self) -> None:
        pass

    def get_detected_objects(self) -> List[CameraDetection]:
        pass
    
    def get_position(self,pixel_pos_x,pixel_pos_y,camera_angle):
        
        mid_y_pos = 0.132
        length_per_pixel_y = 0.071 / 240
        length_per_pixel_x = 0.098/320
        x_pos = np.sin(camera_angle)*mid_y_pos + pixel_pos_x*length_per_pixel_x
        y_pos = np.cos(camera_angle)*mid_y_pos + pixel_pos_y*length_per_pixel_y
        
        return x_pos,y_pos

cam = Camera()
x,y = cam.get_position(0,0,np.pi/4)

print(x,y)