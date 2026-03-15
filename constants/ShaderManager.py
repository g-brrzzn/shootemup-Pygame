import moderngl
import pygame
from constants import moderngl_utils

BASE_FRAGMENT_SHADER = """
#version 330 core

uniform sampler2D surface;

in vec2 uvs;
out vec4 f_color;

void main() {
    vec4 base_color = texture(surface, uvs);

    vec2 center_uv = uvs - 0.5;
    float dist = length(center_uv);
    float vignette = smoothstep(0.8, 0.35, dist);

    float scanline = sin(uvs.y * 1400.0) * 0.015; 
    
    vec3 final_rgb = base_color.rgb * (vignette - scanline);

    f_color = vec4(final_rgb, base_color.a);
}
"""

class ShaderManager:
    def __init__(self, internal_res: tuple, screen_res: tuple):
        self.context = moderngl_utils.initialize_context()
        self.texture_handler = moderngl_utils.TextureHandler(10)
        self.surface = moderngl_utils.GLSurface(
            internal_res, 
            screen_res, 
            self.texture_handler, 
            fragment_shader=BASE_FRAGMENT_SHADER
        )
        
    def draw(self, offset: tuple = (0, 0)):
        self.texture_handler.clear_memory()
        
        screen_w, screen_h = self.surface.screen_size
        center_pos = (
            (screen_w / 2) + offset[0], 
            (screen_h / 2) + offset[1]
        )
        
        self.surface.draw(position=center_pos)
        
    def get_draw_surface(self) -> pygame.Surface:
        return self.surface.surface