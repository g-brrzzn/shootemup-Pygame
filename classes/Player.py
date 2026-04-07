import math
import numpy as np 

import pygame
from time import time
from pygame.locals import *
from random import randint, choice

from classes.Weapons import FrontalCannon
from game_engine import g_engine
from constants.global_var import (
    MAX_LIFE,
    CONTROLS,
    config,
    PLAYER_COLOR_GREEN,
    GAME_COLOR,
)

class Player(pygame.sprite.Sprite):
    MAX_POWER_LEVEL = 3

    def __init__(self, pos, *groups):
        super().__init__(*groups)

        self.shot_delay = 0.25
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.firing = False

        self.last_time = time()
        self.last_shot = self.last_time
        self.trail_timer = 0.0
        
        self.speed_mult = 1.0
        self.bullet_damage_mult = 1.0
        self.bullet_speed_mult = 1.0
        self.spread_arc_mult = 1.0
        self.tracking_strength_mult = 1.0
        
        self.parry_active = False
        self.parry_timer = 0.0
        self.parry_duration = 0.25  
        self.parry_cooldown_timer = 0.0
        self.parry_cooldown = 0.5   
        
        self.parry_visual_alpha = 0.0
        
        self.overdrive_timer = 0.0
        self.ricochet_timer = 0.0

        self.parry_texts = []
        try:
            self.parry_font = pygame.font.Font(g_engine.assets.get_font_path("american_captain"), 30)
        except:
            self.parry_font = pygame.font.SysFont("arial", 30, bold=True)

        self.original_sprites = [
            g_engine.assets.get_image("player_idle1"),
            g_engine.assets.get_image("player_idle2"),
        ]

        self.original_white_sprites = [
            self.create_white_surface(s) for s in self.original_sprites
        ]
        
        self.original_pink_sprites = [
            self.create_pink_surface(s) for s in self.original_sprites
        ]

        self.current_sprite_index = 0

        self.image = self.original_sprites[self.current_sprite_index]
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy()

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.movement = pygame.math.Vector2()
        self.speed = config.INTERNAL_RESOLUTION[1] * 0.525

        self.life = MAX_LIFE

        self.last_hit = 0
        self.invincibility_duration = 100
        self.power_level = 1

        self.angle = 0
        self.target_angle = 0
        self.exhaust_particles = []
        self.muzzle_flashes = []
        self.trail = []

        self.level = 1
        self.exp = 0
        self.max_exp = 10
        self.pending_level_up = False

        self.acquired_skills = []
        self.active_weapons = {
            "base": FrontalCannon()
        }
        self.weapon_levels = {
            "base": 1
        }

    def reset_movement(self):
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.firing = False

    def create_white_surface(self, surface):
        mask = pygame.mask.from_surface(surface)
        white_surface = mask.to_surface(
            setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)
        )
        white_surface.set_colorkey((0, 0, 0))
        return white_surface
    
    def create_pink_surface(self, surface):
        tinted = surface.copy()
        arr = pygame.surfarray.pixels3d(tinted)

        gray = np.dot(arr[..., :3], [0.2989, 0.5870, 0.1140])
        
        arr[..., 0] = np.clip(gray * 1.0, 0, 255)         
        arr[..., 1] = np.clip(gray * (105/255.0), 0, 255)  
        arr[..., 2] = np.clip(gray * (180/255.0), 0, 255) 
        
        del arr 
        tinted.set_colorkey((0, 0, 0))
        return tinted

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.max_exp:
            self.exp -= self.max_exp
            self.level += 1
            self.max_exp = int(self.max_exp * 1.5)
            self.pending_level_up = True

    def equip_weapon(self, weapon_id, weapon_instance, level=1):
        self.active_weapons[weapon_id] = weapon_instance
        self.weapon_levels[weapon_id] = max(self.weapon_levels.get(weapon_id, 0), level)

    def unequip_weapon(self, weapon_id):
        if weapon_id == "base":
            return
        self.active_weapons.pop(weapon_id, None)
        self.weapon_levels.pop(weapon_id, None)

    def add_skill(self, skill):
        self.acquired_skills.append(dict(skill))

    def get_input(self, event):
        if event.key in CONTROLS["LEFT"]:
            self.moving_left = True
        if event.key in CONTROLS["RIGHT"]:
            self.moving_right = True
        if event.key in CONTROLS["DOWN"]:
            self.moving_down = True
        if event.key in CONTROLS["UP"]:
            self.moving_up = True
        if event.key in CONTROLS["FIRE"]:
            self.firing = True          
        if event.key in CONTROLS["ABSORB"]: 
            if not self.parry_active and self.parry_cooldown_timer <= 0:
                self.parry_active = True
                self.parry_timer = self.parry_duration
                self.parry_cooldown_timer = self.parry_cooldown
                

        # Debug keys
        if event.key == K_o:
            if self.shot_delay >= 0.1:
                self.shot_delay -= 0.1
        if event.key == K_l:
            if self.shot_delay < 0.25:
                self.shot_delay += 0.1
        if event.key == K_i:
            self.speed += 1
        if event.key == K_k:
            if self.speed >= 7:
                self.speed -= 1

    def get_input_keyup(self, event):
        if event.key in CONTROLS["LEFT"]:
            self.moving_left = False
        if event.key in CONTROLS["RIGHT"]:
            self.moving_right = False
        if event.key in CONTROLS["DOWN"]:
            self.moving_down = False
        if event.key in CONTROLS["UP"]:
            self.moving_up = False
        if event.key in CONTROLS["FIRE"]:
            self.firing = False

    def get_controller_input(self, event):
        if event.button == 0:
            self.firing = True
        if event.button == 1:
            self.firing = True
        if event.button == 5:
            self.firing = True
        if event.button == 4:
            self.firing = True

        if g_engine.platform == "Darwin":
            if event.button == 11:
                self.moving_up = True
            if event.button == 12:
                self.moving_down = True
            if event.button == 13:
                self.moving_left = True
            if event.button == 14:
                self.moving_right = True

    def get_controller_keyup(self, event):
        if event.button == 0:
            self.firing = False
        if event.button == 1:
            self.firing = False
        if event.button == 5:
            self.firing = False
        if event.button == 4:
            self.firing = False

        if g_engine.platform == "Darwin":
            if event.button == 11:
                self.moving_up = False
            if event.button == 12:
                self.moving_down = False
            if event.button == 13:
                self.moving_left = False
            if event.button == 14:
                self.moving_right = False

    def get_joyhat_input(self, event):
        if event.hat != 0:
            return

        x, y = event.value

        if x == -1:
            self.moving_left = True
        elif x == 1:
            self.moving_right = True
        else:
            self.moving_left = False
            self.moving_right = False

        if y == -1:
            self.moving_down = True
        elif y == 1:
            self.moving_up = True
        else:
            self.moving_down = False
            self.moving_up = False

    def get_joyaxismotion_input(self, event):
        if not config.use_analog_stick and event.axis in (0, 1):
            return

        deadzone = 0.3

        if event.axis == 0:
            if event.value < -deadzone:
                self.moving_left = True
                self.moving_right = False
            elif event.value > deadzone:
                self.moving_right = True
                self.moving_left = False
            else:
                self.moving_left = False
                self.moving_right = False

        if event.axis == 1:
            if event.value < -deadzone:
                self.moving_up = True
                self.moving_down = False
            elif event.value > deadzone:
                self.moving_down = True
                self.moving_up = False
            else:
                self.moving_up = False
                self.moving_down = False

        if event.axis == 5 or (event.axis == 4 and g_engine.platform == "Linux"):
            if event.value > 0.5:
                self.firing = True
            else:
                self.firing = False

    def get_firing_weapons(self):
        fusion_weapons = [
            (w_id, w) for w_id, w in self.active_weapons.items()
            if w_id.startswith("fusion_") and not getattr(w, "is_auto", False)
        ]

        if fusion_weapons:
            return fusion_weapons[:1]

        weapons = []
        has_main_weapon = any(w in self.active_weapons for w in ["burst_turret"])

        for w_id, w in self.active_weapons.items():
            if getattr(w, "is_auto", False):
                continue 
                
            if has_main_weapon and w_id == "base":
                continue 
                
            weapons.append((w_id, w))

        return weapons

    def fire(self):
        actually_fired = False
        firing_weapons = self.get_firing_weapons()
        
        for weapon_id, weapon in firing_weapons:
            if weapon.fire(self.rect, self.power_level, g_engine.player_bullets) is not False:
                actually_fired = True

        if actually_fired:
            for _ in range(2):
                self.muzzle_flashes.append([randint(-2, 2), randint(2, 6), randint(3, 5)])

            pygame.mixer.Sound.play(g_engine.assets.get_sound("shoot"))

            if config.apply_controller_vibration and g_engine.joystick:
                g_engine.joystick.rumble(5, 50, 20)

    def upgrade(self):
        self.power_level = min(self.power_level + 1, self.MAX_POWER_LEVEL)

    def update_particles(self, dt):
        self.trail_timer += dt
        offset_x = randint(-12, 12)
        p_x = self.rect.centerx + offset_x
        p_y = self.rect.bottom - 20

        color = choice([(167, 94, 67), (198, 128, 127)])
        radius = randint(6, 10)

        if self.moving_up:
            radius += 4

        self.exhaust_particles.append([p_x, p_y, radius, color, 255])

        for p in self.exhaust_particles[:]:
            p[1] += 300.0 * dt
            p[2] -= 30.0 * dt
            p[4] -= 900.0 * dt

            if p[2] <= 0 or p[4] <= 0:
                try:
                    self.exhaust_particles.remove(p)
                except ValueError:
                    pass

        if self.trail_timer >= 0.015:
            self.trail.append((self.rect.centerx, self.rect.centery))
            if len(self.trail) > 12:
                self.trail.pop(0)
            self.trail_timer = 0.0
            
                

    
    def draw_absorb_effect(self, surf):
        if self.parry_active:
            glow = g_engine.assets.get_image("glow_absorb").copy()
            pulse = int((math.sin(pygame.time.get_ticks() * 0.05) + 1) * 50) + 155 
            glow.set_alpha(pulse)
            surf.blit(glow, glow.get_rect(center=self.rect.center), special_flags=pygame.BLEND_ADD)
            
            
    def on_parry_success(self):
        pygame.mixer.Sound.play(g_engine.assets.get_sound("wah-parry"))

        g_engine.hit_stop_frames = 0.15  
        
        self.parry_active = False
        self.parry_visual_alpha = 0.0
        self.parry_cooldown_timer = 0.0
        
        self.overdrive_timer = 3.0
        
        self.upgrade()  

        self.last_hit = pygame.time.get_ticks() + 3000
    
    def activate_ricochet(self):
        self.ricochet_timer = 6.0        
            
    def update(self, dt):
        self.last_time = time()
        self.update_particles(dt)
        
        if self.overdrive_timer > 0:
            self.overdrive_timer -= dt
        
        if self.parry_cooldown_timer > 0:
            self.parry_cooldown_timer -= dt
            
        if self.ricochet_timer > 0:
            self.ricochet_timer -= dt

        if self.parry_active:
            self.parry_timer -= dt
            self.parry_visual_alpha = min(255.0, self.parry_visual_alpha + 1500.0 * dt) 
            if self.parry_timer <= 0:
                self.parry_active = False
        else:
            self.parry_visual_alpha = max(0.0, self.parry_visual_alpha - 800.0 * dt) 

        max_flash_radius = 25
        for flash in self.muzzle_flashes[:]:
            flash[1] += (flash[2] * 60.0 * dt)
            if flash[1] > max_flash_radius:
                self.muzzle_flashes.remove(flash)

        self.current_sprite_index += 5.25 * dt
        if self.current_sprite_index >= len(self.original_sprites):
            self.current_sprite_index = 0

        current_speed = self.speed * self.speed_mult

        if self.moving_right:
            self.x += current_speed * dt
            self.rect.x = round(self.x)
        if self.moving_left:
            self.x -= current_speed * dt
            self.rect.x = round(self.x)
        if self.moving_up:
            self.y -= current_speed * dt
            self.rect.y = round(self.y)
        if self.moving_down:
            self.y += current_speed * dt
            self.rect.y = round(self.y)

        if self.rect.right > config.INTERNAL_RESOLUTION[0]:
            self.rect.right = config.INTERNAL_RESOLUTION[0]
            self.x = float(self.rect.x)

        if self.rect.left < 0:
            self.rect.left = 0
            self.x = float(self.rect.x)

        if self.rect.bottom > config.INTERNAL_RESOLUTION[1]:
            self.rect.bottom = config.INTERNAL_RESOLUTION[1]
            self.y = float(self.rect.y)

        if self.rect.top < 0:
            self.rect.top = 0
            self.y = float(self.rect.y)

        target_angle = 0
        if self.moving_left and not self.moving_right:
            target_angle = 10
        if self.moving_right and not self.moving_left:
            target_angle = -10

        self.angle += (target_angle - self.angle) * 15.0 * dt

        current_time = pygame.time.get_ticks()
        is_invincible = current_time - self.last_hit < self.invincibility_duration

        current_time = pygame.time.get_ticks()

        is_invincible = (current_time < self.last_hit) or (current_time - self.last_hit < self.invincibility_duration)

        idx = int(self.current_sprite_index)
        
        if self.parry_active:
            base_image = self.original_pink_sprites[idx]
        elif is_invincible and (current_time // 100) % 2 == 1:
            base_image = self.original_white_sprites[idx]
        else:
            base_image = self.original_sprites[idx]

        self.image = pygame.transform.rotate(base_image, self.angle)
        self.image.set_colorkey((0, 0, 0))

        original_center = self.rect.center
        self.rect = self.image.get_rect(center=original_center)

        self.hitbox = self.rect.inflate(-20, -10)
        self.hitbox.y += 15
        
        self.parry_rect = self.rect.inflate(70, 70)

        effective_shot_delay = self.shot_delay / 2.0 if self.overdrive_timer > 0 else self.shot_delay

        if self.firing and self.last_time - self.last_shot > effective_shot_delay:
            self.fire()
            self.last_shot = self.last_time
            
        if self.life > 0:
            for w_id, w in self.active_weapons.items():
                if getattr(w, "is_auto", False):
                    w.fire(self.rect, self.power_level, g_engine.player_bullets)


    def draw_particles(self, surf):
        for i, (tx, ty) in enumerate(self.trail):
            radius = int((i / len(self.trail)) * 9)
            if radius > 0:
                surf_trail = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                alpha = int((i / len(self.trail)) * 120)
                
                trail_color = (255, 105, 180) if self.parry_active else PLAYER_COLOR_GREEN
                
                pygame.draw.circle(
                    surf_trail, (*trail_color, alpha), (radius, radius), radius
                )
                surf.blit(surf_trail, (tx - radius, ty - radius))

        for p in self.exhaust_particles:
            x, y, r, c, a = p
            radius_int = int(r)
            if radius_int <= 0:
                continue

            particle_surf = pygame.Surface(
                (radius_int * 2, radius_int * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                particle_surf, (*c, int(a)), (radius_int, radius_int), radius_int
            )
            surf.blit(particle_surf, (x - radius_int, y - radius_int))

    def draw_muzzle_flash(self, surf):
        max_flash_radius = 25.0
        center_x = self.rect.centerx

        for flash in self.muzzle_flashes:
            offset_y, radius, speed = flash
            center_y = self.rect.top + offset_y

            alpha = int(255 * (1.0 - (radius / max_flash_radius)))
            if alpha <= 0:
                continue

            rad_int = int(radius)
            flash_surf = pygame.Surface((rad_int * 2, rad_int * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                flash_surf, (*GAME_COLOR, alpha), (rad_int, rad_int), rad_int, 3
            )
            surf.blit(flash_surf, (center_x - rad_int, center_y - rad_int))
            

    def take_damage(self):
        current_time = pygame.time.get_ticks()
        is_invincible = (current_time < self.last_hit) or (current_time - self.last_hit < self.invincibility_duration)
        
        if not is_invincible:
            self.life -= 1
            self.power_level = 1
            self.last_hit = current_time 
            g_engine.explosion_system.create(
                self.rect.centerx,
                self.rect.centery,
                PLAYER_COLOR_GREEN,
                speed=-375,
            )
            pygame.mixer.Sound.play(g_engine.assets.get_sound("hit"))
            g_engine.screen_shake = 0.5
            
            return True 
            
        return False 

    def getLife(self):
        return self.life

    def setLife(self, life):
        self.life = life

    def gain_life(self):
        self.life += 1

    def getPowerLevel(self):
        return self.power_level

    def setPowerLevel(self, power_level):
        self.power_level = power_level

    def getX(self):
        return self.rect.x

    def getY(self):
        return self.rect.y

    def apply_ai_action(self, action):
        """
        action is an array [X Axis, Y Axis]
        X -> 0: Left, 1: Stopped, 2: Right
        Y -> 0: Up,   1: Stopped, 2: Down
        """
        self.moving_left = action[0] == 0
        self.moving_right = action[0] == 2

        self.moving_up = action[1] == 0
        self.moving_down = action[1] == 2

        self.firing = True