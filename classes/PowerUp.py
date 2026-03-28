import pygame
import math
from time import time
from constants.global_var import config

from game_engine import g_engine


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos, p_type, *groups):
        super().__init__(*groups)

        self.p_type = p_type
        self.image = pygame.Surface((32, 16))
        if p_type == "life":
            img = g_engine.assets.images["life_powerup"]
        elif p_type == "weapon":
            img = g_engine.assets.images["weapon_powerup"]
        else:
            img = self.image.fill((255, 255, 255))  # Default white if type is unknown
        self.image = img
        self.rect = self.image.get_rect(center=pos)
        self.speed = 225

    def update(self, dt):
        self.rect.y += self.speed * dt
        alpha = 150 + 105 * math.sin(pygame.time.get_ticks() * 0.01)
        self.image.set_alpha(int(alpha))

        if self.rect.top > config.INTERNAL_RESOLUTION[1]:
            self.kill()
