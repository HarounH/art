from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
import argparse
from cloth.graphics_api import GraphicsAPI
from cloth.static_cloth import StaticCloth
import glfw
import platform
import ctypes


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertex_shader_path", default="cloth/shaders/vertex_shader.glsl", type=str, help="Relative path to file with vertex shader")
    parser.add_argument("--fragment_shader_path", default="cloth/shaders/fragment_shader.glsl", type=str, help="Relative path to file with fragment shader")
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    # TODO: use args
    model = StaticCloth(step_size=0.5)
    api = GraphicsAPI(800, 800, "cloth rendering")

    # TODO: shader
    # ASSERT: gl is initialized
    with api.create_window() as window:
        # TODO: VBO
        vertices_vbo = VBO(model.vertices, usage='GL_STATIC_DRAW')
        vertices_vbo.create_buffers()

        # create and bind VAO - needed to enable VertexAttrib
        with api.new_vertex_array() as vertices_vao:
            # bind VBO then buffer into GL
            vertices_vbo.bind()
            vertices_vbo.copy_data()
            # arguments: index, size, type, normalized, stride, pointer
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)


        program = api.make_program(
            vertex_shader=api.read_file_to_str(args.vertex_shader_path),
            fragment_shader=api.read_file_to_str(args.fragment_shader_path),
        )
        if program is None:
            raise RuntimeError("Program making failed")
        while True:
            if not api.should_run_then_clear():
                break

            # use our own rendering program
            glUseProgram(program)

            # draw vertices
            glBindVertexArray(vertices_vao)
            glDrawArrays(GL_TRIANGLES, 0, 3)  # TODO: 3 is a property of model.vertices

            # tell glfw to poll and process window events
            glfw.poll_events()
            # swap frame buffer
            glfw.swap_buffers(window)
    print("Successfully reached end of main")