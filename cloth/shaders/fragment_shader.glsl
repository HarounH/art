#version 330 core
in vec2 o_TexPos;
out vec4 color;

uniform sampler2D textureSample;

void main(){
    vec4 sampled = texture(textureSample, o_TexPos);
    color = sampled;
}