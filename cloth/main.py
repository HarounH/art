""" Meant to be a living rendering pipeline. """
from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
import argparse
from cloth.graphics_api import GraphicsAPI
from cloth.gl_uniform import GlUniformCollection, GlUniform
from cloth.gl_texture import GlTexture
from cloth.drawables.square import Square
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
    parser.add_argument("--vertex_shader_path", default="cloth/shaders/vertex_shader_with_mat.glsl", type=str, help="Relative path to file with vertex shader")
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
            # TODO: figure out where to keep texture
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
            model.create_buffers()

        uniforms = GlUniformCollection([
            GlUniform(name="view_matrix", dtype="mat4f", gl_program=program),
            GlUniform(name="projection_matrix", dtype="mat4f", gl_program=program),
        ])

        tic = time.time()
        while True:
            if not api.should_run_then_clear():
                break
            t_seconds = time.time() - tic
            model.update(t_seconds)
            # use our own rendering program
            glUseProgram(program)
            uniforms.update({
                "view_matrix": api.camera.view_matrix(), #.transpose().copy(),
                "projection_matrix": api.camera.projection_matrix(), #.transpose().copy(),
            })
            with api.use_vao(vertices_vao) as vao:
                with model.texture.activate():
                    model.draw()

            # tell glfw to poll and process window events
            glfw.poll_events()
            # swap frame buffer
            glfw.swap_buffers(window)
    print("Successfully reached end of main")