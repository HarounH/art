#version 330 core
layout (location = 0) in vec4 aPos;
out float alpha;
void main()
{
   gl_Position = aPos;
   alpha = aPos.x + 0.5;
}
