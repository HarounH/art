""" Pre-emptive class around light source """
import numpy as np


class LightSource:
    def __init__(self, pos: np.ndarray):
        self.pos = pos