import pygame
import math
from pygame.locals import *
from time import time

from game_engine import g_engine
from .GameState import GameState
from .States_util import draw_text, vertical
from classes.particles.Fall import Fall
from constants.global_var import config, CONTROLS, GAME_COLOR, PLAYER_COLOR_GREEN, TITLE_YELLOW_1
from constants.Utils import delta_time


class ControlsScreen(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "Game"
        self.last_time = time()
        self.state_alpha = 0.0

        self.fall_back = Fall(amount=35, min_s=5, max_s=12, color=(50, 50, 60), size=1)
        self.fall_mid = Fall(amount=25, min_s=15, max_s=25, color=(90, 90, 100), size=2)
        self.fall_front = Fall(amount=15, min_s=30, max_s=45, color=(150, 150, 160), size=3)

        self.using_gamepad = False

    def start(self):
        self.last_time = time()
        self.state_alpha = 0.0
        self.using_gamepad = False

        self.life_img = g_engine.assets.get_image("life_powerup")
        self.weapon_img = g_engine.assets.get_image("weapon_powerup")

        self.ricochet_img = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.ricochet_img, (50, 150, 255), (0, 0, 20, 20), border_radius=5)
        pygame.draw.rect(self.ricochet_img, (255, 255, 255), (0, 0, 20, 20), 2, border_radius=5)
        pygame.draw.circle(self.ricochet_img, (255, 255, 255), (10, 10), 5)

    def _draw_panel(self, surf, rect, fill=(12, 14, 20, 210), border=(255, 255, 255, 35), radius=24):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, fill, panel.get_rect(), border_radius=radius)
        pygame.draw.rect(panel, border, panel.get_rect(), 2, border_radius=radius)
        surf.blit(panel, rect.topleft)

    def _draw_keycap(self, surf, center, text, w=40, h=40, is_pressed=False):
        rect = pygame.Rect(0, 0, w, h)
        rect.center = center
        
        fill = (50, 120, 255, 240) if is_pressed else (28, 31, 42, 230)
        border = (150, 200, 255, 255) if is_pressed else (255, 255, 255, 60)
        text_color = (255, 255, 255) if is_pressed else (240, 240, 240)

        keycap = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(keycap, fill, keycap.get_rect(), border_radius=8)
        pygame.draw.rect(keycap, border, keycap.get_rect(), 2, border_radius=8)
        surf.blit(keycap, rect.topleft)
        
        draw_text(surf, text, rect.centerx, rect.centery + 2, text_color)

    def _draw_card_bg(self, surf, rect, accent=(255, 255, 255)):
        self._draw_panel(surf, rect, fill=(16, 18, 26, 215), border=(255, 255, 255, 40), radius=18)
        accent_bar = pygame.Surface((8, rect.height - 18), pygame.SRCALPHA)
        pygame.draw.rect(accent_bar, accent, accent_bar.get_rect(), border_radius=8)
        surf.blit(accent_bar, (rect.x + 10, rect.y + 9))

    def _draw_powerup_card(self, surf, rect, title, subtitle, icon_surf, accent):
        self._draw_card_bg(surf, rect, accent)
        icon_rect = icon_surf.get_rect(center=(rect.centerx, rect.y + int(rect.height * 0.30)))
        surf.blit(icon_surf, icon_rect)
        draw_text(surf, title, rect.centerx, rect.y + int(rect.height * 0.55), accent, True)
        draw_text(surf, subtitle, rect.centerx, rect.bottom - int(rect.height * 0.15), (210, 210, 210))

    def _draw_control_card(self, surf, rect, title, accent):
        self._draw_card_bg(surf, rect, accent)
        title_y = rect.y + int(rect.height * 0.28)
        draw_text(surf, title, rect.centerx, title_y, accent, True)

    def update(self):
        dt, self.last_time = delta_time(self.last_time)
        
        self.fall_back.update(gravity=15, wind=0, dt=dt)
        self.fall_mid.update(gravity=25, wind=0, dt=dt)
        self.fall_front.update(gravity=40, wind=0, dt=dt)
        
        self.state_alpha = min(255.0, self.state_alpha + 800.0 * dt)

    def draw(self, surf):
        w, h = config.INTERNAL_RESOLUTION
        time_now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        ui_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        vertical(ui_surf, False)
        
        self.fall_back.draw(ui_surf)
        self.fall_mid.draw(ui_surf)
        self.fall_front.draw(ui_surf)

        dark_overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        dark_overlay.fill((5, 6, 10, 70))
        ui_surf.blit(dark_overlay, (0, 0))

        main_rect = pygame.Rect(int(w * 0.10), int(h * 0.08), int(w * 0.80), int(h * 0.84))
        self._draw_panel(ui_surf, main_rect, fill=(10, 12, 18, 210), border=(255, 255, 255, 30), radius=28)

        title_y = h * 0.16 + math.sin(time_now * 0.003) * 4
        font_80 = g_engine.assets.get_font("captain_80")
        title_surf = font_80.render("CONTROLS", True, PLAYER_COLOR_GREEN)
        title_rect = title_surf.get_rect(center=(w / 2, title_y))
        ui_surf.blit(title_surf, title_rect)

        mode_text = "GAMEPAD DETECTED" if self.using_gamepad else "KEYBOARD & MOUSE"
        draw_text(ui_surf, mode_text, w / 2, h * 0.23, (180, 180, 180))

        section_top = int(h * 0.30)
        draw_text(ui_surf, "ACTIONS", w / 2, section_top, TITLE_YELLOW_1)

        card_w = int(w * 0.22)
        card_h = int(h * 0.16)
        gap = int(w * 0.02)
        
        total_top_w = card_w * 3 + gap * 2
        start_x = int(w / 2 - total_top_w / 2)
        card_y = int(h * 0.35)

        move_rect = pygame.Rect(start_x, card_y, card_w, card_h)
        shoot_rect = pygame.Rect(start_x + card_w + gap, card_y, card_w, card_h)
        parry_rect = pygame.Rect(start_x + (card_w + gap) * 2, card_y, card_w, card_h)

        self._draw_control_card(ui_surf, move_rect, "MOVE", (190, 190, 190))
        self._draw_control_card(ui_surf, shoot_rect, "SHOOT", PLAYER_COLOR_GREEN)
        self._draw_control_card(ui_surf, parry_rect, "PARRY", GAME_COLOR)

        center_y = card_y + int(card_h * 0.68)

        if not self.using_gamepad:
            w_press = keys[K_w]
            a_press = keys[K_a]
            s_press = keys[K_s]
            d_press = keys[K_d]
            
            self._draw_keycap(ui_surf, (move_rect.centerx, center_y - 21), "W", w=36, h=36, is_pressed=w_press)
            self._draw_keycap(ui_surf, (move_rect.centerx - 40, center_y + 21), "A", w=36, h=36, is_pressed=a_press)
            self._draw_keycap(ui_surf, (move_rect.centerx, center_y + 21), "S", w=36, h=36, is_pressed=s_press)
            self._draw_keycap(ui_surf, (move_rect.centerx + 40, center_y + 21), "D", w=36, h=36, is_pressed=d_press)

            spc_press = keys[K_SPACE]
            self._draw_keycap(ui_surf, (shoot_rect.centerx, center_y), "SPACE", w=120, h=40, is_pressed=spc_press)

            prry_press = keys[K_LSHIFT] or keys[K_f]
            self._draw_keycap(ui_surf, (parry_rect.centerx, center_y), "SHIFT / F", w=130, h=40, is_pressed=prry_press)

        else:
            up_press = False
            left_press = False
            down_press = False
            right_press = False
            shoot_btn_press = False
            parry_btn_press = False

            if pygame.joystick.get_count() > 0:
                joy = pygame.joystick.Joystick(0)
                
                if joy.get_numhats() > 0:
                    hat = joy.get_hat(0)
                    if hat[0] == -1: left_press = True
                    if hat[0] == 1: right_press = True
                    if hat[1] == 1: up_press = True
                    if hat[1] == -1: down_press = True

                if joy.get_numaxes() >= 2:
                    if joy.get_axis(0) < -0.3: left_press = True
                    if joy.get_axis(0) > 0.3: right_press = True
                    if joy.get_axis(1) < -0.3: up_press = True
                    if joy.get_axis(1) > 0.3: down_press = True
                    
                if joy.get_numbuttons() > 0:
                    shoot_btn_press = joy.get_button(0)
                    if joy.get_numbuttons() > 2:
                        parry_btn_press = joy.get_button(2)

            self._draw_keycap(ui_surf, (move_rect.centerx, center_y - 21), "^", w=36, h=36, is_pressed=up_press)
            self._draw_keycap(ui_surf, (move_rect.centerx - 40, center_y + 21), "<", w=36, h=36, is_pressed=left_press)
            self._draw_keycap(ui_surf, (move_rect.centerx, center_y + 21), "v", w=36, h=36, is_pressed=down_press)
            self._draw_keycap(ui_surf, (move_rect.centerx + 40, center_y + 21), ">", w=36, h=36, is_pressed=right_press)

            self._draw_keycap(ui_surf, (shoot_rect.centerx, center_y), "A / RT", w=110, h=40, is_pressed=shoot_btn_press)
            self._draw_keycap(ui_surf, (parry_rect.centerx, center_y), "X / LT", w=110, h=40, is_pressed=parry_btn_press)

        draw_text(ui_surf, "POWER-UPS", w / 2, h * 0.58, TITLE_YELLOW_1)

        p_y = int(h * 0.63)
        power_card_w = int(w * 0.18)
        power_card_h = int(h * 0.18)
        power_gap = int(w * 0.03)
        total_w = power_card_w * 3 + power_gap * 2
        power_x = int(w / 2 - total_w / 2)

        life_rect = pygame.Rect(power_x, p_y, power_card_w, power_card_h)
        weapon_rect = pygame.Rect(power_x + power_card_w + power_gap, p_y, power_card_w, power_card_h)
        ricochet_rect = pygame.Rect(power_x + (power_card_w + power_gap) * 2, p_y, power_card_w, power_card_h)

        self._draw_powerup_card(ui_surf, life_rect, "LIFE", "Extra life", self.life_img, (255, 80, 80))
        self._draw_powerup_card(ui_surf, weapon_rect, "POWER", "Weapon up", self.weapon_img, PLAYER_COLOR_GREEN)
        self._draw_powerup_card(ui_surf, ricochet_rect, "RICOCHET", "Bouncing shots", self.ricochet_img, (50, 150, 255))

        blink_alpha = abs(math.sin(time_now * 0.005)) * 255
        
        continue_text = "PRESS A / START TO CONTINUE" if self.using_gamepad else "PRESS SPACE TO CONTINUE"
        footer = g_engine.assets.get_font("captain_32").render(continue_text, True, (255, 255, 255))
        footer.set_alpha(int(blink_alpha))
        footer_rect = footer.get_rect(center=(w / 2, int(h * 0.90)))
        ui_surf.blit(footer, footer_rect)

        ui_surf.set_alpha(int(self.state_alpha))
        surf.blit(ui_surf, (0, 0))

    def get_event(self, event):
        if event.type == KEYDOWN:
            self.using_gamepad = False
            if event.key in CONTROLS["START"] or event.key == K_SPACE:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                g_engine.has_seen_controls = True
                self.done = True

        elif event.type in (JOYBUTTONDOWN, JOYHATMOTION, JOYAXISMOTION):
            if event.type == JOYAXISMOTION and abs(event.value) < 0.3:
                return
                
            self.using_gamepad = True
            
            if event.type == JOYBUTTONDOWN:
                if event.button == 0 or event.button == 7:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                    g_engine.has_seen_controls = True
                    self.done = True