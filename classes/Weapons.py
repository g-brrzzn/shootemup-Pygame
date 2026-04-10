import random
from game_engine import g_engine


class Weapon:
    def fire(self, player_rect, power_level, bullet_system):
        raise NotImplementedError


def _lvl(power_level: int) -> int:
    return max(1, int(power_level or 1))


def _apply_stats(kwargs):
    if g_engine.player:
        kwargs["speed_scale"] = kwargs.get("speed_scale", 1.0) * getattr(g_engine.player, "bullet_speed_mult", 1.0)
        kwargs["damage_scale"] = kwargs.get("damage_scale", 1.0) * getattr(g_engine.player, "bullet_damage_mult", 1.0)
        
        kwargs["power_level"] = getattr(g_engine.player, "power_level", 1)
        
        if "tracking_strength" in kwargs:
            kwargs["tracking_strength"] *= getattr(g_engine.player, "tracking_strength_mult", 1.0)
    return kwargs

def _single(bullet_system, pos, **kwargs):
    kwargs = _apply_stats(kwargs)
    bullet_system.emit_pattern("single", pos, kwargs)

def _spread(bullet_system, pos, **kwargs):
    if g_engine.player and "spread_arc" in kwargs:
        kwargs["spread_arc"] *= getattr(g_engine.player, "spread_arc_mult", 1.0)
        
    kwargs = _apply_stats(kwargs)
    bullet_system.emit_pattern("spread", pos, kwargs)


class FrontalCannon(Weapon):
    def fire(self, player_rect, power_level, bullet_system):
        lvl = _lvl(power_level)
        if lvl == 1:
            _single(bullet_system, player_rect.center, angle=90, speed_scale=1.0)
        elif lvl == 2:
            _spread(bullet_system, player_rect.center, count=2, spread_arc=14, angle=90, speed_scale=1.0)
        else:
            _spread(bullet_system, player_rect.center, count=3, spread_arc=24, angle=90, speed_scale=1.02)


class RearShot(Weapon):
    def fire(self, player_rect, power_level, bullet_system):
        lvl = _lvl(power_level)
        if lvl == 1:
            _single(bullet_system, player_rect.center, angle=270, speed_scale=0.85)
        elif lvl == 2:
            _spread(bullet_system, player_rect.center, count=2, spread_arc=18, angle=270, speed_scale=0.88)
        else:
            _spread(bullet_system, player_rect.center, count=3, spread_arc=30, angle=270, speed_scale=0.9)


class SideShot(Weapon):
    def __init__(self):
        self.last_fire_time = 0
        self.cooldown = 1.2
        self.is_auto = False

    def fire(self, player_rect, power_level, bullet_system):
        import pygame
        current_time = pygame.time.get_ticks() / 1000.0
        
        if current_time - self.last_fire_time < self.cooldown:
            return False
            
        self.last_fire_time = current_time
        lvl = _lvl(power_level)
        count = min(6, 2 * lvl) 
        _spread(bullet_system, player_rect.center, count=count, spread_arc=180, angle=90, speed_scale=0.95)


class BurstTurret(Weapon):
    def __init__(self):
        self.last_fire_time = 0
        self.cooldown = 0.7

        self.burst_active = False
        self.burst_total = 0
        self.burst_remaining = 0
        self.next_shot_time = 0
        self.burst_delay = 0.08

        self.base_spread = 9        
        self.spread_step = 2.2     
        self._current_lvl = 1 

    @property
    def is_auto(self):
        return self.burst_active

    def fire(self, player_rect, power_level, bullet_system):
        import pygame
        current_time = pygame.time.get_ticks() / 1000.0

        if self.burst_active:
            if current_time >= self.next_shot_time:
                self._shoot_projectile(player_rect, bullet_system)
                self.burst_remaining -= 1
                self.next_shot_time = current_time + self.burst_delay

                if self.burst_remaining <= 0:
                    self.burst_active = False

            return False 

        if current_time - self.last_fire_time < self.cooldown:
            return False

        self.last_fire_time = current_time
        lvl = _lvl(power_level)
        self._current_lvl = lvl

        if lvl == 1:
            self.burst_total = 3
        elif lvl == 2:
            self.burst_total = 4
        else:
            self.burst_total = 5

        self.burst_remaining = self.burst_total
        self.burst_active = True
        
        self._shoot_projectile(player_rect, bullet_system)
        self.burst_remaining -= 1
        self.next_shot_time = current_time + self.burst_delay

        if self.burst_remaining <= 0:
            self.burst_active = False

        return True

    def _shoot_projectile(self, player_rect, bullet_system):
        import random
        i = self.burst_total - self.burst_remaining
        spread = random.uniform(-self.base_spread, self.base_spread) + (i * random.uniform(-self.spread_step, self.spread_step))
        speed = 1.05 + (i * 0.02)

        if self._current_lvl >= 2:
            offset = 14
            _single(bullet_system, (player_rect.centerx - offset, player_rect.centery), angle=90 + spread, speed_scale=speed, damage_scale=0.85)
            _single(bullet_system, (player_rect.centerx + offset, player_rect.centery), angle=90 + spread, speed_scale=speed, damage_scale=0.85)
        else:
            _single(bullet_system, player_rect.center, angle=90 + spread, speed_scale=speed, damage_scale=0.85)
            

    def _shoot_projectile(self, player_rect, bullet_system):
        import random
        i = self.burst_total - self.burst_remaining
        spread = random.uniform(-self.base_spread, self.base_spread) + (i * random.uniform(-self.spread_step, self.spread_step))
        speed = 1.05 + (i * 0.02)

        _single(
            bullet_system,
            player_rect.center,
            angle=90 + spread,
            speed_scale=speed,
            damage_scale=0.85
        )

