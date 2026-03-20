import pygame
import numpy as np
from constants.global_var import config

class Fall:
    def __init__(self, amount: int, min_s: float = 0.1, max_s: float = 0.9, color: tuple = (70, 70, 70), size: int = 3, alpha: int = 255):
        self.amount = amount
        self.pos = np.zeros((amount, 2), dtype=np.float32)
        self.fall_speed = np.zeros(amount, dtype=np.float32)
        
        width, height = config.INTERNAL_RESOLUTION
        
        self.pos[:, 0] = np.random.randint(1, width, size=amount)
        self.pos[:, 1] = np.random.randint(1, height, size=amount)
        self.fall_speed[:] = np.random.uniform(min_s, max_s, size=amount)
        
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*color, alpha), (size, size), size)

    def update(self, gravity: float = 0.3, wind: float = 0.3, dt: float = 1.0) -> None:
        width, height = config.INTERNAL_RESOLUTION
        
        self.pos[:, 1] += (gravity + self.fall_speed) * dt
        
        if wind != 0:
            self.pos[:, 0] += wind * dt

        out_y = self.pos[:, 1] > height
        num_out_y = np.count_nonzero(out_y)
        if num_out_y > 0:
            self.pos[out_y, 1] = -10
            self.pos[out_y, 0] = np.random.randint(0, width, size=num_out_y)

        out_y_top = self.pos[:, 1] < -20
        if np.any(out_y_top):
            self.pos[out_y_top, 1] = height

        out_x_right = self.pos[:, 0] > width
        if np.any(out_x_right):
            self.pos[out_x_right, 0] = 0

        out_x_left = self.pos[:, 0] < 0
        if np.any(out_x_left):
            self.pos[out_x_left, 0] = width

    def draw(self, surf: pygame.Surface) -> None:
        pos_list = self.pos.astype(int).tolist()
        for p in pos_list:
            surf.blit(self.image, p)