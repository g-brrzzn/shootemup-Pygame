import pygame
import numpy as np
from constants.global_var import config

class LightRays:
    def __init__(
        self,
        amount: int,
        min_speed: float = 400.0,
        max_speed: float = 1000.0,
        color: tuple = (255, 255, 255),
        width: int = 2,
        length: int = 80,
        alpha: int = 150,
        direction: int = -1 
    ):
        self.amount = amount
        self.direction = direction
        self.length = length
        self.min_s = min_speed
        self.max_s = max_speed

        self.pos = np.zeros((amount, 2), dtype=np.float32)
        self.speed = np.zeros(amount, dtype=np.float32)

        width_screen, height_screen = config.INTERNAL_RESOLUTION

        self.pos[:, 0] = np.random.uniform(0, width_screen, size=amount)
        self.pos[:, 1] = np.random.uniform(0, height_screen, size=amount)
        self.speed[:] = np.random.uniform(self.min_s, self.max_s, size=amount)

        self.image = pygame.Surface((width, length), pygame.SRCALPHA)
        for y in range(length):
            fade = 1.0 - abs((y / length) * 2 - 1.0)
            current_alpha = int(alpha * fade)
            pygame.draw.line(self.image, (*color[:3], current_alpha), (0, y), (width, y))

    def update(self, dt: float = 1.0) -> None:
        width_screen, height_screen = config.INTERNAL_RESOLUTION

        self.pos[:, 1] += self.speed * self.direction * dt

        if self.direction == -1:  
            out_y = self.pos[:, 1] < -self.length
            num_out = np.count_nonzero(out_y)
            if num_out > 0:
                self.pos[out_y, 1] = height_screen + np.random.uniform(0, 100, size=num_out)
                self.pos[out_y, 0] = np.random.uniform(0, width_screen, size=num_out)
                self.speed[out_y] = np.random.uniform(self.min_s, self.max_s, size=num_out)
        else:  
            out_y = self.pos[:, 1] > height_screen
            num_out = np.count_nonzero(out_y)
            if num_out > 0:
                self.pos[out_y, 1] = -self.length - np.random.uniform(0, 100, size=num_out)
                self.pos[out_y, 0] = np.random.uniform(0, width_screen, size=num_out)
                self.speed[out_y] = np.random.uniform(self.min_s, self.max_s, size=num_out)

    def draw(self, surf: pygame.Surface) -> None:
        pos_list = self.pos.astype(int).tolist()
        for p in pos_list:
            surf.blit(self.image, p, special_flags=pygame.BLEND_ADD)