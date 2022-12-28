import numpy as np
import itertools
from cloth.timeseries import AbsoluteSine
from cloth.gl_texture import GlTexture
from typing import Optional


class Square:
    def __init__(
        self,
        side: float = 0.1,
        min_scale: float = 1.0,
        max_scale: float = 2.0,
        frequency_hertz: float = 12.0,
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
        self.max_scale = max_scale
        self.min_scale = min_scale
        self.timeseries = AbsoluteSine(frequency_hertz)


        self.update(0.0)

        self.elements = np.array(
            [
                [0, 1, 2], # bottom left, bottom right, top left
                [2, 1, 3],  # top left, bottom right, top right
            ],
            dtype=np.uint32,
        )


    def scale(self, t_seconds: float) -> float:
        return self.min_scale + (self.max_scale - self.min_scale) * self.timeseries.sample(t_seconds)

    def update(self, t_seconds: float) -> None:
        # Just update vertices
        self.vertices = self.scale(t_seconds) * self.vertices_unscaled
        if self.texture is not None:
            self.vertices = np.concatenate(
                (self.vertices, self.texture_coords),
                axis=1,
            )
        self.vertices = self.vertices.flatten()