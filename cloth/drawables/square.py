from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO

import numpy as np
import itertools
from cloth.timeseries import AbsoluteSine
from cloth.gl_texture import TextureBounds
from typing import Optional
from cloth.drawables.base_drawable import BaseDrawable
import logging

logger = logging.getLogger(__name__)


class Square(BaseDrawable):
    def __init__(
        self,
        side: float = 0.1,
        n_points_per_side: int = 10,
        texture_bounds: Optional[TextureBounds] = None,
        static_normals: bool = True,
        t0: Optional[float] = 0.0,
    ):
        self.side = side
        s = side / 2.0

        pos = np.linspace(-s, s, n_points_per_side)
        n_vertices = n_points_per_side * n_points_per_side
        self.vertices = np.zeros((n_vertices, 3), dtype=np.float32)
        # order of vertices: row major
        # i, j -> i, j+1 ... -> i, (n_points_per_side - 1) -> i + 1, 0
        self.vertices[:, 0] = np.repeat(pos, n_points_per_side)
        self.vertices[:, 1] = np.tile(pos, n_points_per_side)
        logger.info(f"created vertices_unscaled with {self.vertices.shape=}")

        if static_normals:
            self.vertex_normals = np.zeros((n_vertices, 3), dtype=np.float32)
            self.vertex_normals[:, 2] = 1.0  # positive-z direction
            logger.info(f"created normals_unscaled with {self.vertex_normals.shape=}")

        if (use_texture := (texture_bounds is not None)):
            texture_u_pos = np.linspace(texture_bounds.left, texture_bounds.right, n_points_per_side)
            texture_v_pos = np.linspace(texture_bounds.top, texture_bounds.bottom, n_points_per_side)
            self.texture_coords = np.zeros((n_vertices, 2), dtype=np.float32)
            self.texture_coords[:, 0] = np.repeat(texture_u_pos, n_points_per_side)
            self.texture_coords[:, 1] = np.tile(texture_v_pos, n_points_per_side)
            logger.info(f"created texture_coords with {self.texture_coords.shape=}")
        self.use_texture = use_texture

        # We produce elements in a fun 2-step process:

        # first, construct all possible triangles incident on the grid
        # vertex (i, j) induces two triangles: ((i, j), (i+1, j), (i, j+1)) and ((i, j), (i-1, j), (i, j-1))
        # vertex (i, j) = k = n*i + j, induces two triangles: (k, k+n, k+1) and (k, k-n, k-1)
        # we use element k as (k, k+n, k+1) and element k+1 as (k, k-n, k-1)
        k_array_repeated = np.repeat(np.array(list(range(0, n_vertices)), dtype=np.int), 2)  # use int to support sub
        alternating_plus_minus_one = np.array([1 if (k % 2 == 0) else -1 for k in range(0, 2 * n_vertices)], dtype=np.int)
        alternating_plus_minus_n = alternating_plus_minus_one * n_points_per_side
        with_invalid_elements = np.stack((k_array_repeated, k_array_repeated + alternating_plus_minus_n , k_array_repeated + alternating_plus_minus_one), axis=-1)
        # second, filter out triangles outside the grid
        # unfortunately, we can't filter by `k` because the constrains are in (i, j) space
        # we construct 2 invalidity filters:
        # CONDITION 0-edge: forall (i,j) if ij = 0, then second triangle ((i, j), (i-1, j), (i, j-1)) doesnt exist
        lower_edge_condition = np.array(
            [
                (two_k % 2 == 0)  # first triangle is always fine
                or (  # second triangle is fine if both i and j > 0
                    (((two_k // 2) % n_points_per_side) != 0)  # j = 0
                    and (((two_k // 2) // n_points_per_side) != 0)  # i = 0
                )
                for two_k in range(2 * n_vertices)
            ],
            dtype=bool
        )
        # forall (i,j) if j = n-1 or i = n-1, then first triangle ((i, j), (i+1, j), (i, j+1)) doesnt exist
        upper_edge_condition = np.array(
            [
                (two_k % 2 == 1)  # second triangle is always fine
                or (  # first triangle is fine if both i and j < (n - 1)
                    (((two_k // 2) % n_points_per_side) < (n_points_per_side - 1))  # j = 0
                    and (((two_k // 2) // n_points_per_side) < (n_points_per_side - 1))  # i = 0
                )
                for two_k in range(2 * n_vertices)
            ],
            dtype=bool
        )
        # apply them filters
        self.elements = with_invalid_elements[(lower_edge_condition & upper_edge_condition), :].astype(np.uint32)
        logger.info(f"created elements with {self.elements.shape=}")
        if t0 is not None:
            logger.info(f"Updated {self.__class__} to {t0=}")
            self.update(t0)

    def update(self, t_seconds: float) -> None:
        # Just update vertices
        self.vertices_buffer = self.vertices
        # add in normals
        self.vertices_buffer = np.concatenate((self.vertices_buffer, self.vertex_normals), axis=1)
        if self.use_texture:
            self.vertices_buffer = np.concatenate(
                (self.vertices_buffer, self.texture_coords),
                axis=1,
            )
        self.vertices_buffer = self.vertices_buffer.flatten()

    def create_buffers(self) -> None:
        self.vertices_vbo = VBO(self.vertices_buffer, usage='GL_DYNAMIC_DRAW')
        self.vertices_vbo.create_buffers()
        self.vertices_ebo = VBO(self.elements, usage='GL_STATIC_DRAW', target='GL_ELEMENT_ARRAY_BUFFER')
        self.vertices_ebo.create_buffers()
        # bind VBO then buffer into GL
        self.vertices_vbo.bind()
        self.vertices_vbo.copy_data()
        self.vertices_ebo.bind()
        self.vertices_ebo.copy_data()

        # arguments: index, size, type, normalized, stride, pointer
        stride = (
            self.vertices.shape[1] + self.vertex_normals.shape[1] + self.texture_coords.shape[1]
        ) * ctypes.sizeof(ctypes.c_float)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(2)

    def draw(self) -> None:
        self.vertices_vbo.set_array(self.vertices_buffer)
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