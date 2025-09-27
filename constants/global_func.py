import pygame
from time import time
from .global_var import (
    config, FRAME_RATE, BACKGROUND_COLOR_1, BACKGROUND_COLOR_2,
    TITLE_YELLOW_1, TITLE_YELLOW_2, BACKGROUND_COLOR_MENU_1, GAME_COLOR
)
pygame.init()
screen = pygame.display.set_mode(config.window_size)


def title_text(string, x, y, assets): 
    string = str(string)
    title_font_obj = assets.get_font('captain_80')
    info_1 = title_font_obj.render(string, True, TITLE_YELLOW_1)
    info_2 = title_font_obj.render(string, True, TITLE_YELLOW_2)
    textrect = info_1.get_rect()
    textrect.center = (x, y)
    textrect_2 = info_2.get_rect()
    textrect_2.center = (x+4, y+4)
    screen.blit(info_2, textrect_2)
    screen.blit(info_1, textrect)

def text(string, x, y, assets, color=(200, 200, 200), original_font=True):
    string = str(string)
    if original_font:
        font_obj = assets.get_font('captain_42')
    else:
        font_obj = assets.get_font('captain_32')
    
    info = font_obj.render(string, True, color)
    textrect = info.get_rect()
    textrect.center = (x, y)
    screen.blit(info, textrect)


def bool2Switch(bool):
    if bool: return 'ON'
    else:    return 'OFF'


def delta_time(last_time):
    dt = time() - last_time
    dt *= FRAME_RATE
    last_time = time()
    return dt, last_time


def find_key_by_value(dict, target_value):
    for key, value in dict.items():
        if value == target_value:
            return key
    return None


def vertical(surf, is_square=True, start_color=BACKGROUND_COLOR_1, end_color=BACKGROUND_COLOR_2):
    if not is_square:
        size = config.window_size
        axis_x, axis_y = 0, 0
    else:
        size = (400, 400)
        center = (config.window_size[0] / 2, config.window_size[1] / 2)
        x, y = center
        axis_x = x - size[0] / 2
        axis_y = y - size[1] / 2

    height = size[1]
    big_surf = pygame.Surface((1, height)).convert_alpha()
    dd = 1.0 / height
    sr, sg, sb, sa = start_color
    er, eg, eb, ea = end_color
    rm = (er - sr) * dd
    gm = (eg - sg) * dd
    bm = (eb - sb) * dd
    am = (ea - sa) * dd
    for y in range(height):
        big_surf.set_at((0, y),
                       (int(sr + rm * y),
                        int(sg + gm * y),
                        int(sb + bm * y),
                        int(sa + am * y)))
    v = pygame.transform.scale(big_surf, size)
    surf.blit(v, (axis_x, axis_y))

def MenuMaker(options, title, selected, surf, assets):
    vertical(surf)
    for i in range(200):
        pygame.draw.line(surf, BACKGROUND_COLOR_MENU_1,
                         (config.window_size[0] / 2 - 100 + i, config.window_size[1] / 2 - 179),      # Title background
                         (config.window_size[0] / 2 - 100 + i, config.window_size[1] / 2 - 230), 4)   # Title background
    text(title, config.window_size[0] / 2, config.window_size[1] / 2 - 200, assets)

    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 180),      # Title Bottom outline
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 180), 4)   # Title Bottom outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 179),      # Title Top-left outline
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 230), 4)   # Title Top-left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 179),      # Title Top-right outline
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 230), 4)   # Title Top-right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 230),      # Title Top outline
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 230), 4)   # Title Top outline

    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 + 100, config.window_size[1] / 2 - 200),      # Top-right outline
                     (config.window_size[0] / 2 + 200, config.window_size[1] / 2 - 200), 4)   # Top-right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 100, config.window_size[1] / 2 - 200),      # Top-left outline
                     (config.window_size[0] / 2 - 200, config.window_size[1] / 2 - 200), 4)   # Top-left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 + 200, config.window_size[1] / 2 - 200),      # Left outline
                     (config.window_size[0] / 2 + 200, config.window_size[1] / 2 + 200), 4)   # Left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 200, config.window_size[1] / 2 - 200),      # Right outline
                     (config.window_size[0] / 2 - 200, config.window_size[1] / 2 + 200), 4)   # Right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (config.window_size[0] / 2 - 200, config.window_size[1] / 2 + 200),      # Bottom outline
                     (config.window_size[0] / 2 + 200, config.window_size[1] / 2 + 200), 4)   # Bottom outline

    if len(options) >= 4: y_gap = 90
    elif len(options) >= 6: y_gap = 120
    else: y_gap = 50

    for option in options:
        if selected == options.index(option):
            text(option, config.window_size[0] / 2, (config.window_size[1] / 2 - y_gap) + 50 * options.index(option), assets, GAME_COLOR)
            if len(option) < 10:
                text('|', config.window_size[0] / 2 + 100, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), assets, GAME_COLOR)
                text('|', config.window_size[0] / 2 - 100, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), assets, GAME_COLOR)
            elif len(option) < 20:
                text('|', config.window_size[0] / 2 + 150, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), assets, GAME_COLOR)
                text('|', config.window_size[0] / 2 - 150, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), assets, GAME_COLOR)
            else:
                text('|', config.window_size[0] / 2 + 180, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), assets, GAME_COLOR)
                text('|', config.window_size[0] / 2 - 180, (config.window_size[1] / 2 - y_gap - 5) + 50 * options.index(option), assets, GAME_COLOR)
        else:
            text(option, config.window_size[0] / 2, (config.window_size[1] / 2 - y_gap) + 50 * options.index(option), assets)


