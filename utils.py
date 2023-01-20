import time
import logging


def setup_logger():
    logging.basicConfig(level=logging.NOTSET)


class LogicBlock:
    def __init__(self, description: str, logger: logging.Logger):
        self.description = description
        self.logger = logger

    def __enter__(self):
        self.t0 = t0 = time.time()
        self.logger.info(f"[start] description={self.description} {t0=}")
        return self

    def __exit__(self, *args):  # TODO: handle error logging
        self.t1 = t1 = time.time()
        self.elapsed = elapsed = self.t1 - self.t0
        self.logger.info(f"[end] description={self.description} {t1=}; {elapsed=}")
