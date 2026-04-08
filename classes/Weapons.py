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
        self.cooldown = 0.8
        self.is_auto = False 

    def fire(self, player_rect, power_level, bullet_system):
        import pygame
        current_time = pygame.time.get_ticks() / 1000.0
        
        if current_time - self.last_fire_time < self.cooldown:
            return False
            
        self.last_fire_time = current_time
        lvl = _lvl(power_level)
        
        burst_count = 1 + (lvl + 1)

        for i in range(burst_count):
            offset_y = i * 15 
            spread_angle = 90 + random.uniform(-18, 18) 
            _single(bullet_system, (player_rect.centerx, player_rect.centery + offset_y), angle=spread_angle, speed_scale=1.1, damage_scale=1.2)

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