import pygame
import math
from constants.global_var import config

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos, p_type, color, *groups):
        super().__init__(*groups)
        
        self.p_type = p_type  
        self.image = pygame.Surface((32, 16))
        self.image.fill(color) 
        self.rect = self.image.get_rect(center=pos)
        self.speed = 3

    def update(self, dt):
        self.rect.y += self.speed * dt
        alpha = 150 + 105 * math.sin(pygame.time.get_ticks() * 0.01)
        self.image.set_alpha(int(alpha))

        if self.rect.top > config.INTERNAL_RESOLUTION[1]:
            self.kill()