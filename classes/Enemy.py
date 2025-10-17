import pygame
import math
from random import choice, randint
from time import time

from game_engine import g_engine
from classes.Bullet import Bullet
from classes.particles.Explosion import Explosion
from constants.global_var import config, SCALED_SPRITE_SIZE

class EnemyBase(pygame.sprite.Sprite):
    instancelist = []

    def __init__(self, pos, sprite_files_keys, *groups):
        super().__init__(*groups) 
        self.x, self.y = pos
        self.instancelist.append(self)
        self.sprites = self.load_sprites(sprite_files_keys) 
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.direction = choice([True, False])
        self.y_direction = False
        self.explosion = Explosion()
        self.explosion.create(self.rect.centerx, self.rect.centery, speed=-5)
        
        self.last_time = time()
        self.last_damage = self.last_time
        
        self.life = 3
        self.speed = config.INTERNAL_RESOLUTION[1] * 0.005
        self.weight = 1
        
    @classmethod
    def load_assets(cls, assets_manager):
        cls.hit_sound = assets_manager.get_sound('hit')

    def load_sprites(self, sprite_keys):
        sprites = []
        for key in sprite_keys: 
            sprite = g_engine.assets.get_image(key) 
            sprites.append(sprite)
        return sprites

    def animate(self):
        self.current_sprite += 0.07
        if self.current_sprite >= len(self.sprites): self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def kill(self):
        super().kill() 
        try:
            EnemyBase.instancelist.remove(self) 
        except ValueError:
            pass
        
    def damage(self):
        self.explosion.create(self.x, self.y)
        if self.life <= 1: self.kill()
        else: self.life -= 1
                
    def shoot(self):
        for _ in range(self.weight):
            if randint(0, 1000) < 2:
                Bullet.create_bullets(
                    pattern='single',
                    pos=self.rect.center,
                    is_from_player=False,
                    groups=(g_engine.enemy_bullets, g_engine.all_sprites),
                    options={'angle': -90}
                )
            
    def move(self, dt):
        if self.y > (config.INTERNAL_RESOLUTION[1] - (SCALED_SPRITE_SIZE + 10)): 
            g_engine.player.take_damage()
        if randint(0, 500 * self.weight) < 1:
            self.y_direction = True
            self.old_y = self.y
        if self.y_direction:
            if self.y < self.old_y + SCALED_SPRITE_SIZE:
                self.y += self.speed * dt
            else:
                self.y_direction = False
        else:
            if self.direction:
                self.x += self.speed * dt
                if self.x > config.INTERNAL_RESOLUTION[0] - (config.INTERNAL_RESOLUTION[0] * (self.weight * 0.1)):
                    self.direction = False
            else:
                self.x -= self.speed * dt
                if self.x < (config.INTERNAL_RESOLUTION[0] * (self.weight * 0.1)):
                    self.direction = True
    
    def update(self, dt):
        self.move(dt)   
        self.shoot() 
        self.explosion.update(dt)

        self.rect.topleft = (self.x, self.y)
        self.animate()

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        self.explosion.draw(surf)

    @staticmethod
    def spawn_enemy(n, enemy_class): 
        for _ in range(n):
            x = randint(0, config.INTERNAL_RESOLUTION[0])
            y = config.INTERNAL_RESOLUTION[1] / 2 - 320
            enemy_class((x, y), g_engine.all_enemies, g_engine.all_sprites) 

class Enemy1(EnemyBase):
    def __init__(self, pos, *groups):
        super().__init__(pos, ['enemy1_1', 'enemy1_2'], *groups)
        self.life = 1
        self.weight = 1

    def move(self, dt):
        return super().move(dt)
    
    def update(self, dt):
        super().update(dt)


class Enemy2(EnemyBase):
    def __init__(self, pos, *groups):
        super().__init__(pos, ['enemy2_1', 'enemy2_2'], *groups)
        self.life = 3
        self.weight = 2
        self.speed = self.speed * 0.75
        self.x_direction = 1

    def move(self, dt):
        weight = 2
        if self.y > (config.INTERNAL_RESOLUTION[1] - (SCALED_SPRITE_SIZE + 10)): 
            g_engine.player.setLife(g_engine.player.getLife() - 1)

        if randint(0, 500 * weight) < 1:
            self.y_direction = True
            self.old_y = self.y
            self.x_direction = choice([-1, 1])

        if self.y_direction:
            if self.y < self.old_y + SCALED_SPRITE_SIZE:
                self.y += self.speed * dt
            else:
                self.y_direction = False
        else:
            time_elapsed = pygame.time.get_ticks() / 1000.0
            frequency = 0.5 
            
            self.x += self.speed * dt * math.sin(2 * math.pi * frequency * time_elapsed) * self.x_direction
            self.y += self.speed * dt * math.sin(2 * math.pi * frequency * time_elapsed)
            
            if self.x < 0: self.x = 0
            elif self.x > config.INTERNAL_RESOLUTION[0] - SCALED_SPRITE_SIZE: self.x = config.INTERNAL_RESOLUTION[0] - SCALED_SPRITE_SIZE
            
            if self.y > config.INTERNAL_RESOLUTION[1] - SCALED_SPRITE_SIZE:
                self.y = config.INTERNAL_RESOLUTION[1] - SCALED_SPRITE_SIZE
                self.y_direction = False
    
    def update(self, dt):
        super().update(dt)
        
        
class Enemy3(EnemyBase):
    def __init__(self, pos, *groups):
        super().__init__(pos, ['enemy3_1', 'enemy3_2'], *groups)
        self.life = 5
        self.weight = 3
        self.speed = self.speed * 0.5
        self.xy_direction = choice([-1, 1])

    def move(self, dt):
        weight = 3
        if self.y > (config.INTERNAL_RESOLUTION[1] - (SCALED_SPRITE_SIZE + 10)): 
            g_engine.player.setLife(g_engine.player.getLife() - 1)

        if randint(0, 500 * weight) < 1:
            self.y_direction = True
            self.old_y = self.y

        if self.y_direction:
            if self.y < self.old_y + SCALED_SPRITE_SIZE:
                self.y += self.speed * dt
            else:
                self.y_direction = False
        else:
            time_elapsed = pygame.time.get_ticks() / 1000.0
            frequency = 0.5 
            
            self.x += self.speed * dt * math.sin(2 * math.pi * frequency * time_elapsed) * self.xy_direction
            self.y += self.speed * dt * math.cos(2 * math.pi * frequency * time_elapsed) * self.xy_direction
            
            if self.x < 0: self.x = 0
            elif self.x > config.INTERNAL_RESOLUTION[0] - SCALED_SPRITE_SIZE: self.x = config.INTERNAL_RESOLUTION[0] - SCALED_SPRITE_SIZE
            
            if self.y > config.INTERNAL_RESOLUTION[1] - SCALED_SPRITE_SIZE:
                self.y = config.INTERNAL_RESOLUTION[1] - SCALED_SPRITE_SIZE
                self.y_direction = False
    
    def update(self, dt):
        super().update(dt)