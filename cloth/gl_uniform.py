from typing import Dict, Callable, Any, List
from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
import glfw
import numpy as np
from dataclasses import dataclass


GlUniformUpdateRegistry: Dict[str, Callable] = {
    "float": lambda location, value: glUniform1f(location, value),
    "int": lambda location, value: glUniform1i(location, value),
    "vec2f": lambda location, value: glUniform2fv(location, 1, value.ctypes.data_as(ctypes.POINTER(ctypes.c_float))),
    "vec3f": lambda location, value: glUniform3fv(location, 1, value.ctypes.data_as(ctypes.POINTER(ctypes.c_float))),
    "vec4f": lambda location, value: glUniform4fv(location, 1, value.ctypes.data_as(ctypes.POINTER(ctypes.c_float))),
    "mat2f": lambda location, value: glUniformMatrix2fv(location, 1, GL_TRUE, value.ctypes.data_as(ctypes.POINTER(ctypes.c_float))),
    "mat3f": lambda location, value: glUniformMatrix3fv(location, 1, GL_TRUE, value.ctypes.data_as(ctypes.POINTER(ctypes.c_float))),
    "mat4f": lambda location, value: glUniformMatrix4fv(location, 1, GL_TRUE, value.ctypes.data_as(ctypes.POINTER(ctypes.c_float))),
}


@dataclass
class GlUniform:
    name: str
    dtype: str
    gl_program: Any  # gl Program type...

    def update(self, value: Any) -> None:
        location = glGetUniformLocation(self.gl_program, self.name)
        GlUniformUpdateRegistry.get(self.dtype)(location, value)
        return


class GlUniformCollection:
    def __init__(self, gl_uniforms: List[GlUniform]):
        self.gl_uniforms = {
            uniform.name: uniform
            for uniform in gl_uniforms
        }

    def update(self, name_to_values: Dict[str, Any]) -> None:
        for name, value in name_to_values.items():
            self.gl_uniforms[name].update(value)
