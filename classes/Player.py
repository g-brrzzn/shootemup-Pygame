import pygame
from time import time
from pygame.locals import *

from game_engine import g_engine
from classes.Bullet import Bullet
from classes.particles.Explosion import Explosion
from constants.global_var import MAX_LIFE, CONTROLS, config, SPRITE_SIZE, PLAYER_COLOR_GREEN

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups): 
        super().__init__(*groups)
        self.shot_delay = 0.25
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.firing = False
        self.last_time = time()
        self.last_shot = self.last_time

        self.sprites = [
            g_engine.assets.get_image('player_idle1'),
            g_engine.assets.get_image('player_idle2')
        ]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect(center=pos)
        self.movement = pygame.math.Vector2()
        self.speed = config.INTERNAL_RESOLUTION[1] * 0.007
        
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
        if event.key == K_o:
            if self.shot_delay >= 0.1:
                self.shot_delay -= 0.1
        if event.key == K_l:
            if self.shot_delay < 0.25:
                self.shot_delay += 0.1
        if event.key == K_i:
            self.speed += 1
        if event.key == K_k:
            if self.speed >= 7:
                self.speed -= 1      
    

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
        Bullet.create_bullets(
            pattern='single',
            pos=self.rect.center,
            is_from_player=True,
            groups=(g_engine.player_bullets, g_engine.all_sprites),
            options={'angle': 90}  
        )
        pygame.mixer.Sound.play(g_engine.assets.get_sound('shoot'))

    def update(self, dt):
        self.last_time = time() 
        self.explosion.update(dt)
        self.animate()
        if self.moving_right: self.rect[0]  +=  round(self.speed * dt)
        if self.moving_left: self.rect[0]   -=  round(self.speed * dt)
        if self.moving_up: self.rect[1]     -=  round(self.speed * dt)
        if self.moving_down: self.rect[1]   +=  round(self.speed * dt)

        if self.rect[0] > config.INTERNAL_RESOLUTION[0] - self.rect.width: self.rect[0] = config.INTERNAL_RESOLUTION[0] - self.rect.width
        if self.rect[0] < 0: self.rect[0] = 0
        if self.rect[1] > config.INTERNAL_RESOLUTION[1] - self.rect.height: self.rect[1] = config.INTERNAL_RESOLUTION[1] - self.rect.height
        if self.rect[1] < 0: self.rect[1] = 0
        
        if self.firing and self.last_time - self.last_shot > self.shot_delay:
            self.fire()
            self.last_shot = self.last_time
    
                
    def draw(self, surf):
        surf.blit(self.image, self.rect)
        self.explosion.draw(surf)
        
    def take_damage(self):
        self.life -= 1
        self.explosion.create(self.rect.center[0] - SPRITE_SIZE / 2, self.rect.center[1] - SPRITE_SIZE, PLAYER_COLOR_GREEN, speed=-5)
        pygame.mixer.Sound.play(g_engine.assets.get_sound('hit'))

    def getLife(self):      return self.life
    def setLife(self, life): self.life = life
    
    def getX(self):         return self.rect.x
    def getY(self):         return self.rect.y