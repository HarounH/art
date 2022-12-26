import numpy as np
import itertools


class BasicCloth:
    def __init__(self, step_size: float = 0.1, min_scale: float = 1.0, max_scale: float = 2.0, frequency_hertz: float = 12.0):
        self.step_size = step_size

        x = step_size / 2.0
        y = step_size / 2.0
        # TODO: make it vertices
        self.vertices_unscaled = np.array(
            [
                -x, -y,
                x, -y,
                -x, y,
                x, y,
            ],
            dtype=np.float32,
        )
        self.max_scale = max_scale
        self.min_scale = min_scale
        self.frequency_hertz = frequency_hertz

        self.vertices = self.scale(0.0) * self.vertices_unscaled
        self.elements = np.array(
            [
                [0, 1, 2], # bottom left, bottom right, top left
                [2, 1, 3],  # top left, bottom right, top right
            ],
            dtype=np.uint32,
        )

    def scale(self, t_seconds: float) -> float:
        return self.min_scale + (self.max_scale - self.min_scale) * np.abs(np.sin(2 * np.pi * t_seconds / self.frequency_hertz))

    def update(self, t_seconds: float) -> None:
        # Just update vertices
        self.vertices = self.scale(t_seconds) * self.vertices_unscaled
