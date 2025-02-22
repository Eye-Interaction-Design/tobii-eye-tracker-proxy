from collections import deque
from math import pi, sqrt


def smoothing_factor(t_e, cutoff):
    r = 2 * pi * cutoff * t_e
    return r / (r + 1)


def exponential_smoothing(a, x, x_prev):
    return a * x + (1 - a) * x_prev


class OneEuroFilter:
    def __init__(self, t0=0.0, x0=0.0, dx0=0.0, min_cutoff=1.0, beta=0.0,
                 d_cutoff=1.0):
        """Initialize the one euro filter."""
        # The parameters.
        self._min_cutoff = float(min_cutoff)
        self._beta = float(beta)
        self._d_cutoff = float(d_cutoff)
        # Previous values.
        self._t_prev = t0
        self._x_prev = x0
        self._dx_prev = dx0

    def __call__(self, t: float, x: float) -> float:
        if not self._t_prev:
            self._t_prev = t
            self._x_prev = x
            return x

        """Compute the filtered signal."""
        t_e = t - self._t_prev

        # The filtered derivative of the signal.
        a_d = smoothing_factor(t_e, self._d_cutoff)
        dx = (x - self._x_prev) / t_e
        dx_hat = exponential_smoothing(a_d, dx, self._dx_prev)

        # The filtered signal.
        cutoff = self._min_cutoff + self._beta * abs(dx_hat)
        a = smoothing_factor(t_e, cutoff)
        x_hat = exponential_smoothing(a, x, self._x_prev)

        # Memorize the previous values.
        self._x_prev = x_hat
        self._dx_prev = dx_hat
        self._t_prev = t

        return x_hat


class IvtFilter:
    def __init__(self, v_threshold=1):
        self.init()
        self._v_threshold = v_threshold

    def init(self, t0=0.0, x0=0.0, y0=0.0):
        self._queue: deque[tuple[float, float]] = deque(maxlen=100)
        self._t_prev = t0
        self._gaze_x_sum: float = 0
        self._gaze_y_sum: float = 0
        self._fixation = x0, y0

    def __call__(self, t: float, x: float, y: float) -> tuple[float, float]:
        if not self._t_prev:
            self.init(t, x, y)
            return x, y

        if sqrt((x - self._fixation[0]) ** 2 + (y - self._fixation[1]) ** 2) / (t - self._t_prev) >= self._v_threshold:
            self.init(t, x, y)
        else:
            self._queue.append((x, y))
            self._gaze_x_sum += x
            self._gaze_y_sum += y
            self._fixation: tuple[float, float] = (self._gaze_x_sum / len(self._queue), self._gaze_y_sum / len(self._queue))

        self._t_prev = t

        return self._fixation
