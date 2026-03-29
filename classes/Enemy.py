import pygame
import math
from random import randint, uniform

from game_engine import g_engine
from classes.PowerUp import PowerUp
from constants.global_var import config, SCALED_SPRITE_SIZE


class EnemyBase(pygame.sprite.Sprite):
    instancelist = []

    def __init__(self, pos, sprite_files_keys, *groups):
        super().__init__(*groups)
        self.x, self.y = float(pos[0]), float(pos[1])
        self.instancelist.append(self)

        self.sprites = self.load_sprites(sprite_files_keys)
        self.white_sprites = [self.create_white_surface(s) for s in self.sprites]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

        self.life = 1
        self.base_speed = config.INTERNAL_RESOLUTION[1] * 0.225
        self.weight = 1
        self.score_value = 100

        self.last_hit = 0
        self.hit_flash_duration = 100

        self.spawn_time = pygame.time.get_ticks()
        self.random_offset = uniform(0, 100)

    @classmethod
    def load_assets(cls, assets_manager):
        cls.hit_sound = assets_manager.get_sound("hit")

    def create_white_surface(self, surface):
        mask = pygame.mask.from_surface(surface)
        white_surface = mask.to_surface(
            setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)
        )
        white_surface.set_colorkey((0, 0, 0))
        return white_surface

    def load_sprites(self, sprite_keys):
        sprites = []
        for key in sprite_keys:
            sprite = g_engine.assets.get_image(key)
            sprites.append(sprite)
        return sprites

    def kill(self):
        super().kill()
        try:
            EnemyBase.instancelist.remove(self)
        except ValueError:
            pass

    def damage(self):
        self.last_hit = pygame.time.get_ticks()

        if self.life <= 1:
            g_engine.score += self.score_value
            roll = randint(0, 100)
            if roll < 10:
                PowerUp(
                    self.rect.center, "life", g_engine.powerups, g_engine.all_sprites
                )
            elif roll < 15 and g_engine.player.getPowerLevel() < 3:
                PowerUp(
                    self.rect.center, "weapon", g_engine.powerups, g_engine.all_sprites
                )

            self.kill()
        else:
            self.life -= 1

    def shoot(self):
        pass

    def move(self, dt):
        self.y += self.base_speed * dt

    def check_bounds(self):
        if self.y > config.INTERNAL_RESOLUTION[1] + 100:
            self.kill()

    def update(self, dt):
        self.move(dt)
        self.shoot()
        self.check_bounds()

        self.rect.topleft = (self.x, self.y)

        self.current_sprite += 7.5 * dt
        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        if pygame.time.get_ticks() - self.last_hit < self.hit_flash_duration:
            self.image = self.white_sprites[int(self.current_sprite)]
        else:
            self.image = self.sprites[int(self.current_sprite)]

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    @staticmethod
    def spawn_enemy(n, enemy_class):
        for _ in range(n):
            x = randint(0, config.INTERNAL_RESOLUTION[0])
            y = randint(-200, -50)
            enemy_class((x, y), g_engine.all_enemies, g_engine.all_sprites)


class Enemy1(EnemyBase):
    def __init__(self, pos, *groups):
        super().__init__(pos, ["enemy1_1", "enemy1_2"], *groups)
        self.life = 1
        self.weight = 1
        self.base_speed = config.INTERNAL_RESOLUTION[1] * 0.375
        self.score_value = 100

    def move(self, dt):
        speed = self.base_speed * 3 if self.y < 0 else self.base_speed
        self.y += speed * dt
        self.x += (
            math.sin(pygame.time.get_ticks() * 0.05 + self.random_offset) * 37.5 * dt
        )

    def shoot(self):
        if randint(0, 1000) < 5:
            g_engine.enemy_bullets.emit_pattern(
                "single", self.rect.center, {"angle": -90, "speed_scale": 0.75}
            )


class Enemy2(EnemyBase):
    def __init__(self, pos, *groups):
        super().__init__(pos, ["enemy2_1", "enemy2_2"], *groups)
        self.life = 3
        self.weight = 2
        self.base_speed = config.INTERNAL_RESOLUTION[1] * 0.15
        self.score_value = 300
        self.initial_x = self.x

    def move(self, dt):
        speed = self.base_speed * 3 if self.y < 0 else self.base_speed
        self.y += speed * dt

        t = pygame.time.get_ticks() * 0.003
        self.x = self.initial_x + math.sin(t + self.random_offset) * 150
        self.x = max(0, min(self.x, config.INTERNAL_RESOLUTION[0] - SCALED_SPRITE_SIZE))

    def shoot(self):
        if randint(0, 1000) < 5:
            g_engine.enemy_bullets.emit_pattern(
                "spread",
                self.rect.center,
                {"count": 2, "spread_arc": 20, "angle": -90, "speed_scale": 0.45},
            )


class Enemy3(EnemyBase):
    def __init__(self, pos, *groups):
        super().__init__(pos, ["enemy3_1", "enemy3_2"], *groups)
        self.life = 5
        self.weight = 3
        self.base_speed = config.INTERNAL_RESOLUTION[1] * 0.1125
        self.score_value = 500
        self.horizontal_speed = 150.0

    def move(self, dt):
        speed = self.base_speed * 3 if self.y < 0 else self.base_speed
        self.y += speed * dt

        if self.y > 0:
            target_x = g_engine.player.rect.centerx
            if self.x < target_x:
                self.x += self.horizontal_speed * dt
            elif self.x > target_x:
                self.x -= self.horizontal_speed * dt

    def shoot(self):
        if randint(0, 1000) < 5:
            dx = g_engine.player.rect.centerx - self.rect.centerx
            dy = g_engine.player.rect.centery - self.rect.centery
            angle = math.degrees(math.atan2(-dy, dx))

            g_engine.enemy_bullets.emit_pattern(
                "single", self.rect.center, {"angle": angle, "speed_scale": 0.6}
            )