class TrackingDrones(Weapon):
    def __init__(self):
        self.last_fire_time = 0
        self.cooldown = 3.5 
        self.is_auto = True

    def fire(self, player_rect, power_level, bullet_system):
        import pygame
        current_time = pygame.time.get_ticks() / 1000.0
        
        if current_time - self.last_fire_time < self.cooldown:
            return False

        self.last_fire_time = current_time
        lvl = _lvl(power_level)
        drone_count = min(5, 2 + lvl)

        _spread(
            bullet_system, player_rect.center, count=drone_count,
            spread_arc=220, angle=270, speed_scale=0.85, 
            homing=True, tracking_strength=3.5 + (lvl * 0.5) 
        )


class BombPod(Weapon):
    def fire(self, player_rect, power_level, bullet_system):
        lvl = _lvl(power_level)
        _single(
            bullet_system, player_rect.center, angle=90, speed_scale=1.15,
            explosive=True, blast_radius=70 + (lvl * 20), splash_damage=1.0 + (lvl * 0.2)
        )


class BombardmentFusion(Weapon):
    def __init__(self):
        self.last_fire_time = 0
        self.cooldown = 1.0  
        self.is_auto = False

    def fire(self, player_rect, power_level, bullet_system):
        import pygame
        current_time = pygame.time.get_ticks() / 1000.0
        
        if current_time - self.last_fire_time < self.cooldown:
            return False
            
        self.last_fire_time = current_time
        lvl = _lvl(power_level)
        
        bomb_count = min(5, 2 + lvl)

        _spread(
            bullet_system, player_rect.center, count=bomb_count,
            spread_arc=50 + (lvl * 10), angle=90, speed_scale=1.15 + (lvl * 0.05),
            explosive=True, blast_radius=80 + (lvl * 15), splash_damage=2.0,
        )

class StormWallFusion(Weapon):
    def fire(self, player_rect, power_level, bullet_system):
        lvl = _lvl(power_level)
        wall_count = min(7, 3 + lvl)
        _spread(bullet_system, player_rect.center, count=wall_count, spread_arc=70, angle=180, speed_scale=1.0, damage_scale=0.85)
        _spread(bullet_system, player_rect.center, count=wall_count, spread_arc=70, angle=0, speed_scale=1.0, damage_scale=0.85)
        
class FlakCannonFusion(Weapon):
    def __init__(self):
        self.last_fire_time = 0
        self.cooldown = 1.0
        self.burst_active = False
        self.burst_total = 4
        self.burst_remaining = 0
        self.next_shot_time = 0
        self.burst_delay = 0.1
        self.base_spread = 12
        self._current_lvl = 1

    @property
    def is_auto(self):
        return self.burst_active

    def fire(self, player_rect, power_level, bullet_system):
        import pygame
        current_time = pygame.time.get_ticks() / 1000.0

        if self.burst_active:
            if current_time >= self.next_shot_time:
                self._shoot_projectile(player_rect, bullet_system)
                self.burst_remaining -= 1
                self.next_shot_time = current_time + self.burst_delay
                if self.burst_remaining <= 0:
                    self.burst_active = False
            return False

        if current_time - self.last_fire_time < self.cooldown:
            return False

        self.last_fire_time = current_time
        self._current_lvl = _lvl(power_level)
        self.burst_remaining = self.burst_total
        self.burst_active = True
        
        self._shoot_projectile(player_rect, bullet_system)
        self.burst_remaining -= 1
        self.next_shot_time = current_time + self.burst_delay
        if self.burst_remaining <= 0:
            self.burst_active = False
        return True

    def _shoot_projectile(self, player_rect, bullet_system):
        import random
        spread = random.uniform(-self.base_spread, self.base_spread)
        offset = 18
        blast_rad = 50 + (self._current_lvl * 10)
        
        _single(bullet_system, (player_rect.centerx - offset, player_rect.centery), angle=90 + spread, speed_scale=1.2, damage_scale=0.8, explosive=True, blast_radius=blast_rad, splash_damage=0.8)
        _single(bullet_system, (player_rect.centerx + offset, player_rect.centery), angle=90 + spread, speed_scale=1.2, damage_scale=0.8, explosive=True, blast_radius=blast_rad, splash_damage=0.8)

class AegisSystemFusion(Weapon):
    def __init__(self):
        self.last_fire_time = 0
        self.cooldown = 6.0   
        self.is_auto = True

    def fire(self, player_rect, power_level, bullet_system):
        import pygame
        current_time = pygame.time.get_ticks() / 1000.0
        
        if current_time - self.last_fire_time < self.cooldown:
            return False
            
        self.last_fire_time = current_time
        lvl = _lvl(power_level)
        count = lvl  
        
        blocks_bullets = getattr(g_engine.player, 'orbiters_block_bullets', False)
        
        for i in range(count):
            angle = (360 / count) * i
            _single(
                bullet_system, player_rect.center, angle=angle, speed_scale=0,
                orbit=True, orbit_radius=115.0, orbit_speed=3.5, 
                life=5.5,
                is_shield=blocks_bullets, indestructible=True, is_aegis=True, damage_scale=1.5
            )
        return True