""" Meant to be a living rendering pipeline. """
from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
import argparse
from cloth.graphics_api import GraphicsAPI
from cloth.gl_uniform import GlUniformCollection, GlUniform
from cloth.gl_texture import GlTexture
from cloth.square import Square
import glfw
import platform
import ctypes
import time
from cloth.timeseries import AbsoluteSine
import numpy as np
import logging

def setup_logger():
    logging.basicConfig(level=logging.NOTSET)

setup_logger()

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertex_shader_path", default="cloth/shaders/vertex_shader.glsl", type=str, help="Relative path to file with vertex shader")
    parser.add_argument("--fragment_shader_path", default="cloth/shaders/fragment_shader.glsl", type=str, help="Relative path to file with fragment shader")
    parser.add_argument("--texture_path", default="cloth/rsc/leaves.jpg", type=str, help="Relative path to a textured file")
    # TODO: need a way to map parts of texture to different classes?
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    api = GraphicsAPI(800, 800, "cloth rendering", auto_update_camera=True)

    # ASSERT: gl is initialized
    with api.create_window() as window:
        model = Square(
            side=0.5,
            texture=GlTexture.init_from_file(args.texture_path),
        )
        program = api.make_program(
            vertex_shader=api.read_file_to_str(args.vertex_shader_path),
            fragment_shader=api.read_file_to_str(args.fragment_shader_path),
        )
        if program is None:
            raise RuntimeError("Program making failed")

        # create and bind VAO - needed to enable VertexAttrib
        with api.new_vertex_array() as vertices_vao:
            vertices_vbo = VBO(model.vertices, usage='GL_DYNAMIC_DRAW')
            vertices_vbo.create_buffers()
            vertices_ebo = VBO(model.elements, usage='GL_STATIC_DRAW', target='GL_ELEMENT_ARRAY_BUFFER')
            vertices_ebo.create_buffers()
            # bind VBO then buffer into GL
            vertices_vbo.bind()
            vertices_vbo.copy_data()
            vertices_ebo.bind()
            vertices_ebo.copy_data()

            # arguments: index, size, type, normalized, stride, pointer
            stride = 5 * ctypes.sizeof(ctypes.c_float)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
            glEnableVertexAttribArray(1)

        uniforms = GlUniformCollection([
            # GlUniform(name="view_matrix", dtype="mat4f", gl_program=program),
            # GlUniform(name="projection_matrix", dtype="mat4f", gl_program=program),
        ])

        tic = time.time()
        while True:
            if not api.should_run_then_clear():
                break
            t_seconds = time.time() - tic
            # use our own rendering program
            glUseProgram(program)
            with api.use_vao(vertices_vao) as vao:
                # draw vertices
                model.update(t_seconds)
                vertices_vbo.set_array(model.vertices)
                vertices_vbo.bind()
                vertices_vbo.copy_data()
                vertices_vbo.unbind()
                uniforms.update({
                    # "view_matrix": api.camera.view_matrix().transpose().copy(),
                    # "projection_matrix": api.camera.projection_matrix().transpose().copy(),
                })
                with model.texture.activate():
                    glDrawElements(
                        GL_TRIANGLES,
                        model.elements.size,
                        GL_UNSIGNED_INT,
                        ctypes.c_void_p(0),
                    )

            # tell glfw to poll and process window events
            glfw.poll_events()
            # swap frame buffer
            glfw.swap_buffers(window)
    print("Successfully reached end of main")