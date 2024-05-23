import pygame
import pygame.image

from constants.global_func import *
from constants.global_var import *
from constants.global_imports import *

class Bullet:
    image = pygame.image.load('assets/Bullet.png').convert()
    image.set_colorkey((0, 0, 0))
    image = pygame.transform.scale(image, (SPRITE_SIZE, SPRITE_SIZE))
    rect = image.get_rect()
    
    enemyimage = pygame.image.load('assets/enemy_bullet.png').convert()
    enemyimage.set_colorkey((0, 0, 0))
    enemyimage = pygame.transform.scale(enemyimage, (SPRITE_SIZE, SPRITE_SIZE))
    
    locs = []
    enemylocs = []
    speed = 12
    enemyspeed = 4

    def __init__(self, rectx, recty, direction, isFromPlayer=True):
        if direction < 5:
            if isFromPlayer:
                self.locs.append([rectx, recty, direction, isFromPlayer])
            else: self.enemylocs.append([rectx, recty, direction, isFromPlayer])

    def moveBullets(self, loc, dt, surf):
        if loc[3]: speed = self.speed
        else:      speed = self.enemyspeed
        
        # 1 - UP; 2 - LEFT; 3 - DOWN; 4 - RIGHT;
        if   loc[2] == 1: loc[1] -= round(speed * dt)
        elif loc[2] == 2: loc[0] -= round(speed * dt)
        elif loc[2] == 3: loc[1] += round(speed * dt)
        elif loc[2] == 4: loc[0] += round(speed * dt)

        try:
            if loc[3]:
                if loc[0] > config.window_size[0] + 1: self.locs.remove(loc)
                if loc[0] < 0 - self.rect.height: self.locs.remove(loc)
                if loc[1] > config.window_size[1] + 1: self.locs.remove(loc)
                if loc[1] < 0 - self.rect.height: self.locs.remove(loc)
            else: 
                if loc[0] > config.window_size[0] + 1: self.enemylocs.remove(loc)
                if loc[0] < 0 - self.rect.height: self.enemylocs.remove(loc)
                if loc[1] > config.window_size[1] + 1: self.enemylocs.remove(loc)
                if loc[1] < 0 - self.rect.height: self.enemylocs.remove(loc)
        except: pass

        self.rect[0] = loc[0]
        self.rect[1] = loc[1]
        self.draw(surf, loc[3])
    
    def update(self, dt, surf):
        
        for loc in self.locs:
            self.moveBullets(loc, dt, surf)
        for loc in self.enemylocs:
            self.moveBullets(loc, dt, surf)

    def draw(self, surf, isFromPlayer):
        if isFromPlayer: surf.blit(self.image, self.rect)
        else: surf.blit(self.enemyimage, self.rect)
