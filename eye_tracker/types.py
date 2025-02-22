from dataclasses import dataclass

@dataclass
class Point2d:
    x: float
    y: float

@dataclass
class Point3d:
    x: float
    y: float
    z: float

@dataclass
class GazeFrame:
    ts: float
    num: int
    left: Point3d
    right: Point3d
    gaze: Point2d
    fixation: Point2d
    tracker_name: str
    serial: str
