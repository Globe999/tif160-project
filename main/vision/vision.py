from dataclasses import dataclass
from typing import List


@dataclass
class CameraDetection:
    type: str
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
