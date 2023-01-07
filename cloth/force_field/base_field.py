import numpy as np


class BaseField:
    def get_force_field(self, *args, **kwargs) -> np.ndarray:
        ...