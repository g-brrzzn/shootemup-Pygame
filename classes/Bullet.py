import pygame
import numpy as np
import math
from constants.global_var import config


class BulletSystem:
    player_images = []
    enemy_images = []
    glow_player = None
    glow_enemy = None

    @classmethod
    def load_assets(cls, assets_manager):
        p_img = assets_manager.get_image("bullet_player")
        e_img = assets_manager.get_image("bullet_enemy")

        if p_img is None:
            p_img = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(p_img, (255, 200, 0), (2, 2), 2)
        if e_img is None:
            e_img = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(e_img, (200, 50, 50), (2, 2), 2)

        cls.player_images = []
        for a in range(360):
            rotated = pygame.transform.rotate(p_img, a - 90)
            rotated.set_colorkey((0, 0, 0))
            cls.player_images.append(rotated)

        cls.enemy_images = []
        for a in range(360):
            rotated = pygame.transform.rotate(e_img, a - 90)
            rotated.set_colorkey((0, 0, 0))
            cls.enemy_images.append(rotated)

        cls.glow_player = assets_manager.get_image("glow_bullet_player")
        cls.glow_enemy = assets_manager.get_image("glow_bullet_enemy")

    def __init__(self, max_particles, is_player):
        self.max_particles = max_particles
        self.is_player = is_player
        self.active_count = 0

        self.pos = np.zeros((max_particles, 2), dtype=np.float32)
        self.vel = np.zeros((max_particles, 2), dtype=np.float32)
        self.angle = np.zeros(max_particles, dtype=np.int32)
        self.grazed = np.zeros(max_particles, dtype=bool)

        self.base_speed = config.INTERNAL_RESOLUTION[1]

    def emit_pattern(self, pattern, pos, options):
        if pattern == "single":
            angle = options.get("angle", 90 if self.is_player else 270)
            speed_scale = options.get("speed_scale", 0.9 if self.is_player else 0.3)
            self.emit(pos, angle, speed_scale)
        elif pattern == "spread":
            count = options.get("count", 3)
            spread_arc = options.get("spread_arc", 30)
            base_angle = options.get("angle", 90 if self.is_player else 270)
            speed_scale = options.get("speed_scale", 0.9 if self.is_player else 0.3)

            if count <= 1:
                self.emit(pos, base_angle, speed_scale)
                return

            angle_step = spread_arc / (count - 1)
            start_angle = base_angle - spread_arc / 2

            for i in range(count):
                self.emit(pos, start_angle + i * angle_step, speed_scale)

    def emit(self, pos, angle, speed_scale):
        if self.active_count >= self.max_particles:
            return

        idx = self.active_count
        self.pos[idx, 0] = pos[0]
        self.pos[idx, 1] = pos[1]

        angle_deg = int(angle) % 360
        self.angle[idx] = angle_deg

        angle_rad = math.radians(angle)
        speed = self.base_speed * speed_scale
        self.vel[idx, 0] = math.cos(angle_rad) * speed
        self.vel[idx, 1] = -math.sin(angle_rad) * speed

        self.grazed[idx] = False
        self.active_count += 1

    def update(self, dt):
        if self.active_count == 0:
            return

        n = self.active_count
        self.pos[:n] += self.vel[:n] * dt

        world_w, world_h = config.INTERNAL_RESOLUTION
        out_x = (self.pos[:n, 0] < -50) | (self.pos[:n, 0] > world_w + 100)
        out_y = (self.pos[:n, 1] < -50) | (self.pos[:n, 1] > world_h + 100)
        out_mask = out_x | out_y

        dead_indices = np.nonzero(out_mask)[0]
        for i in reversed(dead_indices):
            self.kill_bullet(i)

    def kill_bullet(self, idx):
        self.active_count -= 1
        last_idx = self.active_count
        if idx != last_idx:
            self.pos[idx] = self.pos[last_idx]
            self.vel[idx] = self.vel[last_idx]
            self.angle[idx] = self.angle[last_idx]
            self.grazed[idx] = self.grazed[last_idx]

    def draw(self, surf):
        if self.active_count == 0:
            return

        n = self.active_count
        pos_list = self.pos[:n].astype(int).tolist()
        angle_list = self.angle[:n].tolist()

        glow_img = self.glow_player if self.is_player else self.glow_enemy
        glow_w = glow_img.get_width() // 2
        glow_h = glow_img.get_height() // 2

        images = self.player_images if self.is_player else self.enemy_images

        for i in range(n):
            px, py = pos_list[i]
            img = images[angle_list[i]]

            surf.blit(img, (px - img.get_width() // 2, py - img.get_height() // 2))
            surf.blit(
                glow_img, (px - glow_w, py - glow_h), special_flags=pygame.BLEND_ADD
            )
