#version 330 core
in vec3 o_Pos;
in vec3 o_Normal;
in vec2 o_TexPos;
out vec4 color;

uniform sampler2D textureSample;
uniform vec3 light_source_position;

void main(){
    vec4 sampled = texture(textureSample, o_TexPos);

    vec3 light_direction = normalize(light_source_position - o_Pos);
    float diffusion = max(0.0, dot(normalize(o_Normal), light_direction));

    color = vec4(diffusion * vec3(sampled.xyz), 1.0);
}