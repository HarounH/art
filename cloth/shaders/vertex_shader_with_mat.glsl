#version 330 core
layout (location = 0) in vec4 i_Pos;
layout (location = 1) in vec2 i_TexPos;
out vec2 o_TexPos;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;

void main()
{
    gl_Position = projection_matrix * view_matrix * i_Pos;
    o_TexPos = i_TexPos;
}