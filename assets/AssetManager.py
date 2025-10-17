import pygame
import os

ASSET_DIR = os.path.join(os.path.dirname(__file__))

class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def load_assets(self, scale_factor):
        self._load_images(scale_factor)
        self._load_sounds()
        self._load_fonts()

    def _load_images(self, scale_factor):
        # Player
        self.images['player_idle1'] = self._load_sprite(os.path.join('sprites', 'player', 'player_idle1.png'), (16 * scale_factor, 24 * scale_factor))
        self.images['player_idle2'] = self._load_sprite(os.path.join('sprites', 'player', 'player_idle2.png'), (16 * scale_factor, 24 * scale_factor))

        # Bullet
        self.images['bullet_player'] = self._load_sprite(os.path.join('sprites', 'bullet', 'Bullet.png'),       (16 * 1, 16 * 1))
        self.images['bullet_enemy']  = self._load_sprite(os.path.join('sprites', 'bullet', 'enemy_bullet.png'), (16 * 1, 16 * 1))
        
        # Enemies
        self.images['enemy1_1'] = self._load_sprite(os.path.join('sprites', 'enemies', 'enemy_1', 'enemy_1_1.png'), scale=scale_factor, flip_y=True)
        self.images['enemy1_2'] = self._load_sprite(os.path.join('sprites', 'enemies', 'enemy_1', 'enemy_1_2.png'), scale=scale_factor, flip_y=True)
        
        self.images['enemy2_1'] = self._load_sprite(os.path.join('sprites', 'enemies', 'enemy_2', 'enemy_2_1.png'), scale=scale_factor, flip_y=True)
        self.images['enemy2_2'] = self._load_sprite(os.path.join('sprites', 'enemies', 'enemy_2', 'enemy_2_2.png'), scale=scale_factor, flip_y=True)
        
        self.images['enemy3_1'] = self._load_sprite(os.path.join('sprites', 'enemies', 'enemy_3', 'enemy_3_1.png'), scale=scale_factor, flip_y=True)
        self.images['enemy3_2'] = self._load_sprite(os.path.join('sprites', 'enemies', 'enemy_3', 'enemy_3_2.png'), scale=scale_factor, flip_y=True)
        
        # Other
        self.images['icon'] = self._load_image(os.path.join('sprites', 'player', 'player_idle1.png'))


    def _load_sounds(self):
        self.sounds['shoot'] = self._load_sound(os.path.join('sound', 'shoot.mp3'))
        self.sounds['hit'] = self._load_sound(os.path.join('sound', 'hit.mp3'))
        self.sounds['menu_select'] = self._load_sound(os.path.join('sound', 'impactMetal_002.ogg'))
        self.sounds['menu_confirm'] = self._load_sound(os.path.join('sound', 'forceField_001.mp3'))
        self.sounds['music'] = os.path.join(ASSET_DIR, 'sound', 'victory.mp3')

    def _load_fonts(self):
        self.fonts['captain_32'] = self._load_font(os.path.join('font', 'American Captain.ttf'), 32)
        self.fonts['captain_42'] = self._load_font(os.path.join('font', 'American Captain.ttf'), 42)
        self.fonts['captain_80'] = self._load_font(os.path.join('font', 'American Captain.ttf'), 80)

    def get_image(self, key):
        return self.images.get(key)

    def get_sound(self, key):
        return self.sounds.get(key)
        
    def get_font(self, key):
        return self.fonts.get(key)

    def _load_image(self, path):
        return pygame.image.load(os.path.join(ASSET_DIR, path)).convert_alpha()

    def _load_sprite(self, path, new_size=None, scale=None, flip_y=False):
        sprite = self._load_image(path)
        if flip_y:
            sprite = pygame.transform.flip(sprite, False, True)
        if scale:
            new_size = (sprite.get_width() * scale, sprite.get_height() * scale)
        if new_size:
            sprite = pygame.transform.scale(sprite, new_size)
        
        sprite.set_colorkey((0, 0, 0)) 
        return sprite

    def _load_sound(self, path):
        return pygame.mixer.Sound(os.path.join(ASSET_DIR, path))

    def _load_font(self, path, size):
        return pygame.font.Font(os.path.join(ASSET_DIR, path), size)