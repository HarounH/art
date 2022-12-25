import numpy as np
import itertools


class StaticCloth:
    def __init__(self, step_size: float = 0.1):
        self.step_size = step_size

        x = step_size / 2.0
        y = step_size / 2.0
        # TODO: make it vertices
        self.vertices = np.array(
            [
                -x, -y,
                x, -y,
                -x, y,
                x, y,
            ],
            dtype=np.float32,
        )

        self.elements = np.array(
            [
                [0, 1, 2], # bottom left, bottom right, top left
                [2, 1, 3],  # top left, bottom right, top right
            ],
            dtype=np.uint32,
        )
