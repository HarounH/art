from cloth.drawables.square import Square
from typing import Optional, List
from cloth.gl_texture import TextureBounds
import numpy as np
import logging
import itertools
from cloth.force_field.base_field import BaseField


logger = logging.getLogger(__name__)
_EPSILON: float = 1e-3


class SpringMassGridSquare(Square):
    gravity_coefficient: float = 0.1
    def __init__(
        self,
        side: float = 0.1,
        n_points_per_side: int = 50,
        texture_bounds: Optional[TextureBounds] = None,
        t0: Optional[float] = 0.0,
        mass: float = 0.1,  # TODO: replace with gsm
        init_spring_length_factor: float = 1.0,
        uniform_spring_stiffness: float = 50.0,
        damping_force_coefficient: float = 0.05,
        wind_field: Optional[BaseField] = None,
    ):
        super().__init__(
            side=side,
            n_points_per_side=n_points_per_side,
            texture_bounds=texture_bounds,
            static_normals=False,
            t0=None,
        )
        self.init_spring_length_factor = init_spring_length_factor
        self.uniform_spring_stiffness = uniform_spring_stiffness
        self.damping_force_coefficient = damping_force_coefficient
        self.fixed_vertices = [0, n_points_per_side - 1]
        self.wind_field = wind_field

        # Make vertex-to-element array where v2e[i, j] > 0 if vertex i is in element j
        # value of v2e[i, j] is 1 / ( \sum_j v2e[i, j] )
        self.vertex_to_element = np.zeros((self.vertices.shape[0], self.elements.shape[0]), dtype=np.float32)
        for j in range(self.elements.shape[0]):
            for i in self.elements[j, :]:
                self.vertex_to_element[i, j] = 1.0
        self.vertex_to_element /= self.vertex_to_element.sum(axis=1, keepdims=True)

        self.init_springs()

        # TODO: make mass a property based on gsm
        self.mass_per_vertex = mass
        self.velocity = np.zeros_like(self.vertices)
        self.acceleration = np.zeros_like(self.vertices)

        self.t = None
        logger.info(f"Updating {self.__class__} to {t0=}")
        self.update(t0)

    def init_springs(self) -> None:
        """ Constructs variables needed for the spring part of this cloth simulation:
        spring_end_points (S, 2) int matrix like elements
        spring_resting_lengths (S, 1) float vector of initial length
        spring_stiffness (S, 1) float vector
        vertex_to_spring (V, S): 2d array, ij = 1 if vertex i is first end point is spring j
        """
        # For each vertex (i, j): we have a few springs...
        # uniquely, (i, j) attaches to (i+1, j), (i, j+1), (i+1, j+1), (i-1, j+1)
        js = list(range(0, self.n_points_per_side))
        ijs = np.array(list(itertools.product(js, js)), dtype=np.int)  # V, 2

        def valid_vertex_indices(indices: np.ndarray, axis: int = -1) -> np.ndarray:
            # indices: k dimensional array of indices, last axis is conjunctioned over
            # output: k-1 dimensional boolean - True if valid else False
            below_zero = indices < 0
            above_n = indices >= self.n_points_per_side
            invalid = np.any(below_zero | above_n, axis=axis)
            return ~invalid

        spring_ends = []
        for spring_end_point_offset in [
            [1, 0],
            [0, 1],
            [1, 1],
            [-1, 1],
            [2, 0],
            [0, 2],
        ]:
            candidate_spring_end = ijs.copy()
            for k, v in enumerate(spring_end_point_offset):
                candidate_spring_end[:, k] += v
            candidate_spring_end = np.concatenate((ijs, candidate_spring_end), axis=1)  # V, 4
            spring_ends.append(candidate_spring_end[valid_vertex_indices(candidate_spring_end)])

        valid_springs_ij = np.concatenate(
            tuple(spring_ends),
            axis=0,
        )

        self.spring_end_points = np.stack(
            (
                (valid_springs_ij[:, 0] * self.n_points_per_side) + valid_springs_ij[:, 1],
                (valid_springs_ij[:, 2] * self.n_points_per_side) + valid_springs_ij[:, 3],
            ),
            axis=1
        )

        spring_resting_lengths = self.vertices[self.spring_end_points]  # S, 2, 3
        self.spring_resting_lengths = self.init_spring_length_factor * np.linalg.norm(
            spring_resting_lengths[:, 1, :] - spring_resting_lengths[:, 0, :],
            axis=1,
            keepdims=True,
        )  # S, 1
        self.spring_stiffness = self.uniform_spring_stiffness + np.zeros((spring_resting_lengths.shape[0], 1), dtype=np.float32)

        self.vertex_to_spring = np.zeros((self.vertices.shape[0], self.spring_end_points.shape[0]), dtype=np.float32)
        for j in range(self.spring_end_points.shape[0]):
            self.vertex_to_spring[self.spring_end_points[j, 0], j] = 1
            self.vertex_to_spring[self.spring_end_points[j, 1], j] = -1

    @property
    def mass(self) -> np.ndarray:
        # TODO: use g/m^2 and area per vertex?
        return np.zeros((self.vertices.shape[0], 1), dtype=np.float32) + self.mass_per_vertex

    @property  # Only a getter :)
    def vertex_normals(self) -> np.ndarray:
        # For each triangle, compute normal
        triangles = self.vertices[self.elements]  # nE, 3, 3
        dir_01 = triangles[:, 1, :] - triangles[:, 0, :]  # nE, 3
        dir_12 = triangles[:, 2, :] - triangles[:, 1, :]  # nE, 3
        element_normals = np.cross(dir_01, dir_12)  # nE, 3 ... default axis=-1
        element_normals /= np.linalg.norm(element_normals, axis=1, keepdims=True)  # E, 3
        # Associate each vertex to all normals on incident triangles
        vertex_normals = np.matmul(self.vertex_to_element, element_normals)  # V, 3
        # Average normals per vertex
        vertex_normals /= np.linalg.norm(vertex_normals, axis=1, keepdims=True)  # V, 3
        return vertex_normals

    def force(self) -> np.ndarray:
        force = np.zeros_like(self.vertices, dtype=np.float32)  # V, 3

        # gravity
        force[:, 1] -= self.gravity_coefficient * self.mass[:, 0]

        # damping
        force[:, :] -= self.damping_force_coefficient * self.velocity

        # springs
        spring_end_pos_3d = self.vertices[self.spring_end_points]  # S, 2, 3

        spring_displacement = spring_end_pos_3d[:, 1, :] - spring_end_pos_3d[:, 0, :]  # S, 3
        spring_lengths = np.linalg.norm(spring_displacement, axis=1, keepdims=True)  # S, 1
        spring_direction_vector = spring_displacement / spring_lengths  # S, 3

        spring_size_change = spring_lengths - self.spring_resting_lengths
        spring_size_change_norm = np.linalg.norm(spring_size_change, axis=1, keepdims=True)  # S, 1
        valid_spring_size_change = (spring_size_change_norm > _EPSILON).astype(np.float32)
        spring_size_change = spring_size_change * valid_spring_size_change

        spring_force_magnitude = self.spring_stiffness * spring_size_change  # S, 1
        spring_force = spring_force_magnitude * spring_direction_vector  # S, 3
        force += np.matmul(self.vertex_to_spring, spring_force)  # V, 3

        if self.wind_field is not None:
            force += self.wind_field.get_force_field(self.vertices)

        # clamp top two corners
        for vertex in self.fixed_vertices:
            force[vertex, :] = 0

        return force

    def update(self, t: float) -> None:
        if self.t is not None:
            dt = t - self.t
            force = self.force()
            self.acceleration = force / self.mass
            self.velocity = self.velocity + (dt * self.acceleration)
            self.vertices = self.vertices + (dt * self.velocity)
            logger.debug(f"Iteration stats: {dt=} {np.linalg.norm(self.velocity)=} {np.linalg.norm(self.acceleration)=} {np.linalg.norm(force)=}")
        self.t = t
        return super().update(t)