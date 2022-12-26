import numpy as np


class AbsoluteSine:
    def __init__(self, frequency_hertz: float):
        self.frequency_hertz = frequency_hertz

    def sample(self, time_seconds: float) -> float:
        return np.abs(np.sin(2 * np.pi * time_seconds / self.frequency_hertz))