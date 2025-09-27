import math
from dataclasses import dataclass
from typing import Tuple, List
from random import uniform
import pygame
from pygame.math import Vector2

@dataclass
class Particle:
    pos: Vector2
    origin: Vector2
    vel: Vector2
    color: Tuple[int, int, int]
    max_range: float

class Explosion:
    def __init__(self):
        self.particles: List[Particle] = []

    def create(self, x: float, y: float,
               color: Tuple[int, int, int] = (221, 245, 154),
               count: int = 50,
               e_range: float = 50,
               speed: float = 12.0,
               range_variation: float = 0.4) -> None:
        origin = Vector2(x, y)
        for _ in range(count):
            angle = uniform(0, 2 * math.pi)
            magnitude = uniform(0.2, 1.0) * speed
            vel = Vector2(math.cos(angle), math.sin(angle)) * magnitude
            random_factor = 1.0 + uniform(-range_variation, range_variation)
            particle_range = e_range * random_factor
            
            p = Particle(pos=origin.copy(),
                         origin=origin.copy(),
                         vel=vel,
                         color=color,
                         max_range=particle_range)
            self.particles.append(p)

    def update(self, dt: float) -> None:
        alive: List[Particle] = []
        for p in self.particles:
            p.pos += p.vel * dt
            if (p.pos - p.origin).length_squared() <= (p.max_range * p.max_range):
                alive.append(p)
        self.particles = alive

    def draw(self, surf: pygame.Surface) -> None:
        for p in self.particles:
            pygame.draw.circle(surf, p.color, (int(p.pos.x), int(p.pos.y)), 3)
