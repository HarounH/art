# F_w = f(x, t) \in R^3
# point p at position x... surface has normal n

import numpy as np
from .base_field import BaseField

class WindCylinderField(BaseField):
    """
    The field applies a force f(x) at position x, constant in time.
        f(x) = |F| direction

    where |F| is the magnitude of force.
        it is 0 if x > r; otherwise it decays nicely from 1 to 0
    """

    def __init__(
        self,
        origin: np.ndarray,
        direction: np.ndarray,
        radius: float,
        coefficient: float = 1.0
    ):
        self.origin = origin
        self.direction = direction
        self.radius = radius
        self.coefficient = coefficient

    def get_force_field(self, query: np.ndarray) -> np.ndarray:
        # query: V, 3 array of points
        nVertices = query.shape[0]
        displacement = query - self.origin
        intersections = self.origin + self.direction * np.reshape(
            np.einsum("vk,k->v", displacement, self.direction),
            (nVertices, 1)
        )
        distance_from_axis = query - intersections  # V, 3
        u = np.linalg.norm(distance_from_axis, axis=1, keepdims=True) / self.radius  # V
        u = np.clip(u, 0.0, 1.0)
        u = 3 * (1 - u)**2 - 2 * (1 - u)**3
        return self.coefficient * u * self.direction  # V, 3?


if __name__ == "__main__":
    field = WindCylinderField(
        origin=np.array([0, 0, 0], dtype=np.float32),
        direction=np.array([0.0, 0.0, 1.0], dtype=np.float32),
        radius=1.0,
    )
    query = np.array(
        [
            [0.0, 0.5, 1.0],
            [0.0, 0.5, 0.7],
            [0.0, 0.2, 5.0],
            [0.3, 0.4, 1.0],
            [1.3, 1.4, 1.0],
        ],
        dtype=np.float32
    )
    force = field.get_force_field(query)
    print(force)