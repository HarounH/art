import numpy as np
import itertools
from cloth.timeseries import AbsoluteSine
from cloth.gl_texture import GlTexture
from typing import Optional


class Square:
    def __init__(
        self,
        side: float = 0.1,
        texture: Optional[GlTexture] = None,
    ):
        self.side = side
        self.texture = texture
        s = side / 2.0
        # TODO: make it vertices
        self.vertices_unscaled = np.array(
            [
                [-s, -s, 0.0],
                [s, -s, 0.0],
                [-s, s, 0.0],
                [s, s, 0.0],
            ],
            dtype=np.float32,
        )
        if texture is not None:
            self.texture_coords = np.array(
                [
                    [0.0, 1.0],
                    [1.0, 1.0],
                    [0.0, 0.0],
                    [1.0, 0.0],
                ],
                dtype=np.float32,
            )

        self.update(0.0)

        self.elements = np.array(
            [
                [0, 1, 2], # bottom left, bottom right, top left
                [2, 1, 3],  # top left, bottom right, top right
            ],
            dtype=np.uint32,
        )

    def update(self, t_seconds: float) -> None:
        # Just update vertices
        self.vertices = self.vertices_unscaled
        if self.texture is not None:
            self.vertices = np.concatenate(
                (self.vertices, self.texture_coords),
                axis=1,
            )
        self.vertices = self.vertices.flatten()