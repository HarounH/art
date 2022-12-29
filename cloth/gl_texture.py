# Like GlUniform but for textures. GL Textures are annoying bruv
from OpenGL.GL import *
from PIL import Image
import numpy as np
from typing import Optional
import contextlib
import logging
from dataclasses import dataclass


logger = logging.getLogger()


@dataclass
class TextureBounds:
    bottom: float = 1.0
    top: float = 0.0
    left: float = 0.0
    right: float = 1.0


class GlTexture:
    """
    with graphics_api.
    texture = GlTexture.init_from_file(...)

    texture.
    """
    @staticmethod
    def init_from_file(filename: str) -> "GlTexture":
        image = Image.open(filename)
        data = np.array(image, np.uint8)
        logger.info(f"Loaded texture from {filename=}.. {data.shape=} ... {data.dtype=}")
        return GlTexture(data)

    def __init__(self, data: np.ndarray):
        self.data = data

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        self.texture_id = glGenTextures(1)
        if self.texture_id == 0:
            raise RuntimeError(f"Unexpected {self.texture_id=}")
        self.bind(data=data)
        self.unbind()

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def bind(self, data: Optional[np.ndarray]):  # no data means use self.data
        if data is None:
            data = self.data
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA8,  # internal format
            data.shape[1],
            data.shape[0],
            0,  # border
            GL_RGB,  # format
            GL_UNSIGNED_BYTE,  # type
            data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
        )

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        # in this case, GL_NEAREST and GL_LINEAR should make little difference
        # because only the center of pixels are used in the shader
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


    def __del__(self):
        if self.texture_id != 0:
            glDeleteTextures([self.texture_id])
        self.texture_id = 0

    @contextlib.contextmanager
    def activate(self, slot: int = 0):
        glActiveTexture(GL_TEXTURE0 + slot)  # TODO: understand this
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        yield self.texture_id
        # render stuff
        glBindTexture(GL_TEXTURE_2D, 0)
