import pygame
import math
from game_engine import g_engine
from constants.global_var import config
from states.States_util import draw_text

class HUD:
    def __init__(self):
        self.icon_size = 24
        self.margin = 20

    def _draw_timer_icon(self, surf, x, y, current_time, max_time, color):
        rect = pygame.Rect(x, y, self.icon_size, self.icon_size)
        pygame.draw.circle(surf, (40, 40, 40), rect.center, self.icon_size // 2)
        
        fill_fraction = max(0, current_time / max_time)
        if fill_fraction > 0:
            start_angle = -math.pi / 2
            end_angle = start_angle + (2 * math.pi * fill_fraction)
            points = [rect.center]
            for i in range(int(fill_fraction * 30) + 2):
                angle = start_angle + (end_angle - start_angle) * (i / (int(fill_fraction * 30) + 1))
                points.append((rect.centerx + math.cos(angle) * (self.icon_size // 2),
                               rect.centery + math.sin(angle) * (self.icon_size // 2)))
            if len(points) > 2:
                pygame.draw.polygon(surf, color, points)

        pygame.draw.circle(surf, (200, 200, 200), rect.center, self.icon_size // 2, 1)

    def draw(self, surf, clock, fill_pct):
        w, h = config.INTERNAL_RESOLUTION
        player = g_engine.player

        if player and player.getLife() > 0:
            bar_w, bar_h = w * 0.4, 8
            x_pos = (w - bar_w) // 2
            pygame.draw.rect(surf, (20, 30, 35), (x_pos, 15, bar_w, bar_h))
            pygame.draw.rect(surf, (0, 255, 150), (x_pos, 15, int(fill_pct * bar_w), bar_h))
            pygame.draw.rect(surf, (200, 200, 200), (x_pos, 15, bar_w, bar_h), 1)

        if player:
            level_icon_x = self.margin
            level_icon_y = h - self.margin - 30
            
            powerup_img = g_engine.assets.get_image("weapon_powerup")
            powerup_icon = pygame.transform.scale(powerup_img, (24, 24))
            
            for i in range(player.power_level):
                surf.blit(powerup_icon, (level_icon_x + (i * 30), level_icon_y))

            current_effect_y = level_icon_y - 35
            
            if getattr(player, 'ricochet_timer', 0) > 0:
                self._draw_timer_icon(surf, self.margin, current_effect_y, player.ricochet_timer, 6.0, (50, 150, 255))
                current_effect_y -= 30
            
            if getattr(player, 'overdrive_timer', 0) > 0:
                self._draw_timer_icon(surf, self.margin, current_effect_y, player.overdrive_timer, 3.0, (255, 105, 180))
                current_effect_y -= 30

            current_time = pygame.time.get_ticks()
            inv_remaining = 0
            inv_max = 1.0

            if current_time < player.last_hit:
                inv_remaining = (player.last_hit - current_time) / 1000.0
                inv_max = 3.0
            elif current_time - player.last_hit < player.invincibility_duration:
                inv_remaining = (player.invincibility_duration - (current_time - player.last_hit)) / 1000.0
                inv_max = player.invincibility_duration / 1000.0

            if inv_remaining > 0:
                self._draw_timer_icon(surf, self.margin, current_effect_y, inv_remaining, inv_max, (255, 255, 255))
                current_effect_y -= 30

        draw_text(surf, f"Score {g_engine.score:06d}", w / 2, 45)
        draw_text(surf, f"Wave {g_engine.level}", w - 60, h - 30)
        draw_text(surf, f"Life {max(0, player.getLife() if player else 0)}", w - 60, h - 60)

        if config.show_fps and clock:
            draw_text(surf, f"FPS {int(clock.get_fps())}", 50, 30)