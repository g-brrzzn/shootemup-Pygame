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
    speed = config.window_size[1] * 0.004

    def __init__(self, pos, sprite_files):
        self.x, self.y = pos
        self.instancelist.append(self)
        self.sprites = self.load_sprites(sprite_files)
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.direction = choice([True, False])
        self.y_direction = False
        self.explosion = Explosion()
        
        self.last_time = time()
        self.last_damage = self.last_time
        
        self.life = 3

    def load_sprites(self, sprite_files):
        sprites = []
        for file in sprite_files:
            sprite = pygame.image.load(file).convert()
            sprite = pygame.transform.flip(sprite, False, True)
            sprite = pygame.transform.scale(sprite, (SCALED_SPRITE_SIZE, SCALED_SPRITE_SIZE))
            sprite.set_colorkey((0, 0, 0))
            sprites.append(sprite)
        return sprites

    def animate(self):
        self.current_sprite += 0.07
        if self.current_sprite >= len(self.sprites): self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def kill(self):
        self.instancelist.remove(self)
        
    def damage(self):
        if self.life <= 1: self.kill()
        else: self.life -= 1

    def death(self):
        for bloc in Bullet.locs:
            if self.x - self.rect.width/2 < bloc[0] < self.x+10 + self.rect.height and self.y - self.rect.height < bloc[1] < self.y + self.rect.height:
                self.explosion.create(self.x, self.y)
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/hit.mp3'))
                self.damage()
                Bullet.locs.remove(bloc)
                
    def damage_player(self):
        for e in self.instancelist:
            if Player.getX() - self.rect.width/2 < e.rect.x < Player.getX() + self.rect.width/2 and Player.getY() - self.rect.height/2 < e.rect.y < Player.getY() + self.rect.height/2:
                Player.setLife(Player.getLife() - 1)
                
    def shoot(self):
        if randint(0, 1000) < 2:
            Bullet(self.rect.center[0] - SPRITE_SIZE / 2, self.rect.center[1] - SPRITE_SIZE, 3, False)
              
    def move(self, dt):
        pass  # This method should be implemented in subclasses

    def update(self, dt, last_time, surf):
        self.last_time = last_time
        self.death()
        self.move(dt)
        self.shoot()
        self.explosion.update(dt)
        self.explosion.draw(surf)

        self.rect[0] = self.x
        self.rect[1] = self.y
        
        if (self.x > config.window_size[0]+100 or self.x < -100 or self.y > config.window_size[1] or self.y < -100) and ((self.last_time - self.last_damage) > 1): 
            self.last_damage = self.last_time
            self.damage()

        self.animate()
        self.draw(surf)

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    @staticmethod
    def spawn_enemy(n, enemy_class):
        for _ in range(n):
            x = randint(0, config.window_size[0])
            y = config.window_size[1] / 2 - 320
            enemy_class((x, y))


class Enemy1(EnemyBase):
    def __init__(self, pos):
        sprite_files = ['assets/enemy_idle1.png', 'assets/enemy_idle2.png']
        super().__init__(pos, sprite_files)
        self.life = 1

    def move(self, dt):
        if randint(0, 500) < 1:
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
                if self.x > config.window_size[0] - 100:
                    self.direction = False
            else:
                self.x -= self.speed * dt
                if self.x < 5:
                    self.direction = True

    def damage_player(self):
        return super().damage_player()
        