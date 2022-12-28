#version 330 core
layout (location = 0) in vec4 i_Pos;
layout (location = 1) in vec2 i_TexPos;
out vec2 o_TexPos;
void main()
{
   gl_Position = i_Pos;
   o_TexPos = i_TexPos;
}
