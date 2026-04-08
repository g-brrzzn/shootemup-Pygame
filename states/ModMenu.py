import pygame
import math
from pygame.locals import *
from time import time

from game_engine import g_engine
from .GameState import GameState
from .States_util import draw_text, handle_analog_stick
from classes.particles.Fall import Fall
from classes.PowerUp import PowerUp
from constants.global_var import config, CONTROLS
from constants.Utils import delta_time

class ModMenu(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "Game"
        self.selected = 0
        self.state_alpha = 0.0

    def start(self):
        self.selected = 0
        self.last_time = time()
        self.state_alpha = 0.0
        self.fall = Fall(amount=60, min_s=20, max_s=50, color=(255, 50, 100), size=2)
        
        self.god_mode = getattr(g_engine.player, 'god_mode', False)
        self.inf_ricochet = getattr(g_engine.player, 'infinite_ricochet', False)
        if not hasattr(g_engine, 'show_hitboxes'):
            g_engine.show_hitboxes = False

    def update(self):
        dt, self.last_time = delta_time(self.last_time)
        self.fall.update(gravity=40, wind=0, dt=dt)
        self.state_alpha = min(255.0, self.state_alpha + 1000.0 * dt)

    def draw(self, surf):
        w, h = config.INTERNAL_RESOLUTION
        time_now = pygame.time.get_ticks()

        ui_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        ui_surf.fill((10, 5, 15, 210))
        self.fall.draw(ui_surf)

        title_y = h * 0.15 + math.sin(time_now * 0.003) * 5
        draw_text(ui_surf, "MOD MENU", w / 2, title_y, (255, 50, 100))
        draw_text(ui_surf, "DEBUG & CHEATS", w / 2, title_y + 40, use_smaller_font=True)

        p_life = g_engine.player.getLife() if g_engine.player else 0
        p_power = g_engine.player.getPowerLevel() if g_engine.player else 0
        p_delay = g_engine.player.shot_delay if g_engine.player else 0.25

        self.options = [
            f"< PLAYER LIFE : {p_life} >",
            f"< POWER LEVEL : {p_power} >",
            f"< SHOT DELAY : {p_delay:.2f} >",
            f"SHOW HITBOXES : {'ON' if getattr(g_engine, 'show_hitboxes', False) else 'OFF'}",
            f"INFINITE RICOCHET : {'ON' if self.inf_ricochet else 'OFF'}",
            f"GOD MODE : {'ON' if self.god_mode else 'OFF'}",
            "INSTANT LEVEL UP",
            "WIPE SCREEN",
            "RESUME"
        ]

        base_y = int(h * 0.35)
        gap = 45

        for i, option in enumerate(self.options):
            y = base_y + (i * gap)
            is_selected = (i == self.selected)

            color = (200, 200, 200)
            if is_selected:
                color = (255, 50, 100)
                float_x = math.sin(time_now * 0.01) * 10
                draw_text(ui_surf, ">", w / 2 - 240 + float_x, y, color)
                draw_text(ui_surf, "<", w / 2 + 240 - float_x, y, color)

            draw_text(ui_surf, option, w / 2, y, color, use_smaller_font=True)

        ui_surf.set_alpha(int(self.state_alpha))
        surf.blit(ui_surf, (0, 0))

    def execute_action(self, action_idx, direction=0):
        if not g_engine.player:
            return

        if action_idx == 0:
            if direction > 0: g_engine.player.gain_life()
            elif direction < 0: g_engine.player.setLife(max(1, g_engine.player.getLife() - 1))
        
        elif action_idx == 1:
            if direction > 0: g_engine.player.upgrade()
            elif direction < 0: g_engine.player.setPowerLevel(max(1, g_engine.player.getPowerLevel() - 1))
        
        elif action_idx == 2:
            if direction > 0: g_engine.player.shot_delay = min(1.0, g_engine.player.shot_delay + 0.05)
            elif direction < 0: g_engine.player.shot_delay = max(0.0, g_engine.player.shot_delay - 0.05)
        
        elif action_idx == 3 and direction == 0:
            g_engine.show_hitboxes = not getattr(g_engine, 'show_hitboxes', False)
            
        elif action_idx == 4 and direction == 0:
            self.inf_ricochet = not self.inf_ricochet
            g_engine.player.infinite_ricochet = self.inf_ricochet
            g_engine.player.ricochet_timer = 6.0 if self.inf_ricochet else 0.0
            
        elif action_idx == 5 and direction == 0:
            self.god_mode = not self.god_mode
            g_engine.player.god_mode = self.god_mode
            
        elif action_idx == 6 and direction == 0:
            self.next_state = "LevelUp"
            self.done = True
            
        elif action_idx == 7 and direction == 0:
            for enemy in list(g_engine.all_enemies):
                enemy.life = 1
                enemy.damage()
                
        elif action_idx == 8 and direction == 0:
            if hasattr(g_engine.player, 'reset_movement'):
                g_engine.player.reset_movement()
            self.next_state = "Game"
            self.done = True

    def get_event(self, event):
        if event.type == KEYDOWN:
            if event.key in CONTROLS["UP"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in CONTROLS["DOWN"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in CONTROLS["LEFT"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.execute_action(self.selected, -1)
            elif event.key in CONTROLS["RIGHT"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.execute_action(self.selected, 1)
            elif event.key in CONTROLS["START"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                self.execute_action(self.selected, 0)
            elif event.key in CONTROLS.get("MOD_MENU", [K_BACKSPACE]) or event.key in CONTROLS["ESC"]:
                if hasattr(g_engine.player, 'reset_movement'):
                    g_engine.player.reset_movement()
                self.next_state = "Game"
                self.done = True

        if event.type == JOYHATMOTION:
            if event.hat == 0:
                x, y = event.value
                if y == 1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.selected = (self.selected - 1) % len(self.options)
                elif y == -1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.selected = (self.selected + 1) % len(self.options)
                if x == -1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.execute_action(self.selected, -1)
                elif x == 1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.execute_action(self.selected, 1)

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
                self.execute_action(self.selected, 0)
            elif event.button in [4, 6]:
                if hasattr(g_engine.player, 'reset_movement'):
                    g_engine.player.reset_movement()
                self.next_state = "Game"
                self.done = True

            if g_engine.platform == "Darwin":
                if event.button == 11:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.button == 12:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.button == 13:
                    self.execute_action(self.selected, -1)
                elif event.button == 14:
                    self.execute_action(self.selected, 1)

        if event.type == JOYDEVICEADDED:
            g_engine.joystick = pygame.joystick.Joystick(event.device_index)
        if event.type == JOYDEVICEREMOVED:
            g_engine.joystick = None

        if event.type == JOYAXISMOTION and config.use_analog_stick:
            handle_analog_stick(self, event)