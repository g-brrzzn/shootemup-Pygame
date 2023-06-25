import pygame

FHD = (1920, 1080)
HD = (1280, 720)
XGA = (1024, 768)
QHD = (960, 540)
SVGA = (800, 600)
ALL_RES = [SVGA,  QHD, XGA, HD, FHD]

WINDOW_SIZE = HD
SET_FULLSCREEN = False
SHOW_FPS = False

FRAME_RATE = 75
SPRITE_SIZE = 16
SCALED_SPRITE_SIZE = SPRITE_SIZE * 4

CONTROLS = {
    'UP': [pygame.K_w, pygame.K_UP],
    'DOWN': [pygame.K_s, pygame.K_DOWN],
    'RIGHT': [pygame.K_d, pygame.K_LEFT],
    'LEFT': [pygame.K_a, pygame.K_RIGHT],
    'FIRE': [pygame.K_SPACE],
    'START': [pygame.K_RETURN],
    'ESC': [pygame.K_ESCAPE]
}
