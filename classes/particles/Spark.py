import pygame
import numpy as np
import math
from random import uniform, randint


class SparkSystem:
    def __init__(self, max_particles=20000):
        self.max_particles = max_particles
        self.active_count = 0

        self.pos = np.zeros((max_particles, 2), dtype=np.float32)
        self.vel = np.zeros((max_particles, 2), dtype=np.float32)
        self.color = np.zeros((max_particles, 3), dtype=np.uint8)
        self.scale = np.ones(max_particles, dtype=np.float32)
        self.life = np.zeros(max_particles, dtype=np.float32)
        self.decay = np.zeros(max_particles, dtype=np.float32)

        self.gravity = 11.25
        self.friction = 0.92

    def emit(
        self, pos, angle, speed, color=(221, 245, 154), scale=1.0, fixed_decay=None
    ):
        if self.active_count >= self.max_particles:
            return

        idx = self.active_count

        angle_rad = math.radians(angle + uniform(-15, 15))

        self.pos[idx, 0] = pos[0]
        self.pos[idx, 1] = pos[1]
        self.vel[idx, 0] = math.cos(angle_rad) * speed
        self.vel[idx, 1] = -math.sin(angle_rad) * speed
        self.color[idx] = color
        self.scale[idx] = scale
        self.life[idx] = 200.0
        self.decay[idx] = fixed_decay if fixed_decay else randint(225, 450)

        self.active_count += 1

    def update(self, dt):
        if self.active_count == 0:
            return

        n = self.active_count

        self.vel[:n, 1] += self.gravity * dt
        self.vel[:n] *= self.friction
        self.pos[:n] += self.vel[:n] * dt
        self.life[:n] -= self.decay[:n] * dt

        dead_indices = np.nonzero(self.life[:n] <= 0)[0]

        for i in reversed(dead_indices):
            self.active_count -= 1
            last_idx = self.active_count

            if i != last_idx:
                self.pos[i] = self.pos[last_idx]
                self.vel[i] = self.vel[last_idx]
                self.color[i] = self.color[last_idx]
                self.scale[i] = self.scale[last_idx]
                self.life[i] = self.life[last_idx]
                self.decay[i] = self.decay[last_idx]

    def draw(self, surf):
        if self.active_count == 0:
            return

        n = self.active_count

        end_pos = self.pos[:n] - (self.vel[:n] * 2.5)

        vel_sq = self.vel[:n, 0] ** 2 + self.vel[:n, 1] ** 2
        slow_mask = vel_sq < 1.0
        end_pos[slow_mask] = self.pos[:n][slow_mask] + 1.0

        pos_list = self.pos[:n].tolist()
        end_list = end_pos.tolist()
        color_list = self.color[:n].tolist()
        life_list = self.life[:n].tolist()
        scale_list = self.scale[:n].tolist()

        for i in range(n):
            alpha = int(max(0, min(255, life_list[i])))
            color_with_alpha = (
                color_list[i][0],
                color_list[i][1],
                color_list[i][2],
                alpha,
            )

            pygame.draw.line(
                surf,
                color_with_alpha,
                (pos_list[i][0], pos_list[i][1]),
                (end_list[i][0], end_list[i][1]),
                max(1, int(2 * scale_list[i])),
            )
