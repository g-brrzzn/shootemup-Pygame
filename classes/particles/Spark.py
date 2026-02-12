import pygame
import math
from random import uniform, randint
from pygame.math import Vector2

class Spark:
    def __init__(self, pos, angle, speed, color, scale=1):
        self.pos = Vector2(pos)
        angle_rad = math.radians(angle + uniform(-15, 15))
        self.vel = Vector2(math.cos(angle_rad), -math.sin(angle_rad)) * speed
        
        
        self.color = (221, 245, 154)
        self.scale = scale
        self.gravity = 0.15
        self.friction = 0.92
        self.life = 200 
        
        self.decay = randint(3, 6) 

    def update(self, dt):
        self.vel.y += self.gravity * dt      
        self.vel *= self.friction            
        self.pos += self.vel * dt
        self.life -= self.decay * dt

    def draw(self, surf):
        if self.life > 0:
            end_pos = self.pos - (self.vel * 2.5) 
            
            if self.vel.length() < 1:
                end_pos = self.pos + Vector2(1, 1)

            color_with_alpha = (*self.color, int(max(0, self.life)))
            
            pygame.draw.line(surf, color_with_alpha, self.pos, end_pos, max(1, int(2 * self.scale)))