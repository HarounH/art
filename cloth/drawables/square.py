from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO

import numpy as np
import itertools
from cloth.timeseries import AbsoluteSine
from cloth.gl_texture import TextureBounds
from typing import Optional
from cloth.drawables.base_drawable import BaseDrawable


class Square(BaseDrawable):
    def __init__(
        self,
        side: float = 0.1,
        texture_bounds: Optional[TextureBounds] = None,
    ):
        self.side = side
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
        self.use_texture = texture_bounds is not None
        if self.use_texture:
            self.texture_coords = np.array(
                [
                    [texture_bounds.top, texture_bounds.right],
                    [texture_bounds.bottom, texture_bounds.right],
                    [texture_bounds.top, texture_bounds.left],
                    [texture_bounds.bottom, texture_bounds.left],
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
        if self.use_texture:
            self.vertices = np.concatenate(
                (self.vertices, self.texture_coords),
                axis=1,
            )
        self.vertices = self.vertices.flatten()

    def create_buffers(self) -> None:
        self.vertices_vbo = VBO(self.vertices, usage='GL_DYNAMIC_DRAW')
        self.vertices_vbo.create_buffers()
        self.vertices_ebo = VBO(self.elements, usage='GL_STATIC_DRAW', target='GL_ELEMENT_ARRAY_BUFFER')
        self.vertices_ebo.create_buffers()
        # bind VBO then buffer into GL
        self.vertices_vbo.bind()
        self.vertices_vbo.copy_data()
        self.vertices_ebo.bind()
        self.vertices_ebo.copy_data()

        # arguments: index, size, type, normalized, stride, pointer
        stride = 5 * ctypes.sizeof(ctypes.c_float)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(1)

    def draw(self) -> None:
        self.vertices_vbo.set_array(self.vertices)
        self.vertices_vbo.bind()
        self.vertices_vbo.copy_data()
        self.vertices_vbo.unbind()
        # draw vertices
        glDrawElements(
            GL_TRIANGLES,
            self.elements.size,
            GL_UNSIGNED_INT,
            ctypes.c_void_p(0),
        )