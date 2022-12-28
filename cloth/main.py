""" Meant to be a living rendering pipeline. """
from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
import argparse
from cloth.graphics_api import GraphicsAPI
from cloth.gl_uniform import GlUniformCollection, GlUniform
from cloth.basic_cloth import BasicCloth
import glfw
import platform
import ctypes
import time
from cloth.timeseries import AbsoluteSine
import numpy as np


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertex_shader_path", default="cloth/shaders/vertex_shader.glsl", type=str, help="Relative path to file with vertex shader")
    parser.add_argument("--fragment_shader_path", default="cloth/shaders/fragment_shader.glsl", type=str, help="Relative path to file with fragment shader")
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    model = BasicCloth(step_size=0.5)
    api = GraphicsAPI(800, 800, "cloth rendering")

    # ASSERT: gl is initialized
    with api.create_window() as window:
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
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)

        uniforms = GlUniformCollection([
            GlUniform(name="color", dtype="vec3f", gl_program=program)
        ])

        color_triangle = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float32)
        sine1 = AbsoluteSine(12.0)
        sine2 = AbsoluteSine(24.0)

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
                s1_sample = sine1.sample(t_seconds) / 2.0
                s2_sample = sine2.sample(t_seconds) / 2.0
                uniforms.update({
                    "color": color_triangle @ np.array([s1_sample, s2_sample, 1 - s1_sample - s2_sample])
                })
                glDrawElements(GL_TRIANGLES, model.elements.size, GL_UNSIGNED_INT, ctypes.c_void_p(0))

            # tell glfw to poll and process window events
            glfw.poll_events()
            # swap frame buffer
            glfw.swap_buffers(window)
    print("Successfully reached end of main")