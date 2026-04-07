import pygame
import math
from pygame.locals import *
import random
from collections import Counter
from time import time

from classes.Weapons import *
from game_engine import g_engine
from .GameState import GameState
from .States_util import draw_text, handle_analog_stick
from classes.particles.Fall import Fall
from classes.particles.LightRays import LightRays
from constants.global_var import config, CONTROLS, GAME_COLOR, TITLE_YELLOW_1
from constants.Utils import delta_time

BASE_UPGRADES = [
    {
        "id": "rear_shot",
        "name": "REAR SHOT",
        "desc": "Fires backwards",
        "color": (255, 150, 50),
        "type": "weapon",
        "category": "secondary_back",
        "weapon_class": RearShot,
    },
    {
        "id": "side_shot",
        "name": "SIDE SHOT",
        "desc": "Fires sideways",
        "color": (255, 180, 80),
        "type": "weapon",
        "category": "secondary_side",
        "weapon_class": SideShot,
    },
    {
        "id": "tracking_drones",
        "name": "TRACKING DRONES",
        "desc": "Auto-homing projectiles",
        "color": (120, 220, 255),
        "type": "weapon",
        "category": "auto_pod",
        "weapon_class": TrackingDrones,
    },
    {
        "id": "bomb_pod",
        "name": "BOMB POD",
        "desc": "Area-of-effect explosions",
        "color": (220, 88, 176),
        "type": "weapon",
        "category": "auto_pod", 
        "weapon_class": BombPod,
    },
    {
        "id": "burst_turret",
        "name": "BURST TURRET",
        "desc": "Spread burst attacks",
        "color": (255, 210, 110),
        "type": "weapon",
        "category": "primary", 
        "weapon_class": BurstTurret,
    },
    {
        "id": "reinforced_hull",
        "name": "REINFORCED HULL",
        "desc": "Heals and grants +1 max life",
        "color": (120, 160, 255),
        "type": "stat",
        "category": "passive",
        "stat_target": "life",
        "flat_bonus": 1,
        "max_stacks": 8,
        "repeatable": True,
    },
]

FUSIONS = [
    {
        "id": "fusion_bombardment",
        "name": "BOMBARDMENT",
        "desc": "FUSION: Explosive rain",
        "color": (220, 88, 176),
        "type": "fusion",
        "category": "ultimate",
        "requires": ["bomb_pod", "tracking_drones"],
        "weapon_class": BombardmentFusion,
    },
    {
        "id": "fusion_storm_wall",
        "name": "STORM WALL",
        "desc": "FUSION: Impenetrable side wall",
        "color": (255, 210, 110),
        "type": "fusion",
        "category": "ultimate",
        "requires": ["side_shot", "reinforced_hull"],
        "weapon_class": StormWallFusion,
    },
]

