import pygame
import math
import random
from constants.global_var import config, PLAYER_COLOR_GREEN
from game_engine import g_engine

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos, p_type, *groups):
        super().__init__(*groups)
        self.p_type = p_type
        
        if p_type == "life":
            self.base_img = g_engine.assets.get_image("life_powerup")
            self.glow_color = (255, 50, 50)  
        elif p_type == "weapon":
            self.base_img = g_engine.assets.get_image("weapon_powerup")
            self.glow_color = PLAYER_COLOR_GREEN
        else:
            self.base_img = pygame.Surface((32, 16), pygame.SRCALPHA)
            self.base_img.fill((255, 255, 255))
            self.glow_color = (200, 200, 200)

        glow_radius = 35
        surf_size = (glow_radius * 2, glow_radius * 2)
        self.original_image = pygame.Surface(surf_size, pygame.SRCALPHA)
        
        for r in range(glow_radius, 0, -2):
            alpha = 15  
            temp_surf = pygame.Surface(surf_size, pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*self.glow_color, alpha), (glow_radius, glow_radius), r)
            self.original_image.blit(temp_surf, (0, 0))
        
        item_rect = self.base_img.get_rect(center=(glow_radius, glow_radius))
        self.original_image.blit(self.base_img, item_rect)

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=pos)
        
        self.hitbox = self.base_img.get_rect(center=pos)

        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)

        self.speed_y = random.uniform(100.0, 130.0) 
        self.sway_speed = random.uniform(2.0, 3.5)
        self.sway_amp = random.uniform(40.0, 75.0)
        self.time_offset = random.uniform(0.0, 100.0)

    def update(self, dt):
        t = (pygame.time.get_ticks() / 1000.0) + self.time_offset

        self.y += self.speed_y * dt
        self.x += math.cos(t * self.sway_speed) * self.sway_amp * dt

        w = config.INTERNAL_RESOLUTION[0]
        self.x = max(30, min(w - 30, self.x))

        self.rect.center = (round(self.x), round(self.y))
        self.hitbox.center = self.rect.center

        scale_factor = 1.0 + 0.1 * math.sin(t * 8)
        new_w = int(self.original_image.get_width() * scale_factor)
        new_h = int(self.original_image.get_height() * scale_factor)
        
        self.image = pygame.transform.scale(self.original_image, (new_w, new_h))
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.rect.top > config.INTERNAL_RESOLUTION[1] + 100:
            self.kill()