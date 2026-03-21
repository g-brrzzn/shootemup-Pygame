import pygame
import numpy as np

class ExplosionSystem:
    def __init__(self, max_particles=10000):
        self.max_particles = max_particles
        self.active_count = 0
        
        self.pos = np.zeros((max_particles, 2), dtype=np.float32)
        self.origin = np.zeros((max_particles, 2), dtype=np.float32)
        self.vel = np.zeros((max_particles, 2), dtype=np.float32)
        self.color = np.zeros((max_particles, 3), dtype=np.uint8)
        self.max_range_sq = np.zeros(max_particles, dtype=np.float32)

    def create(self, x, y, color=(221, 245, 154), count=80, e_range=50.0, speed=10.0, range_variation=0.4):
        if self.active_count >= self.max_particles:
            return
            
        available = self.max_particles - self.active_count
        spawn_count = min(count, available)
        
        start_idx = self.active_count
        end_idx = start_idx + spawn_count

        angles = np.random.uniform(0, 2 * np.pi, spawn_count)
        magnitudes = np.random.uniform(0.2, 1.0, spawn_count) * speed
        
        self.vel[start_idx:end_idx, 0] = np.cos(angles) * magnitudes
        self.vel[start_idx:end_idx, 1] = np.sin(angles) * magnitudes
        
        random_factors = 1.0 + np.random.uniform(-range_variation, range_variation, spawn_count)
        self.max_range_sq[start_idx:end_idx] = (e_range * random_factors) ** 2
        
        self.pos[start_idx:end_idx, 0] = x
        self.pos[start_idx:end_idx, 1] = y
        self.origin[start_idx:end_idx, 0] = x
        self.origin[start_idx:end_idx, 1] = y
        self.color[start_idx:end_idx] = color
        
        self.active_count += spawn_count

    def update(self, dt):
        if self.active_count == 0:
            return
            
        n = self.active_count
        self.pos[:n] += self.vel[:n] * dt
        
        dist_x = self.pos[:n, 0] - self.origin[:n, 0]
        dist_y = self.pos[:n, 1] - self.origin[:n, 1]
        dist_sq = dist_x * dist_x + dist_y * dist_y
        
        dead_indices = np.nonzero(dist_sq > self.max_range_sq[:n])[0]
        
        for i in reversed(dead_indices):
            self.active_count -= 1
            last_idx = self.active_count
            
            if i != last_idx:
                self.pos[i] = self.pos[last_idx]
                self.origin[i] = self.origin[last_idx]
                self.vel[i] = self.vel[last_idx]
                self.color[i] = self.color[last_idx]
                self.max_range_sq[i] = self.max_range_sq[last_idx]

    def draw(self, surf):
        if self.active_count == 0:
            return
            
        n = self.active_count
        pos_list = self.pos[:n].astype(int).tolist()
        color_list = self.color[:n].tolist()
        
        for i in range(n):
            pygame.draw.circle(surf, color_list[i], pos_list[i], 3)