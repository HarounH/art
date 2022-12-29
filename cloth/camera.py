import glfw
import numpy as np


def normalized(array: np.ndarray) -> np.ndarray:
    # TODO: div-by-zero
    return array / np.linalg.norm(array)


def get_spherical_coords(pitch: float, yaw: float) -> np.ndarray:
    return np.asarray(
        (
            np.cos(pitch) * np.cos(yaw),
            np.sin(pitch),
            np.cos(pitch) * np.sin(yaw)
        ),
        np.float32
    )


def look_at(eye: np.ndarray, center: np.ndarray, up: np.ndarray) -> np.ndarray:
    z = normalized(eye - center)
    x = normalized(np.cross(up, z))
    y = np.cross(z, x)

    result = np.zeros((4, 4), np.float32)
    result[0, :3] = x
    result[1, :3] = y
    result[2, :3] = z
    result[0, 3] = -x.dot(eye)
    result[1, 3] = -y.dot(eye)
    result[2, 3] = -z.dot(eye)
    result[3, 3] = 1.0

    return result


class Camera:
    """ Utility class to wrap around camera math; the member variables are utilized unsafely by GraphicsApi
    Exposes:
    various public fields for setting and using
    computation functions:
        .view_matrix()
        .projection_matrix()
    """
    def __init__(self):
        self.pos = np.array((0.0, 0.0, 2.0), np.float32)
        self.pitch = 0.0
        self.yaw = -np.pi / 2.0
        self.fov = np.deg2rad(80.0)
        self.keyboard_velocity = 0.1
        self.mouse_velocity = 0.0012
        self.scroll_velocity = 0.1
        self.z_near = 0.01
        self.z_far = 100.0
        self.aspect = 1.0

    def projection_matrix(self) -> np.ndarray:
        tan_fov = np.tan(self.fov / 2.0)
        result = np.zeros((4, 4), np.float32)
        result[0, 0] = 1.0 / (self.aspect * tan_fov)
        result[1, 1] = 1.0 / tan_fov
        result[2, 2] = -(self.z_far + self.z_near)/(self.z_far - self.z_near)
        result[3, 2] = -1.0
        result[2, 3] = -(2.0 * self.z_far * self.z_near) / (self.z_far - self.z_near)
        return result

    def view_matrix(self) -> np.ndarray:
        return look_at(self.pos, self.pos + self.front(), self.up())

    def front(self) -> np.ndarray:
        return get_spherical_coords(self.pitch, self.yaw)

    def up(self) -> np.ndarray:
        return normalized(np.cross(self.right(), self.front()))

    def right(self) -> np.ndarray:
        return normalized(np.cross(self.front(), np.array((0, 1, 0), np.float32)))