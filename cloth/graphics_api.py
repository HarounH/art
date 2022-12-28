from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
import glfw
import numpy as np
import logging
import contextlib
from typing import Optional, Tuple, Dict, Any
import platform as pyPlatform
import time
from dataclasses import dataclass

logger = logging.getLogger()
pressed_key_array = np.array([False] * 300, np.bool) # what ke



def debug_message_callback(source, msg_type, msg_id, severity, length, raw, user):
    # TODO: make customizable
    msg = raw[0:length]
    logger.debug(source, msg_type, msg_id, severity, msg)


def window_keypress_callback(window, key, scanCode, action, mods):
    # TODO: make customizable - allow user to specify it?
    if key == glfw.KEY_UNKNOWN:
        return

    if action == glfw.PRESS:
        logger.debug(f"key press: {key}")
        if key == glfw.KEY_ESCAPE:
            # respond escape here
            glfw.set_window_should_close(window, True)
        else:
            pressed_key_array[key] = True
    elif action == glfw.RELEASE:
        pressed_key_array[key] = False


def window_resize_callback(window, width, height):
    # TODO: make customizable - allow user to specify it?
    # TODO: keep track of width, height?
    glViewport(0, 0, width, height)


def window_cursor_callback(window, x_pos, y_pos):
    # TODO: make customizable - allow user to specify it?
    pass

def window_scroll_callback(window, x_offset, y_offset):
    # TODO: make customizable - allow user to specify it?
    pass

def compile_shader(shader_type, shader_source: str) -> Optional[int]:
    """compile a shader:
    Args:
        shader_type: takes in `GL_VERTEX_SHADER` or `GL_FRAGMENT_SHADER`
        shader_source: actual shader code

    Returns:
        shader id if compilation is successful.
        None if compilation fails - logs to error
    """
    shader_id = glCreateShader(shader_type)
    glShaderSource(shader_id, shader_source)
    glCompileShader(shader_id)
    success = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
    if not success:
        info_log = glGetShaderInfoLog(shader_id)
        logger.error(f"Shader compilation failed for {shader_source=} and {info_log=}")
        return None
    return shader_id

class GraphicsAPI:
    def __init__(
        self,
        window_height: int,
        window_width: int,
        name: Optional[str] = None,
        background_colour: Tuple[float, float, float, float] = (0.3, 0.3, 0.3, 1.0),
    ):
        self.window_height = window_height
        self.window_width = window_width
        self.name = name
        self.background_colour = background_colour

    def should_run_then_clear(self) -> bool:
        # WARNING: two purposes
        if glfw.window_should_close(self.window):
            return False
        # set background color
        glClearColor(*(self.background_colour))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        return True

    @staticmethod
    def read_file_to_str(filename: str) -> str:
        with open(filename, "r") as f:
            data = f.read()
        return data

    @contextlib.contextmanager
    def new_vertex_array(self):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        yield vao
        # user code would go here to populate the vao
        glBindVertexArray(0)

    @contextlib.contextmanager
    def use_vao(self, vao):
        glBindVertexArray(vao)
        yield vao
        # render stuff
        glBindVertexArray(0)


    @contextlib.contextmanager
    def create_window(self):

        # initialize glfw
        glfw.init()

        # set glfw config
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        logger.info(f"Initialized glfw context using glfw.OPENGL_CORE_PROFILE {glfw.OPENGL_CORE_PROFILE}")

        if pyPlatform.system().lower() == 'darwin':
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

        # create window
        self.window = glfw.create_window(self.window_height, self.window_width, self.name, None, None)
        # make window the current context
        glfw.make_context_current(self.window)

        # enable z-buffer
        glEnable(GL_DEPTH_TEST)

        if pyPlatform.system().lower() != 'darwin':
            # enable debug output
            # doesn't seem to work on macOS
            glEnable(GL_DEBUG_OUTPUT)
            glDebugMessageCallback(GLDEBUGPROC(debug_message_callback), None)
        # set resizing callback function
        # glfw.set_framebuffer_size_callback(window, window_resize_callback)

        glfw.set_key_callback(self.window, window_keypress_callback)

        # disable cursor
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

        glfw.set_cursor_pos_callback(self.window, window_cursor_callback)
        # initialize cursor position
        cursorPos = glfw.get_cursor_pos(self.window)

        glfw.set_scroll_callback(self.window, window_scroll_callback)
        _ = glfw.get_time()

        yield self.window

        # TODO: delete buffers and programs

        # terminate glfw
        glfw.terminate()

    def make_program(self, vertex_shader: str, fragment_shader: str) -> Optional[int]:
        """ Create a gl program with two shaders linked.
        Args: vertex_shader and fragment_shader - strings containin GLSL
        Returns: program ID if successful, None otherwise (with logs to error)

        """
        vertex_shader_id = compile_shader(GL_VERTEX_SHADER, vertex_shader)
        if vertex_shader_id is None:
            logger.error('vertex shader compilation failed')
            return None

        fragment_shader_id = compile_shader(GL_FRAGMENT_SHADER, fragment_shader)
        if fragment_shader_id is None:
            logger.error('vertex shader compilation failed')
            return None

        # link shaders into a program
        program_id = glCreateProgram()
        glAttachShader(program_id, vertex_shader_id)
        glAttachShader(program_id, fragment_shader_id)
        glLinkProgram(program_id)
        linkSuccess = glGetProgramiv(program_id, GL_LINK_STATUS)
        if not linkSuccess:
            info_log = glGetProgramInfoLog(program_id)
            logger.error(f"Program Linkage Error: {info_log=}")
            return None

        # delete shaders for they are not longer useful
        glDeleteShader(vertex_shader_id)
        glDeleteShader(fragment_shader_id)
        return program_id

if __name__ == "__main__":
    api = GraphicsAPI(800, 800, "hello world")
    with api.create_window() as window:
        while True:
            if not api.should_run_then_clear():
                break
            # tell glfw to poll and process window events
            glfw.poll_events()
            # swap frame buffer
            glfw.swap_buffers(window)
    print("Successfully reached end of main")