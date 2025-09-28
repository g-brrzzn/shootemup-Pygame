import pygame
from dataclasses import dataclass
from typing import Tuple, List
from random import randint, uniform
from pygame.math import Vector2
from constants.global_var import config

@dataclass
class Drop:
    pos: Vector2
    fall_speed: float
    radius: int = 3
    color: Tuple[int, int, int] = (70, 70, 70)

class Fall:
    def __init__(self, amount: int):
        self.drops: List[Drop] = []
        width, height = config.INTERNAL_RESOLUTION
        for _ in range(amount):
            x = randint(1, width - 1)
            y = randint(1, height - 1)
            fall_speed = uniform(0.1, 0.9)
            self.drops.append(Drop(pos=Vector2(x, y), fall_speed=fall_speed))

    def update(self, gravity: float = 0.3, wind: float = 0.3, dt: float = 1.0) -> None:
        width, height = config.INTERNAL_RESOLUTION
        for drop in self.drops:
            drop.pos.y += (gravity + drop.fall_speed) * dt

            if wind != 0:
                drop.pos.x += wind * dt
            if drop.pos.y > height:
                drop.pos.y = 0
                drop.pos.x = randint(0, width - 1)
            elif drop.pos.y < 0:
                drop.pos.y = height

            if drop.pos.x > width:
                drop.pos.x = 0
            elif drop.pos.x < 0:
                drop.pos.x = width

    def draw(self, surf: pygame.Surface, color: Tuple[int, int, int] = None) -> None:
        for drop in self.drops:
            c = color if color is not None else drop.color
            pygame.draw.circle(surf, pygame.Color(c), (int(drop.pos.x), int(drop.pos.y)), drop.radius)
