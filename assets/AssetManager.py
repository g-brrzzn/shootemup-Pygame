import pygame
import sys
from pathlib import Path

from constants.Utils import create_glow_surface
from constants.global_var import PLAYER_COLOR_GREEN, TITLE_YELLOW_1


def get_assets_dir():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).resolve().parent


ASSET_DIR = get_assets_dir()


class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

        self._generate_glows()

    def load_assets(self, scale_factor):
        self._load_images(scale_factor)
        self._load_sounds()
        self._load_fonts()

    def get_image(self, key):
        if key not in self.images:
            raise KeyError(f"[AssetManager] Image not found: '{key}'")
        return self.images[key]

    def get_sound(self, key):
        if key not in self.sounds:
            raise KeyError(f"[AssetManager] Sound not found: '{key}'")
        return self.sounds[key]

    def get_font(self, key):
        if key not in self.fonts:
            raise KeyError(f"[AssetManager] Font not found: '{key}'")
        return self.fonts[key]

    def _load_images(self, scale_factor):
        p = Path

        # Player
        self.images['player_idle1'] = self._load_sprite(p('sprites/player/player_idle1.png'), (16 * scale_factor, 24 * scale_factor))
        self.images['player_idle2'] = self._load_sprite(p('sprites/player/player_idle2.png'), (16 * scale_factor, 24 * scale_factor))

        # Bullets
        self.images['bullet_player'] = self._load_sprite(p('sprites/bullet/Bullet.png'), (16, 16))
        self.images['bullet_enemy']  = self._load_sprite(p('sprites/bullet/enemy_bullet.png'), (16, 16))

        # Enemies
        for i in range(1, 4):
            for j in range(1, 3):
                key = f'enemy{i}_{j}'
                path = p(f'sprites/enemies/enemy_{i}/enemy_{i}_{j}.png')
                self.images[key] = self._load_sprite(path, scale=scale_factor, flip_y=True)

        # Boss
        for i in range(1, 3):
            key = f'boss_1_{i}'
            path = p(f'sprites/enemies/boss_1/boss_1_{i}.png')
            self.images[key] = self._load_sprite(path, scale=scale_factor * 2, flip_y=True)

        # Powerups
        self.images['life_powerup'] = self._load_sprite(p('sprites/powerups/life_powerup.png'), scale=scale_factor)
        self.images['weapon_powerup'] = self._load_sprite(p('sprites/powerups/weapon_powerup.png'), scale=scale_factor)

        # Icon
        self.images["icon"] = self._load_sprite(p('sprites/player/player_idle1.png'), (32, 32))

    def _load_sounds(self):
        p = Path

        self.sounds['shoot'] = self._load_sound(p('sound/shoot.mp3'))
        self.sounds['hit'] = self._load_sound(p('sound/hit.mp3'))
        self.sounds['menu_select'] = self._load_sound(p('sound/impactMetal_002.ogg'))
        self.sounds['menu_confirm'] = self._load_sound(p('sound/forceField_001.mp3'))

        self.sounds['music'] = str(self._resolve_path(p('sound/victory.mp3')))

    def _load_fonts(self):
        p = Path

        self.fonts['captain_32'] = self._load_font(p('font/American Captain.ttf'), 32)
        self.fonts['captain_42'] = self._load_font(p('font/American Captain.ttf'), 42)
        self.fonts['captain_80'] = self._load_font(p('font/American Captain.ttf'), 80)



    def _resolve_path(self, relative_path: Path) -> Path:
        full_path = ASSET_DIR / relative_path

        if not full_path.exists():
            raise FileNotFoundError(
                f"\n[AssetManager ERROR]\n"
                f"Missing asset: {relative_path}\n"
                f"Resolved path: {full_path}\n"
                f"ASSET_DIR: {ASSET_DIR}\n"
            )

        return full_path

    def _load_image(self, path: Path):
        return pygame.image.load(str(self._resolve_path(path))).convert_alpha()

    def _load_sprite(self, path: Path, new_size=None, scale=None, flip_y=False):
        sprite = self._load_image(path)

        if flip_y:
            sprite = pygame.transform.flip(sprite, False, True)

        if scale:
            new_size = (
                int(sprite.get_width() * scale),
                int(sprite.get_height() * scale),
            )

        if new_size:
            sprite = pygame.transform.scale(sprite, new_size)

        sprite.set_colorkey((0, 0, 0))
        return sprite

    def _load_sound(self, path: Path):
        return pygame.mixer.Sound(str(self._resolve_path(path)))

    def _load_font(self, path: Path, size):
        return pygame.font.Font(str(self._resolve_path(path)), size)



    def _generate_glows(self):
        self.images['glow_bullet_player'] = create_glow_surface(25, (255, 0, 255))
        self.images['glow_bullet_enemy'] = create_glow_surface(25, TITLE_YELLOW_1)
        self.images['glow_player'] = create_glow_surface(45, PLAYER_COLOR_GREEN)