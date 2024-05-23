import pygame
from time import time
import pygame.image

from classes.Bullet import Bullet
from constants.global_func import *
from constants.global_var import *
from constants.global_imports import *

class Player:
    def __init__(self, pos):
        self.shot_delay = 0.25
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.firing = False
        self.rect = pygame.math.Vector2()
        
        self.last_time = time()
        self.last_shot = self.last_time
        self.sprites = []
        for i in range(1, 3):
            self.sprite = pygame.image.load(f'assets/player_idle{i}.png').convert()
            self.sprite = pygame.transform.scale(self.sprite, (SCALED_SPRITE_SIZE, 24*4))
            self.sprite.set_colorkey((0, 0, 0))
            self.sprites.append(self.sprite)
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect(center=pos)
        self.movement = pygame.math.Vector2()
        self.speed = 7
        
        self.life = MAX_LIFE
        self.last_damage = self.last_time
        self.explosion = Explosion()

    def animate(self):
        self.current_sprite += 0.07
        if self.current_sprite >= len(self.sprites): self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def get_input(self, event):
        if event.key in CONTROLS['LEFT']:
            self.moving_left = True
        if event.key in CONTROLS['RIGHT']:
            self.moving_right = True
        if event.key in CONTROLS['DOWN']:
            self.moving_down = True
        if event.key in CONTROLS['UP']:
            self.moving_up = True
        if event.key in CONTROLS['FIRE']:
            self.firing = True

    def get_input_keyup(self, event):
        if event.key in CONTROLS['LEFT']:
            self.moving_left = False
        if event.key in CONTROLS['RIGHT']:
            self.moving_right = False
        if event.key in CONTROLS['DOWN']:
            self.moving_down = False
        if event.key in CONTROLS['UP']:
            self.moving_up = False
        if event.key in CONTROLS['FIRE']:
            self.firing = False

    def fire(self):
        Bullet(self.rect.center[0] - SPRITE_SIZE / 2, self.rect.center[1] - SPRITE_SIZE, 1)
        pygame.mixer.Sound.play(pygame.mixer.Sound('assets/shoot.mp3'))

    def update(self, dt, last_time):
        self.last_time = last_time
        if self.moving_right: self.rect[0]  +=  round(self.speed * dt)
        if self.moving_left: self.rect[0]   -=  round(self.speed * dt)
        if self.moving_up: self.rect[1]     -=  round(self.speed * dt)
        if self.moving_down: self.rect[1]   +=  round(self.speed * dt)

        if self.rect[0] > config.window_size[0] - self.rect.width: self.rect[0] = config.window_size[0] - self.rect.width
        if self.rect[0] < 0: self.rect[0] = 0
        if self.rect[1] > config.window_size[1] - self.rect.height: self.rect[1] = config.window_size[1] - self.rect.height
        if self.rect[1] < 0: self.rect[1] = 0
        
        if self.firing and self.last_time - self.last_shot > self.shot_delay: self.fire(); self.last_shot = self.last_time
        
        

        for bloc in Bullet.enemylocs:
            if self.rect.x - self.rect.width/2+25 < bloc[0] < self.rect.x + self.rect.height/2 and self.rect.y - self.rect.height/2+30 < bloc[1] < self.rect.y + self.rect.height/2:
                self.life -= 1 
                self.explosion.create(bloc[0], bloc[1], 1)
                Bullet.enemylocs.remove(bloc)
                
        self.animate()

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    def getLife(self):       return self.life
    def setLife(self, life): self.life = life
    
    def getX(self):       return self.rect.x
    def getY(self):       return self.rect.y

