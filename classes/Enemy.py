import pygame
from random import choice, randint
from time import time
import pygame.image

from classes.Bullet import Bullet
from classes.Player import Player
from constants.global_func import *
from constants.global_var import *
from constants.global_imports import *

class EnemyBase:
    instancelist = []

    def __init__(self, pos, sprite_files_keys, assets_manager):
        self.assets = assets_manager
        self.x, self.y = pos
        self.instancelist.append(self)
        self.sprites = self.load_sprites(sprite_files_keys) 
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.direction = choice([True, False])
        self.y_direction = False
        self.explosion = Explosion()
        
        self.last_time = time()
        self.last_damage = self.last_time
        
        self.life = 3
        self.speed = config.window_size[1] * 0.005
        
    @classmethod
    def load_assets(cls, assets_manager):
        cls.hit_sound = assets_manager.get_sound('hit')

    def load_sprites(self, sprite_keys):
        sprites = []
        for key in sprite_keys: 
            sprite = self.assets.get_image(key) 
            sprites.append(sprite)
        return sprites

    def animate(self):
        self.current_sprite += 0.07
        if self.current_sprite >= len(self.sprites): self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def kill(self):
        try: self.instancelist.remove(self)
        except: pass
        
    def damage(self):
        if self.life <= 1: self.kill()
        else: self.life -= 1

    def death(self):
        for bloc in Bullet.locs:
            if self.x - self.rect.width/2 < bloc[0] < self.x+10 + self.rect.height and self.y - self.rect.height < bloc[1] < self.y + self.rect.height:
                self.explosion.create(self.rect.center[0] - SPRITE_SIZE / 2, self.rect.center[1] - SPRITE_SIZE)
                pygame.mixer.Sound.play(EnemyBase.hit_sound) 
                self.damage()
                Bullet.locs.remove(bloc)
                
    def damage_player(self, player, assets):
        for e in self.instancelist:
            if player.getX() - self.rect.width/2 < e.rect.x < player.getX() + self.rect.width/2 and player.getY() - self.rect.height/2 < e.rect.y < player.getY() + self.rect.height/2:
                player.take_damage(assets)
                
    def shoot(self, weight):
        for _ in range(weight):
            if randint(0, 1000) < 2:
                Bullet(self.rect.center[0] - SPRITE_SIZE / 2, self.rect.center[1] - SPRITE_SIZE, 3, False)
              
    def move(self, dt, player, weight):
        if self.y > (config.window_size[1] - (SCALED_SPRITE_SIZE + 10)): player.setLife(player.getLife() - 1)
        
        if randint(0, 500 * weight) < 1:
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
                if self.x > config.window_size[0] - (config.window_size[0] * (weight * 0.1)):
                    self.direction = False
            else:
                self.x -= self.speed * dt
                if self.x < (config.window_size[0] * (weight * 0.1)):
                    self.direction = True
    
    def update(self, dt, player, assets, weight):
        self.death()
        self.move(dt, player)
        self.damage_player(player, assets)
        self.shoot(weight)
        self.explosion.update(dt)

        self.rect[0] = self.x
        self.rect[1] = self.y
        
        if (self.x > config.window_size[0]+100 or self.x < -100 or self.y > config.window_size[1] or self.y < -100) and ((self.last_time - self.last_damage) > 1): 
            self.last_damage = self.last_time
            self.damage()

        self.animate()

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        self.explosion.draw(surf)

    @staticmethod
    def spawn_enemy(n, enemy_class, assets_manager):
        for _ in range(n):
            x = randint(0, config.window_size[0])
            y = config.window_size[1] / 2 - 320
            enemy_class((x, y), assets_manager) 

class Enemy1(EnemyBase):
    def __init__(self, pos, assets_manager):
        sprite_keys = ['enemy1_1', 'enemy1_2']
        super().__init__(pos, sprite_keys, assets_manager)
        self.life = 1

    def move(self, dt, player):
        return super().move(dt, player, 1)
    
    def update(self, dt, player, assets): 
        return super().update(dt, player, assets, 1)


class Enemy2(EnemyBase):
    def __init__(self, pos, assets_manager):
        sprite_keys = ['enemy2_1', 'enemy2_2'] 
        super().__init__(pos, sprite_keys, assets_manager)
        self.life = 3
        self.speed = self.speed * 0.75
        self.x_direction = 1

    def move(self, dt, player):
        weight = 2
        if self.y > (config.window_size[1] - (SCALED_SPRITE_SIZE + 10)): player.setLife(player.getLife() - 1)

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
            elif self.x > config.window_size[0] - SCALED_SPRITE_SIZE: self.x = config.window_size[0] - SCALED_SPRITE_SIZE
            
            if self.y > config.window_size[1] - SCALED_SPRITE_SIZE:
                self.y = config.window_size[1] - SCALED_SPRITE_SIZE
                self.y_direction = False
    
    def update(self, dt, player, assets): 
        return super().update(dt, player, assets, 2)
        
        
class Enemy3(EnemyBase):
    def __init__(self, pos, assets_manager):
        sprite_keys = ['enemy3_1', 'enemy3_2']
        super().__init__(pos, sprite_keys, assets_manager)
        self.life = 5
        self.speed = self.speed * 0.5
        self.xy_direction = choice([-1, 1])

    def move(self, dt, player):
        weight = 3
        if self.y > (config.window_size[1] - (SCALED_SPRITE_SIZE + 10)): player.setLife(player.getLife() - 1)

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
            elif self.x > config.window_size[0] - SCALED_SPRITE_SIZE: self.x = config.window_size[0] - SCALED_SPRITE_SIZE
            
            if self.y > config.window_size[1] - SCALED_SPRITE_SIZE:
                self.y = config.window_size[1] - SCALED_SPRITE_SIZE
                self.y_direction = False
    
    def update(self, dt, player, assets): 
        return super().update(dt, player, assets, 3)