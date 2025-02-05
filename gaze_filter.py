from functools import reduce
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
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        # Previous values.
        self.t_prev = t0
        self.x_prev = x0
        self.dx_prev = dx0

    def __call__(self, t: float, x: float) -> float:
        if not self.t_prev:
            self.t_prev = t
            self.x_prev = x
            return x

        """Compute the filtered signal."""
        t_e = t - self.t_prev

        # The filtered derivative of the signal.
        a_d = smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = exponential_smoothing(a_d, dx, self.dx_prev)

        # The filtered signal.
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = smoothing_factor(t_e, cutoff)
        x_hat = exponential_smoothing(a, x, self.x_prev)

        # Memorize the previous values.
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat


class IvtFilter:
    def __init__(self, v_threshold=1):
        self.init()
        self.v_threshold = v_threshold

    def init(self, t0=0.0, x0=0.0, y0=0.0):
        self.fixation = x0, y0
        self.t_prev = t0
        self.gaze_points_prev: list[tuple[float, float]] = []

    def __call__(self, t: float, x: float, y: float) -> tuple[float, float]:
        if not self.t_prev:
            self.init(t, x, y)
            return x, y

        if sqrt((x - self.fixation[0]) ** 2 + (y - self.fixation[1]) ** 2) / (t - self.t_prev) >= self.v_threshold:
            self.init(t, x, y)
        else:
            self.gaze_points_prev.append((x, y))

            fixation = reduce(lambda acc, cur: (acc[0] + cur[0], acc[1] + cur[1]), self.gaze_points_prev, (0.0, 0.0))
            self.fixation: tuple[float, float] = (fixation[0] / len(self.gaze_points_prev), fixation[1] / len(self.gaze_points_prev))

        self.t_prev = t

        return self.fixation