class LevelUp(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "Game"
        self.offered_upgrades = []
        self.selected = 0
        self.state_alpha = 0.0
        self.is_closing = False
        self.target_upgrade = None

    def _skill_counts(self):
        skills = getattr(g_engine.player, "acquired_skills", [])
        return Counter(skill["id"] for skill in skills if "id" in skill)

    def _get_owned_categories(self):
        skills = getattr(g_engine.player, "acquired_skills", [])
        return {skill.get("category") for skill in skills if "category" in skill}

    def _can_take_upgrade(self, upgrade, counts, owned_categories):
        owned_count = counts.get(upgrade["id"], 0)
        category = upgrade.get("category")

        if upgrade["type"] == "weapon" and owned_count == 0:
            if category in owned_categories:
                return False
            return True

        if upgrade["type"] == "weapon" and owned_count > 0:
            return False 

        if upgrade["type"] == "fusion":
            return owned_count == 0

        if upgrade["type"] == "stat":
            max_stacks = upgrade.get("max_stacks", 1)
            return owned_count < max_stacks

        return True

    def _build_offer_pool(self):
        counts = self._skill_counts()
        owned_ids = set(counts.keys())
        owned_categories = self._get_owned_categories()

        available_fusions = []
        for fusion in FUSIONS:
            if fusion["id"] in owned_ids:
                continue
            if all(req in owned_ids for req in fusion["requires"]):
                available_fusions.append(fusion)
                
        available_bases = []
        for upgrade in BASE_UPGRADES:
            if self._can_take_upgrade(upgrade, counts, owned_categories):
                available_bases.append(upgrade)
                
        return available_fusions, available_bases

    def start(self):
        self.selected = 0
        self.last_time = time()
        self.state_alpha = 0.0
        self.is_closing = False
        self.target_upgrade = None
        
        if g_engine.player:
            g_engine.player.last_hit = pygame.time.get_ticks() + 1500

        self.fall_1 = Fall(amount=35, min_s=15, max_s=40, color=TITLE_YELLOW_1, size=2)
        self.fall_2 = Fall(amount=35, min_s=15, max_s=40, color=(100, 200, 255), size=2)
        self.rays_1 = LightRays(amount=20, color=TITLE_YELLOW_1, min_speed=600, max_speed=1000, alpha=160, width=3, length=120, direction=-1)
        self.rays_2 = LightRays(amount=15, color=(255, 150, 220), min_speed=800, max_speed=1400, alpha=200, width=2, length=200, direction=-1)

        available_fusions, available_bases = self._build_offer_pool()
        counts = self._skill_counts()
        self.offered_upgrades = []

        if available_fusions:
            chosen_fusion = dict(random.choice(available_fusions))
            chosen_fusion["next_level"] = "MAX FUSION"
            self.offered_upgrades.append(chosen_fusion)

        needed_cards = 3 - len(self.offered_upgrades)
        if needed_cards > 0 and available_bases:
            random.shuffle(available_bases)
            for base in available_bases[:needed_cards]:
                card = dict(base)
                owned = counts.get(card["id"], 0)
                if card["type"] == "weapon":                
                    card["next_level"] = "NEW WEAPON"
                else:
                    if owned == 0:
                        card["next_level"] = "NEW!"
                    else:
                        card["next_level"] = f"Level {owned + 1}"
                self.offered_upgrades.append(card)

        if not self.offered_upgrades:
            self.offered_upgrades = [
                {
                    "id": "reinforced_hull",
                    "name": "REINFORCED HULL",
                    "desc": "Heals and grants +1 max life",
                    "color": (120, 160, 255),
                    "type": "stat",
                    "stat_target": "life",
                    "flat_bonus": 1,
                    "max_stacks": 999,
                    "repeatable": True,
                    "next_level": "REPEATABLE"
                }
            ]
        self.selected = min(self.selected, len(self.offered_upgrades) - 1)

    def apply_upgrade(self):
        if not self.offered_upgrades or self.is_closing:
            return
        pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_confirm"))
        self.target_upgrade = self.offered_upgrades[self.selected]
        self.is_closing = True

    def _execute_upgrade(self):
        choice = self.target_upgrade
        player = g_engine.player

        if not hasattr(player, "acquired_skills"):
            player.acquired_skills = []
        if not hasattr(player, "active_weapons"):
            player.active_weapons = {}
        if not hasattr(player, "weapon_levels"):
            player.weapon_levels = {}

        player.acquired_skills.append(dict(choice))

        if choice["type"] in ("weapon", "fusion"):
            player.active_weapons[choice["id"]] = choice["weapon_class"]()
            
            current_lvl = player.weapon_levels.get(choice["id"], 0)
            player.weapon_levels[choice["id"]] = min(current_lvl + 1, 3)

        elif choice["type"] == "stat":
            target = choice["stat_target"]
            current_val = getattr(player, target, 0)
            if "multiplier" in choice:
                setattr(player, target, current_val * choice["multiplier"])
            elif "flat_bonus" in choice:
                setattr(player, target, current_val + choice["flat_bonus"])

        if g_engine.player:
            g_engine.player.last_hit = pygame.time.get_ticks() + 1500

        self.next_state = "Game"
        self.done = True

    def update(self):
        dt, self.last_time = delta_time(self.last_time)
        self.fall_1.update(gravity=30, wind=120, dt=dt)
        self.fall_2.update(gravity=-80, wind=-120, dt=dt)
        self.rays_1.update(dt)
        self.rays_2.update(dt)

        fade_speed = 800.0
        if self.is_closing:
            self.state_alpha = max(0.0, self.state_alpha - fade_speed * dt)
            if self.state_alpha <= 0:
                self._execute_upgrade()
        else:
            self.state_alpha = min(255.0, self.state_alpha + fade_speed * dt)

    def draw(self, surf):
        w, h = config.INTERNAL_RESOLUTION
        time_now = pygame.time.get_ticks()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((10, 15, 20, int(180 * (self.state_alpha / 255.0))))
        surf.blit(overlay, (0, 0))

        self.rays_1.draw(surf)
        self.rays_2.draw(surf)

        ui_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        self.fall_1.draw(ui_surf)
        self.fall_2.draw(ui_surf)

        slide_offset_y = (255 - self.state_alpha) * 1.5
        title_y = h * 0.15 + math.sin(time_now * 0.003) * 5 - (slide_offset_y * 0.5)
        draw_text(ui_surf, "WAVE REWARD", w / 2, title_y, TITLE_YELLOW_1)
        draw_text(ui_surf, "CHOOSE AN UPGRADE", w / 2, title_y + 40, use_smaller_font=True)

        card_count = max(1, len(self.offered_upgrades))
        card_w = int(w * 0.22)
        card_h = int(h * 0.45)
        gap = int(w * 0.05)

        if card_count == 1:
            start_x = int(w / 2 - card_w / 2)
        else:
            start_x = int((w - (card_count * card_w + (card_count - 1) * gap)) / 2)

        base_y = int(h * 0.30) + slide_offset_y

        for i, upgrade in enumerate(self.offered_upgrades):
            x = start_x + i * (card_w + gap)
            is_selected = (i == self.selected)
            is_fusion = upgrade.get("type") == "fusion"

            float_y = math.sin(time_now * 0.005 + i) * 15 if is_selected else 0
            y = int(base_y + float_y)
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)

            if is_fusion:
                bg_color = (60, 30, 30, 240) if is_selected else (40, 20, 20, 180)
                pulse = abs(math.sin(time_now * 0.006))
                border_color = (255, int(150 + 100 * pulse), 50)
                border_thick = 5 if is_selected else 3
            else:
                bg_color = (40, 50, 60, 230) if is_selected else (20, 25, 30, 150)
                border_color = TITLE_YELLOW_1 if is_selected else (100, 100, 100, 150)
                border_thick = 4 if is_selected else 2

            if is_selected:
                glow_alpha = abs(math.sin(time_now * 0.008)) * 100 + 50
                aura_rect = pygame.Rect(x - 10, y - 10, card_w + 20, card_h + 20)
                pygame.draw.rect(ui_surf, (*border_color[:3], int(glow_alpha)), aura_rect, border_radius=20)
            elif is_fusion:
                glow_alpha = abs(math.sin(time_now * 0.004)) * 40 + 20
                aura_rect = pygame.Rect(x - 5, y - 5, card_w + 10, card_h + 10)
                pygame.draw.rect(ui_surf, (*border_color[:3], int(glow_alpha)), aura_rect, border_radius=20)

            pygame.draw.rect(card_surf, bg_color, card_surf.get_rect(), border_radius=15)
            pygame.draw.rect(card_surf, border_color, card_surf.get_rect(), border_thick, border_radius=15)
            
            if is_selected:
                draw_text(ui_surf, "V", x + card_w / 2, y - 30, border_color)

            ui_surf.blit(card_surf, (x, y))

            draw_text(
                ui_surf,
                upgrade["name"],
                x + card_w / 2,
                y + card_h * 0.2,
                upgrade.get("color", (255, 255, 255)),
                use_smaller_font=True,
            )
            
            level_text = upgrade.get("next_level", "")
            draw_text(
                ui_surf,
                level_text,
                x + card_w / 2,
                y + card_h * 0.4,
                (100, 255, 100) if "NEW" in level_text or "FUSION" in level_text else (200, 200, 200),
                use_smaller_font=True,
            )

            draw_text(
                ui_surf,
                upgrade["desc"],
                x + card_w / 2,
                y + card_h * 0.65,
                (200, 200, 200),
                use_smaller_font=True,
            )

        panel_y = h * 0.85 + (slide_offset_y * 1.5)
        draw_text(ui_surf, "ACQUIRED SKILLS", w / 2, panel_y, (150, 150, 150), use_smaller_font=True)

        skills = g_engine.player.acquired_skills

        unique_skills = []
        seen_ids = set()
        for s in skills:
            if s["id"] not in seen_ids:
                unique_skills.append(s)
                seen_ids.add(s["id"])

        icon_size = 30
        icon_gap = 10
        total_w = (len(unique_skills) * icon_size) + max(0, (len(unique_skills) - 1) * icon_gap)
        icon_start_x = (w - total_w) / 2
        icon_y = panel_y + 30

        for idx, skill in enumerate(unique_skills):
            icon_rect = pygame.Rect(icon_start_x + idx * (icon_size + icon_gap), icon_y, icon_size, icon_size)
            pygame.draw.rect(ui_surf, skill.get("color", (200, 200, 200)), icon_rect, border_radius=5)
            pygame.draw.rect(ui_surf, (255, 255, 255), icon_rect, 1, border_radius=5)

        ui_surf.set_alpha(int(self.state_alpha))
        surf.blit(ui_surf, (0, 0))

    def get_event(self, event):
        if self.is_closing:
            return

        if event.type == KEYDOWN:
            if event.key in CONTROLS["LEFT"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.selected = max(0, self.selected - 1)
            elif event.key in CONTROLS["RIGHT"]:
                pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                self.selected = min(len(self.offered_upgrades) - 1, self.selected + 1)
            elif event.key in CONTROLS["START"]:
                self.apply_upgrade()

        if event.type == JOYHATMOTION:
            if event.hat == 0:
                x, y = event.value
                if x == -1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.selected = max(0, self.selected - 1)
                elif x == 1:
                    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
                    self.selected = min(len(self.offered_upgrades) - 1, self.selected + 1)

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                self.apply_upgrade()

        if event.type == JOYAXISMOTION and config.use_analog_stick:
            handle_analog_stick(self, event)