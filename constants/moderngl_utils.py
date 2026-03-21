import pygame
import moderngl
import array

VERTEX_SHADER = """
#version 330 core

in vec2 vertex;
in vec2 texture_coordinates;
out vec2 uvs;

void main() {
    uvs = texture_coordinates;
    gl_Position = vec4(vertex.x, vertex.y, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core

uniform sampler2D surface;

in vec2 uvs;
out vec4 f_color;

void main() {
    f_color = texture(surface, uvs);
}
"""

def from_surface_to_texture(gl_context: moderngl.Context, surface: pygame.Surface):
    texture = gl_context.texture(surface.get_size(), 4)
    texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
    texture.write(pygame.image.tobytes(surface, "RGBA", True))
    return texture

def create_texture(gl_context: moderngl.Context, size: tuple):
    texture = gl_context.texture(size, 4)
    texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
    return texture

def write_to_texture(texture: moderngl.Texture, surface: pygame.Surface):
    texture.write(pygame.image.tobytes(surface, "RGBA", True))

def create_data_for_quad_buffer(size: tuple, position: tuple, screen_size: tuple):
    def convert_coord(c: float, screen_half_size: float):
        return (c - screen_half_size) / screen_half_size
    
    screen_half_x = screen_size[0] / 2.0
    screen_half_y = screen_size[1] / 2.0
    
    half_w = screen_size[0] / 2.0
    half_h = screen_size[1] / 2.0

    return array.array("f", [
        convert_coord(position[0] - half_w, screen_half_x), convert_coord(position[1] - half_h, screen_half_y), 0.0, 0.0,
        convert_coord(position[0] + half_w, screen_half_x), convert_coord(position[1] - half_h, screen_half_y), 1.0, 0.0,
        convert_coord(position[0] - half_w, screen_half_x), convert_coord(position[1] + half_h, screen_half_y), 0.0, 1.0,
        convert_coord(position[0] + half_w, screen_half_x), convert_coord(position[1] + half_h, screen_half_y), 1.0, 1.0  
    ])

class TextureHandler:
    def __init__(self, reserved_slots: int):
        self.gl_context = moderngl.get_context()
        self.reserved_slots = reserved_slots
        self.reserved_texture_slots = []
        self.texture_slots = []

    def write_to_memory(self, texture: moderngl.Texture):
        slot = len(self.texture_slots) + self.reserved_slots
        self.texture_slots.append(texture)
        texture.use(slot)
        return slot
    
    def write_to_reserved_memory(self, texture: moderngl.Texture):
        slot = len(self.reserved_texture_slots)
        self.reserved_texture_slots.append(texture)
        texture.use(slot)
        return slot
    
    def clear_memory(self, all: bool = False):
        for texture in self.texture_slots:
            texture.release()
        self.texture_slots.clear()

        if all:
            for texture in self.reserved_texture_slots:
                texture.release()
            self.reserved_texture_slots.clear()

class Shader:
    def __init__(self, vertex_shader: str, fragment_shader: str):
        self.gl_context = moderngl.get_context()
        self.program = self.gl_context.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        self.quad_buffer = self.gl_context.buffer(data=create_data_for_quad_buffer((2, 2), (1, 1), (2, 2)), dynamic=True)
        self.vertex_array = self.gl_context.vertex_array(self.program, [(self.quad_buffer, "2f 2f", "vertex", "texture_coordinates")])
        self.last_draw_data = ()

    def draw(self, texture_slot: int, size: tuple, screen_size: tuple, position: tuple | None = None, **kwargs):
        if (size, screen_size, position) != self.last_draw_data:
            if position is None:
                position = (screen_size[0] / 2, screen_size[1] / 2)
            self.quad_buffer.write(create_data_for_quad_buffer(size, position, screen_size))
            self.last_draw_data = (size, screen_size, position)
            
        if 'surface' in self.program:
            self.program['surface'].value = texture_slot
            
        for key, arg in kwargs.items():
            if key in self.program:
                self.program[key].value = arg
                
        self.vertex_array.render(mode=moderngl.TRIANGLE_STRIP)

class GLSurface:
    id = 0

    def __init__(self, size: tuple, screen_size: tuple, texture_handler: TextureHandler, vertex_shader: str = VERTEX_SHADER, fragment_shader: str = FRAGMENT_SHADER, position: tuple | None = None):
        self.id = GLSurface.id
        GLSurface.id += 1

        self.gl_context = moderngl.get_context()
        self.texture_handler = texture_handler
        self.shader = Shader(vertex_shader, fragment_shader)

        self.size = size
        self.screen_size = screen_size
        self.position = position

        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.texture = create_texture(self.gl_context, size)
        self.texture_slot = self.texture_handler.write_to_reserved_memory(self.texture)

    def draw(self, **kwargs):
        write_to_texture(self.texture, self.surface)
        current_position = kwargs.pop('position', self.position)
        self.shader.draw(self.texture_slot, self.size, self.screen_size, current_position, **kwargs)

    def clear(self):
        self.surface.fill((0, 0, 0, 0))

class RenderBuffer:
    def __init__(self, size: tuple, texture_handler: TextureHandler, vertex_shader: str = VERTEX_SHADER, fragment_shader: str = FRAGMENT_SHADER):
        self.size = size
        self.gl_context = moderngl.get_context()
        self.texture_handler = texture_handler

        self.texture = create_texture(self.gl_context, size)
        self.texture_slot = texture_handler.write_to_reserved_memory(self.texture)
        self.frame_buffer = self.gl_context.framebuffer(color_attachments=[self.texture])
        self.shader = Shader(vertex_shader, fragment_shader)
        
    def set_as_target(self, clear: bool = True):
        self.frame_buffer.use()
        if clear:
            self.frame_buffer.clear(0, 0, 0, 1)

    def draw(self, target: moderngl.Framebuffer, **kwargs):
        target.use()
        self.shader.draw(self.texture_slot, self.size, self.size, **kwargs)

def initialize_context():
    context = moderngl.create_context()
    context.enable(moderngl.BLEND)
    context.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
    return context

def clear_context(context: moderngl.Context):
    context.clear(0, 0, 0, 1)