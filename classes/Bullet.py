import pygame
import pygame.image

from constants.global_func import *
from constants.global_var import *
from constants.global_imports import *

class Bullet(pygame.sprite.Sprite):
    player_image = None
    enemy_image = None

    @classmethod
    def load_assets(cls, assets_manager):
        cls.player_image = assets_manager.get_image('bullet_player')
        cls.enemy_image = assets_manager.get_image('bullet_enemy')

    def __init__(self, pos, direction, is_from_player, *groups):
        super().__init__(*groups)
        
        self.is_from_player = is_from_player
        self.direction = direction # 1:UP, 2:LEFT, 3:DOWN, 4:RIGHT
        
        if self.is_from_player:
            self.image = Bullet.player_image
            self.speed = 12
        else:
            self.image = Bullet.enemy_image
            self.speed = 4
            
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        if self.direction == 1: self.rect.y -= round(self.speed * dt)
        elif self.direction == 2: self.rect.x -= round(self.speed * dt)
        elif self.direction == 3: self.rect.y += round(self.speed * dt)
        elif self.direction == 4: self.rect.x += round(self.speed * dt)
        
        if not pygame.display.get_surface().get_rect().colliderect(self.rect):
            self.kill()

    @classmethod
    def move_bullet(cls, loc, dt, is_player):
        speed = cls.speed if is_player else cls.enemyspeed
        # 1-UP, 2-LEFT, 3-DOWN, 4-RIGHT
        if loc[2] == 1: loc[1] -= round(speed * dt)
        elif loc[2] == 2: loc[0] -= round(speed * dt)
        elif loc[2] == 3: loc[1] += round(speed * dt)
        elif loc[2] == 4: loc[0] += round(speed * dt)

    @classmethod
    def is_off_screen(cls, loc):
        return (loc[0] > config.window_size[0] + 10 or
                loc[0] < -10 or
                loc[1] > config.window_size[1] + 10 or
                loc[1] < -10)

    @classmethod
    def draw_all(cls, surf):
        for loc in cls.locs:
            cls.rect.topleft = (loc[0], loc[1])
            surf.blit(cls.image, cls.rect)
        for loc in cls.enemylocs:
            cls.rect.topleft = (loc[0], loc[1])
            surf.blit(cls.enemyimage, cls.rect)