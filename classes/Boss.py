import pygame
import math
from random import randint
from game_engine import g_engine
from classes.Enemy import EnemyBase
from classes.Bullet import Bullet
from classes.particles.Explosion import Explosion
from constants.global_var import config, GAME_COLOR

class Boss(EnemyBase):
    def __init__(self, pos, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.instancelist.append(self)
        self.sprites = self.load_sprites(['boss_1_1', 'boss_1_2']) 
        self.white_sprites = [self.create_white_surface(s) for s in self.sprites]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect(center=pos)
        self.width = self.rect.width
        self.height = self.rect.height
        self.x, self.y = float(self.rect.x), float(self.rect.y)
        self.max_life = 65 + (g_engine.level * 5)
        self.life = self.max_life
        self.score_value = 5000
        self.weight = 5
        
        self.target_y = 45
        self.speed = config.INTERNAL_RESOLUTION[0] * 0.002
        
        self.last_hit = 0
        self.hit_flash_duration = 50
        
        self.explosion = Explosion()

    def update(self, dt):
        if self.y < self.target_y:
            self.y += self.speed * dt
        else:
            time_now = pygame.time.get_ticks()
            self.x = (config.INTERNAL_RESOLUTION[0] / 2 - self.width / 2) + \
                     (math.sin(time_now * 0.002) * (config.INTERNAL_RESOLUTION[0] * 0.3))

        self.rect.topleft = (self.x, self.y)
        self.shoot()
        
        self.explosion.update(dt)
        self.current_sprite += 0.07
        if self.current_sprite >= len(self.sprites): self.current_sprite = 0
        if pygame.time.get_ticks() - self.last_hit < self.hit_flash_duration:
            self.image = self.white_sprites[int(self.current_sprite)]
        else:
            self.image = self.sprites[int(self.current_sprite)]

    def shoot(self):
        if randint(0, 100) < 2:
             Bullet.create_bullets('single', self.rect.center, False, 
                                 (g_engine.enemy_bullets, g_engine.all_sprites), 
                                 {'angle': -90, 'speed_scale': 0.008})
        
        if randint(0, 200) < 2:
            Bullet.create_bullets('spread', (self.rect.centerx, self.rect.bottom), False,
                                (g_engine.enemy_bullets, g_engine.all_sprites),
                                {'count': 5, 'spread_arc': 60, 'angle': -90})

    def damage(self):
        self.last_hit = pygame.time.get_ticks()
        if self.life <= 1:
            g_engine.score += self.score_value
            g_engine.screen_shake = 30
            self.explosion.create(self.rect.centerx, self.rect.centery, count=150, speed=15)
            self.kill()
        else:
            self.life -= 1

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        bar_width = self.width
        bar_height = 8
        fill = (self.life / self.max_life) * bar_width
        border_rect = pygame.Rect(self.x, self.y - 15, bar_width, bar_height)
        fill_rect = pygame.Rect(self.x, self.y - 15, fill, bar_height)
        
        pygame.draw.rect(surf, (50, 0, 0), border_rect) 
        pygame.draw.rect(surf, (255, 0, 0), fill_rect)  
        pygame.draw.rect(surf, (255, 255, 255), border_rect, 1)