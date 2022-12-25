import numpy as np
import itertools


class StaticCloth:
    def __init__(self, step_size: float = 0.1):
        self.step_size = step_size

        x = step_size / 2.0
        y = step_size / 3.0
        # TODO: make it vertices
        self.vertices = np.array(
            [
                x, -y,
                -x, -y,
                0.0, 2 * y
            ],
            dtype=np.float32,
        )
