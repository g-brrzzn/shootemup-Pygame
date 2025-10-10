import pygame
from pygame.math import Vector2
from typing import Optional, Iterable, Tuple, List
from constants.global_var import config
import math

class Bullet(pygame.sprite.Sprite):
    player_image: Optional[pygame.Surface] = None
    enemy_image: Optional[pygame.Surface] = None

    @classmethod
    def load_assets(cls, assets_manager) -> None:
        cls.player_image = assets_manager.get_image('bullet_player')
        cls.enemy_image = assets_manager.get_image('bullet_enemy')

    @classmethod
    def create_bullets(cls, pattern: str, pos: tuple, is_from_player: bool, groups: tuple, options: dict = {}) -> List['Bullet']:
        bullets = []
        
        if pattern == 'single':
            angle = options.get('angle', 90 if is_from_player else 270)
            direction = Vector2(math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
            bullets.append(cls(pos, direction, is_from_player, *groups, **options))

        elif pattern == 'spread':
            count = options.get('count', 3)
            spread_arc = options.get('spread_arc', 30)
            base_angle = options.get('angle', 90 if is_from_player else 270)
            
            if count <= 1:
                return cls.create_bullets('single', pos, is_from_player, groups, options)
            
            angle_step = spread_arc / (count - 1)
            start_angle = base_angle - spread_arc / 2
            
            for i in range(count):
                angle = start_angle + i * angle_step
                direction = Vector2(math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
                bullets.append(cls(pos, direction, is_from_player, *groups, **options))
        
        return bullets

    def __init__(
        self,
        pos: Tuple[float, float],
        direction_vector: Vector2,
        is_from_player: bool,
        *groups: Iterable[pygame.sprite.Group],
        **kwargs
    ) -> None:
        super().__init__(*groups)
        
        self.is_from_player = is_from_player
        
        speed_scale = kwargs.get('speed_scale')
        if speed_scale is None:
            speed_scale = 0.012 if is_from_player else 0.004

        base_speed = config.INTERNAL_RESOLUTION[1]
        self.speed = base_speed * speed_scale
        
        self.image = self.player_image if is_from_player else self.enemy_image
        if self.image is None:
            size = (4, 4)
            self.image = pygame.Surface(size, pygame.SRCALPHA)
            color = (255, 200, 0) if is_from_player else (200, 50, 50)
            pygame.draw.circle(self.image, color, (size[0] // 2, size[1] // 2), size[0] // 2)

        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        
        if direction_vector.length() > 0:
            self.vel = direction_vector.normalize() * self.speed
        else:
            default_vel_y = -self.speed if is_from_player else self.speed
            self.vel = Vector2(0, default_vel_y)

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        world_w, world_h = config.INTERNAL_RESOLUTION
        game_world_rect = pygame.Rect(0, 0, world_w, world_h)
        if not game_world_rect.colliderect(self.rect):
            self.kill()