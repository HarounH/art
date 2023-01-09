""" Meant to be a living rendering pipeline. """
import os
from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
import argparse
from cloth.graphics_api import GraphicsAPI
from cloth.gl_uniform import GlUniformCollection, GlUniform
from cloth.gl_texture import GlTexture, TextureBounds
from cloth.light_source import LightSource
from cloth.drawables.square import Square
from cloth.drawables.spring_mass_grid_square import SpringMassGridSquare
from cloth.force_field.wind_cylinder_field import WindCylinderField
import glfw
import platform
import ctypes
import time
from cloth.timeseries import AbsoluteSine
import numpy as np
import logging
import json


def setup_logger():
    logging.basicConfig(level=logging.NOTSET)

setup_logger()


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default="cloth/output/", type=str, help="Relative path to folder to renderer will save frames")
    parser.add_argument("--vertex_shader_path", default="cloth/shaders/vertex_shader_with_mat.glsl", type=str, help="Relative path to file with vertex shader")
    parser.add_argument("--fragment_shader_path", default="cloth/shaders/fragment_shader.glsl", type=str, help="Relative path to file with fragment shader")
    parser.add_argument("--texture_path", default="cloth/rsc/leaves.jpg", type=str, help="Relative path to a textured file")
    parser.add_argument("-l", "--light_coords", type=float, nargs=3, help="Where is the light boio", default=[0.0, 0.0, 3.0])
    parser.add_argument("--drawable", type=str, help="Classname of drawable", default="SpringMassGridSquare")
    parser.add_argument("--kwargs_json", type=str, help="Kwargs in json format", default=r"{}")
    # TODO: need a way to map parts of texture to different classes?
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    light_source = LightSource(pos=np.array(args.light_coords, dtype=np.float32))
    api = GraphicsAPI(800, 800, "cloth rendering", auto_update_camera=True)
    model = eval(args.drawable)(  # TODO: make it a registry or an importlib
        side=0.5,
        texture_bounds=TextureBounds(),
        wind_field=WindCylinderField(
            origin=np.array([0.25, -0.25, 5.0], dtype=np.float32),
            direction=np.array([0.0, 0.0, -1.0], dtype=np.float32),
            radius=0.1,
            coefficient=0.05,
        ),
        **(json.loads(args.kwargs_json)),
    )
    os.makedirs(args.output_dir, exist_ok=True)
    # ASSERT: gl is initialized
    with api.create_window() as window:
        # TODO: build drawable based on some configuration file.
        texture = GlTexture.init_from_file(args.texture_path)

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
            GlUniform(name="light_source_position", dtype="vec3f", gl_program=program),
        ])

        tic = 0.0 # time.time()
        delta_t_seconds = 0.01
        while True:
            if not api.should_run_then_clear():
                break
            tic = tic + delta_t_seconds
            model.update(tic)
            # use our own rendering program
            glUseProgram(program)
            # update some uniforms
            uniforms.update({
                "view_matrix": api.camera.view_matrix(),
                "projection_matrix": api.camera.projection_matrix(),
                "light_source_position": light_source.pos,
            })
            with api.use_vao(vertices_vao) as vao:
                with texture.activate():
                    model.draw()

            # tell glfw to poll and process window events
            glfw.poll_events()
            # swap frame buffer
            glfw.swap_buffers(window)
            api.save_frame(save_dir=args.output_dir)

    print("Successfully reached end of main")