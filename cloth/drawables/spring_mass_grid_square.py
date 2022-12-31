from cloth.drawables.square import Square
from typing import Optional
from cloth.gl_texture import TextureBounds
import numpy as np
import logging

logger = logging.getLogger(__name__)


class SpringMassGridSquare(Square):
    def __init__(
        self,
        side: float = 0.1,
        n_points_per_side: int = 10,
        texture_bounds: Optional[TextureBounds] = None,
        t0: Optional[float] = 0.0,
    ):
        super().__init__(
            side=side,
            n_points_per_side=n_points_per_side,
            texture_bounds=texture_bounds,
            static_normals=False,
            t0=None,
        )

        # Make vertex-to-element array where v2e[i, j] > 0 if vertex i is in element j
        # value of v2e[i, j] is 1 / ( \sum_j v2e[i, j] )
        self.vertex_to_element = np.zeros((self.vertices.shape[0], self.elements.shape[0]), dtype=np.float32)
        for j in range(self.elements.shape[0]):
            for i in self.elements[j, :]:
                self.vertex_to_element[i, j] = 1.0
        self.vertex_to_element /= self.vertex_to_element.sum(axis=1, keepdims=True)
        logger.info(f"Updated {self.__class__} to {t0=}")
        self.t = None

        self.mass = np.zeros(self.vertices.shape[0], dtype=np.float32)
        self.velocity = np.zeros_like(self.vertices)
        self.acceleration = np.zeros_like(self.vertices)

        self.update(t0)

    @property  # Only a getter :)
    def vertex_normals(self) -> np.ndarray:
        # For each triangle, compute normal
        triangles = self.vertices[self.elements]
        dir_01 = triangles[:, 1, :] - triangles[:, 0, :]  # nE, 3
        dir_12 = triangles[:, 2, :] - triangles[:, 1, :]  # nE, 3
        element_normals = np.cross(dir_01, dir_12)  # nE, 3 ... default axis=-1
        element_normals /= np.linalg.norm(element_normals, axis=1, keepdims=True)  # E, 3
        # Associate each vertex to all normals on incident triangles
        vertex_normals = np.matmul(self.vertex_to_element, element_normals)  # V, 3
        # Average normals per vertex
        vertex_normals /= np.linalg.norm(vertex_normals, axis=1, keepdims=True)  # V, 3
        return vertex_normals

    def update(self, t: float) -> None:
        if self.t is not None:
            # TODO: update vertices (compute force, use motion equations)
            dt = t - self.t
        self.t = t
        return super().update(t)