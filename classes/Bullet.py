import pygame
import numpy as np
import math
from constants.global_var import config, GAME_COLOR

class BulletSystem:
    player_images = {1: [], 2: [], 3: []}
    enemy_images = []
    
    glow_player = None
    glow_player_l2 = None
    glow_player_l3 = None
    glow_enemy = None

    def __init__(self, max_particles, is_player):
        self.max_particles = max_particles
        self.is_player = is_player
        self.active_count = 0

        self.pos = np.zeros((max_particles, 2), dtype=np.float32)
        self.vel = np.zeros((max_particles, 2), dtype=np.float32)
        self.angle = np.zeros(max_particles, dtype=np.int32)
        self.grazed = np.zeros(max_particles, dtype=bool)
        self.life = np.zeros(max_particles, dtype=np.float32)

        self.meta = [{} for _ in range(max_particles)]
        self.target_provider = None
        self.orbit_anchor_provider = None
        self.base_speed = config.INTERNAL_RESOLUTION[1]

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


        p_img_l2 = pygame.transform.scale(p_img, (int(p_img.get_width() * 1.3), int(p_img.get_height() * 1.3)))
        pygame.draw.circle(p_img_l2, (255, 255, 255), (p_img_l2.get_width() // 2, p_img_l2.get_height() // 2), 3)

        p_img_l3 = pygame.transform.scale(p_img, (int(p_img.get_width() * 1.5), int(p_img.get_height() * 2.5)))
        pygame.draw.circle(p_img_l3, (255, 255, 255), (p_img_l3.get_width() // 2, p_img_l3.get_height() // 2), 5)

        cls.player_images = {1: [], 2: [], 3: []}
        for a in range(360):
            rot1 = pygame.transform.rotate(p_img, a - 90)
            rot1.set_colorkey((0, 0, 0))
            cls.player_images[1].append(rot1)
            
            rot2 = pygame.transform.rotate(p_img_l2, a - 90)
            rot2.set_colorkey((0, 0, 0))
            cls.player_images[2].append(rot2)
            
            rot3 = pygame.transform.rotate(p_img_l3, a - 90)
            rot3.set_colorkey((0, 0, 0))
            cls.player_images[3].append(rot3)

        cls.enemy_images = []
        for a in range(360):
            rotated = pygame.transform.rotate(e_img, a - 90)
            rotated.set_colorkey((0, 0, 0))
            cls.enemy_images.append(rotated)

        cls.glow_player = assets_manager.get_image("glow_bullet_player")
        cls.glow_enemy = assets_manager.get_image("glow_bullet_enemy")
        cls.glow_enemy_pink = assets_manager.get_image("glow_bullet_pink")
        
        cls.glow_player_l2 = pygame.transform.scale(cls.glow_player, (int(cls.glow_player.get_width() * 1.3), int(cls.glow_player.get_height() * 1.3)))
        cls.glow_player_l3 = pygame.transform.scale(cls.glow_player, (int(cls.glow_player.get_width() * 1.8), int(cls.glow_player.get_height() * 1.8)))

    def set_target_provider(self, provider):
        self.target_provider = provider

    def set_orbit_anchor_provider(self, provider):
        self.orbit_anchor_provider = provider

    def emit_pattern(self, pattern, pos, options=None):
        options = dict(options or {})
        angle = options.get("angle", 90 if self.is_player else 270)
        speed_scale = options.get("speed_scale", 0.9 if self.is_player else 0.3)

        pattern_kwargs = {
            k: v for k, v in options.items()
            if k not in {"angle", "speed_scale", "count", "spread_arc"}
        }

        if pattern == "single":
            self.emit(pos, angle, speed_scale, **pattern_kwargs)
            return

        if pattern == "spread":
            count = options.get("count", 3)
            spread_arc = options.get("spread_arc", 30)

            if count <= 1:
                self.emit(pos, angle, speed_scale, **pattern_kwargs)
                return

            angle_step = spread_arc / (count - 1)
            start_angle = angle - spread_arc / 2

            for i in range(count):
                self.emit(pos, start_angle + i * angle_step, speed_scale, **pattern_kwargs)
            return

        if pattern == "ring":
            count = options.get("count", 8)
            if count <= 0:
                return

            angle_step = 360 / count
            for i in range(count):
                self.emit(pos, angle + (i * angle_step), speed_scale, **pattern_kwargs)
            return

        raise ValueError(f"Unknown bullet pattern: {pattern}")

    def emit(self, pos, angle, speed_scale, **props):
        if self.active_count >= self.max_particles:
            return

        idx = self.active_count
        self.pos[idx, 0] = pos[0]
        self.pos[idx, 1] = pos[1]

        angle_deg = int(angle) % 360
        self.angle[idx] = angle_deg

        angle_rad = math.radians(angle)
        speed = self.base_speed * speed_scale
        if props.get("is_pink"):
            speed *= 0.65
        self.vel[idx, 0] = math.cos(angle_rad) * speed
        self.vel[idx, 1] = -math.sin(angle_rad) * speed

        self.grazed[idx] = False

        meta = dict(props)
        meta.setdefault("speed_scale", speed_scale)
        meta.setdefault("damage_scale", 1.0)
        meta.setdefault("kind", "normal")
        
        self.life[idx] = 2.5 if meta.get("homing") else 5.0

        if meta.get("homing"):
            meta.setdefault("tracking_strength", 1.0)

        if meta.get("orbit"):
            meta.setdefault("orbit_radius", 24.0)
            meta.setdefault("orbit_speed", 5.0)
            meta.setdefault("orbit_angle", math.radians(angle))
            meta.setdefault("orbit_center", (float(pos[0]), float(pos[1])))

        self.meta[idx] = meta
        self.active_count += 1

    def _apply_homing(self, idx, dt):
        if self.target_provider is None:
            return

        meta = self.meta[idx]
        if not meta.get("homing"):
            return

        targets = self.target_provider()
        if not targets:
            return

        px, py = self.pos[idx]
        best_target = None
        best_dist_sq = None

        for target in targets:
            rect = getattr(target, "rect", None)
            if rect is None:
                center = getattr(target, "center", None)
                if center is None:
                    continue
                tx, ty = center
            else:
                tx, ty = rect.center

            dx = tx - px
            dy = ty - py
            dist_sq = dx * dx + dy * dy

            if best_dist_sq is None or dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best_target = (dx, dy)

        if best_target is None:
            return

        dx, dy = best_target
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= 0.001:
            return

        desired_vx = dx / dist
        desired_vy = dy / dist

        tracking_strength = float(meta.get("tracking_strength", 1.0))
        turn_rate = 5.0 * tracking_strength * dt

        self.vel[idx, 0] = (self.vel[idx, 0] * (1.0 - turn_rate)) + (desired_vx * np.linalg.norm(self.vel[idx]) * turn_rate)
        self.vel[idx, 1] = (self.vel[idx, 1] * (1.0 - turn_rate)) + (desired_vy * np.linalg.norm(self.vel[idx]) * turn_rate)

        vel_norm = np.linalg.norm(self.vel[idx])
        if vel_norm > 0.001:
            self.angle[idx] = int((math.degrees(math.atan2(-self.vel[idx, 1], self.vel[idx, 0])) % 360))

    def _apply_orbit(self, idx, dt):
        meta = self.meta[idx]
        if not meta.get("orbit"):
            return

        center = None
        if self.orbit_anchor_provider is not None:
            center = self.orbit_anchor_provider()
        if center is None:
            center = meta.get("orbit_center", (float(self.pos[idx, 0]), float(self.pos[idx, 1])))

        cx, cy = center
        radius = float(meta.get("orbit_radius", 24.0))
        orbit_speed = float(meta.get("orbit_speed", 5.0))

        orbit_angle = float(meta.get("orbit_angle", 0.0))
        orbit_angle += orbit_speed * dt
        meta["orbit_angle"] = orbit_angle

        self.pos[idx, 0] = cx + math.cos(orbit_angle) * radius
        self.pos[idx, 1] = cy + math.sin(orbit_angle) * radius

        self.vel[idx, 0] = 0.0
        self.vel[idx, 1] = 0.0

        self.angle[idx] = int((math.degrees(orbit_angle) + 90) % 360)

    def update(self, dt):
        if self.active_count == 0:
            return

        n = self.active_count

        for i in range(n):
            if self.meta[i].get("orbit"):
                self._apply_orbit(i, dt)
            elif self.meta[i].get("homing"):
                self._apply_homing(i, dt)

        self.pos[:n] += self.vel[:n] * dt
        self.life[:n] -= dt

        world_w, world_h = config.INTERNAL_RESOLUTION
        timeout = self.life[:n] <= 0
        
        from game_engine import g_engine
        
        if self.is_player and getattr(g_engine.player, "ricochet_timer", 0) > 0:
            out_l = self.pos[:n, 0] <= 0
            out_r = self.pos[:n, 0] >= world_w
            out_t = self.pos[:n, 1] <= 0
            out_b = self.pos[:n, 1] >= world_h

            self.vel[:n, 0][out_l | out_r] *= -1
            self.vel[:n, 1][out_t | out_b] *= -1

            self.pos[:n, 0] = np.clip(self.pos[:n, 0], 1, world_w - 1)
            self.pos[:n, 1] = np.clip(self.pos[:n, 1], 1, world_h - 1)

            bounces = np.nonzero(out_l | out_r | out_t | out_b)[0]
            for i in bounces:
                self.angle[i] = int((math.degrees(math.atan2(-self.vel[i, 1], self.vel[i, 0])) % 360))

            out_mask = timeout
        else:
            out_x = (self.pos[:n, 0] < -50) | (self.pos[:n, 0] > world_w + 100)
            out_y = (self.pos[:n, 1] < -50) | (self.pos[:n, 1] > world_h + 100)
            out_mask = out_x | out_y | timeout

        dead_indices = np.nonzero(out_mask)[0]
        for i in reversed(dead_indices):
            if timeout[i] and not self.meta[i].get("orbit"):
                g_engine.spark_system.emit(
                    pos=(self.pos[i, 0], self.pos[i, 1]),
                    angle=0, speed=0, color=(100, 100, 100), scale=0.5, fixed_decay=20
                )
            self.kill_bullet(i)


    def kill_bullet(self, idx):
        meta = self.meta[idx]
        if meta.get("explosive"):
            px, py = self.pos[idx]
            blast_radius = meta.get("blast_radius", 60) 
            
            from game_engine import g_engine
            g_engine.explosion_system.create(
                px, py, color=GAME_COLOR, count=60, e_range=blast_radius, speed=600
            )
            
            for enemy in list(g_engine.all_enemies):
                dist = math.hypot(enemy.rect.centerx - px, enemy.rect.centery - py)
                if dist <= blast_radius:
                    enemy.damage()

        self.active_count -= 1
        last_idx = self.active_count

        if idx != last_idx:
            self.pos[idx] = self.pos[last_idx]
            self.vel[idx] = self.vel[last_idx]
            self.angle[idx] = self.angle[last_idx]
            self.grazed[idx] = self.grazed[last_idx]
            self.life[idx] = self.life[last_idx] 
            self.meta[idx] = self.meta[last_idx]

        self.meta[last_idx] = {}

    def get_bullet_meta(self, idx):
        if 0 <= idx < self.active_count:
            return self.meta[idx]
        return {}

    def draw(self, surf):
        if self.active_count == 0:
            return

        n = self.active_count
        pos_list = self.pos[:n].astype(int).tolist()
        angle_list = self.angle[:n].tolist()
        life_list = self.life[:n].tolist()

        for i in range(n):
            px, py = pos_list[i]
            meta = self.meta[i]

            if meta.get("homing"):
                life_left = life_list[i]
                alpha = 255
                if life_left < 1.5:
                    fade = int((life_left / 1.5) * 255)
                    blink = int((math.sin(life_left * 35) + 1) * 127) 
                    alpha = max(0, min(fade, blink))
                
                if alpha > 0:
                    drone_base = pygame.Surface((14, 14), pygame.SRCALPHA)
                    pygame.draw.circle(drone_base, (*GAME_COLOR[:3], alpha), (6, 6), 6)
                    pygame.draw.circle(drone_base, (255, 255, 255, alpha), (6, 6), 2)
                    surf.blit(drone_base, (px - 6, py - 6))
            
            elif meta.get("explosive"):
                bomb_base = pygame.Surface((20, 20), pygame.SRCALPHA)
                
                pygame.draw.circle(bomb_base, (*GAME_COLOR[:3], 255), (10, 10), 8)
                pygame.draw.circle(bomb_base, (250, 160, 210, 255), (10, 10), 4)
                
                pulse = abs(math.sin(life_list[i] * 20)) * 3
                pygame.draw.circle(bomb_base, (*GAME_COLOR[:3], 150), (10, 10), 6 + pulse, 2)

                surf.blit(bomb_base, (px - 10, py - 10))
            
            else:
                if self.is_player:
                    lvl = max(1, min(3, meta.get("power_level", 1)))
                    
                    img = self.player_images[lvl][angle_list[i]]
                    
                    if lvl == 1:
                        glow = self.glow_player
                    elif lvl == 2:
                        glow = self.glow_player_l2
                    else:
                        glow = self.glow_player_l3
                        
                    glow_w = glow.get_width() // 2
                    glow_h = glow.get_height() // 2
                    
                    surf.blit(img, (px - img.get_width() // 2, py - img.get_height() // 2))
                    surf.blit(glow, (px - glow_w, py - glow_h), special_flags=pygame.BLEND_ADD)
                    
                else:
                    if meta.get("is_pink"):
                        pygame.draw.circle(surf, (250, 160, 210), (px, py), 10) 
                        
                        glow = self.glow_enemy_pink
                        glow_w = glow.get_width() // 2
                        glow_h = glow.get_height() // 2
                        surf.blit(glow, (px - glow_w, py - glow_h), special_flags=pygame.BLEND_ADD)
                    else:
                        img = self.enemy_images[angle_list[i]]
                        glow = self.glow_enemy
                        
                        glow_w = glow.get_width() // 2
                        glow_h = glow.get_height() // 2
                        
                        surf.blit(img, (px - img.get_width() // 2, py - img.get_height() // 2))
                        surf.blit(glow, (px - glow_w, py - glow_h), special_flags=pygame.BLEND_ADD)