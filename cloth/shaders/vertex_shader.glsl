#version 330 core
layout (location = 0) in vec4 aPos;
out vec4 color;
void main()
{
   gl_Position = aPos;
   color = vec4(aPos.x + 0.5, 0.0, 0.0, 1.0);
}
