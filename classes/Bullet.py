import pygame
import pygame.image

from constants.global_func import *
from constants.global_var import *
from constants.global_imports import *

class Bullet:    
    locs = []
    enemylocs = []
    speed = 12
    enemyspeed = 4

    def __init__(self, rectx, recty, direction, isFromPlayer=True):
        if direction < 5:
            if isFromPlayer:
                self.locs.append([rectx, recty, direction, isFromPlayer])
            else: self.enemylocs.append([rectx, recty, direction, isFromPlayer])

    @classmethod
    def load_assets(cls, assets_manager):
        cls.image = assets_manager.get_image('bullet_player')
        cls.enemyimage = assets_manager.get_image('bullet_enemy')
        cls.rect = cls.image.get_rect()
    
    @classmethod
    def update(cls, dt):
        for loc in cls.locs[:]:
            cls.move_bullet(loc, dt, is_player=True)
            if cls.is_off_screen(loc):
                cls.locs.remove(loc)

        for loc in cls.enemylocs[:]:
            cls.move_bullet(loc, dt, is_player=False)
            if cls.is_off_screen(loc):
                cls.enemylocs.remove(loc)

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