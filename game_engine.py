class GameEngine:
    def __init__(self):
        self.player = None
        self.all_sprites = None
        self.all_enemies = None
        self.player_bullets = None
        self.enemy_bullets = None
        self.powerups = None
        self.assets = None
        self.level = 1
        self.score = 0
        self.high_score = 0
        self.screen_shake = 0
        self.hit_stop_frames = 0
        self.spark_system = None
        self.explosion_system = None
        self.glow_cache = {}
        self.joystick = None
        self.shader_manager = None
        self.platform = None
        self.fps_limit = None
        self.has_seen_controls = False

g_engine = GameEngine()