# Reproduced from: https://github.com/wolfmanstout/gaze-ocr

import bisect
import time
from collections import deque
from typing import Callable, Optional

from talon import tracking_system
from talon.track import tobii

from .gaze_filter import IvtFilter, OneEuroFilter
from .types import GazeFrame, Point2d, Point3d


GazeCallback = Callable[[tobii.GazeFrame], None]

class TobiiEyeTracker:
    STALE_GAZE_THRESHOLD_SECONDS = 0.1

    def __init__(self) -> None:
        # Keep approximately 10 seconds of frames on Tobii 5
        self._queue: deque[GazeFrame] = deque(maxlen=1000)
        self._current: Optional[GazeFrame] = None
        self.is_connected = False
        self.connect()

        # gaze filters
        self.oe_filter_x = OneEuroFilter()
        self.oe_filter_y = OneEuroFilter()
        self.ivt_filter = IvtFilter(v_threshold=3)

        # callbacks
        self._on_gaze: Optional[GazeCallback] = None


    def _handle_gaze(self, frame: tobii.GazeFrame) -> None:
        if not frame or not frame.gaze:
            return

        left_eye_pos = frame.left.pos
        right_eye_pos = frame.right.pos

        x = self.oe_filter_x(frame.ts, frame.gaze.x)
        y = self.oe_filter_y(frame.ts, frame.gaze.y)
        (fixation_x, fixation_y) = self.ivt_filter(frame.ts, x, y)

        self._current = GazeFrame(
            ts=frame.ts,
            num=frame.num,
            left=Point3d(x=left_eye_pos.x, y=left_eye_pos.y, z=left_eye_pos.z),
            right=Point3d(x=right_eye_pos.x, y=right_eye_pos.y, z=right_eye_pos.z),
            gaze=Point2d(x=x, y=y),
            fixation=Point2d(x=fixation_x, y=fixation_y),
            tracker_name=frame.tracker.name,
            serial=frame.tracker.serial
        )
        self._queue.append(self._current)

        if self._on_gaze:
            self._on_gaze(frame)


    def _handle_head(self, frame) -> None:
        pass


    def connect(self) -> None:
        if self.is_connected:
            return

        # !!! Using unstable private API that may break at any time !!!
        tracking_system.register("gaze", self._handle_gaze)
        tracking_system.register("head", self._handle_head)
        self.is_connected = True


    def disconnect(self) -> None:
        if not self.is_connected:
            return

        # !!! Using unstable private API that may break at any time !!!
        tracking_system.unregister("gaze", self._handle_gaze)
        tracking_system.unregister("head", self._handle_head)
        self.is_connected = False


    def on_gaze(self, callback: GazeCallback) -> None:
        self._on_gaze = callback


    @property
    def now(self) -> Optional[GazeFrame]:
        if not self._current or not self.has_gaze_point():
            return None

        return self._current


    def has_gaze_point(self) -> bool:
        return self._current is not None and self._current.ts > time.perf_counter() - self.STALE_GAZE_THRESHOLD_SECONDS


    def get_gaze_frame_at_timestamp(self, timestamp) -> Optional[GazeFrame]:
        if not self._queue:
            return None

        frame_index = bisect.bisect_left(self._queue, timestamp, key=lambda f: f.ts)
        if frame_index == len(self._queue):
            frame_index -= 1

        frame = self._queue[frame_index]
        if abs(frame.ts - timestamp) > self.STALE_GAZE_THRESHOLD_SECONDS:
            return None

        return frame
