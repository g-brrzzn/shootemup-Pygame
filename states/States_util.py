import pygame
from constants.global_var import (
    config, BACKGROUND_COLOR_1, BACKGROUND_COLOR_2,
    TITLE_YELLOW_1, TITLE_YELLOW_2, BACKGROUND_COLOR_MENU_1, GAME_COLOR
)

def title_text(surf, string, x, y, assets): 
    string = str(string)
    title_font_obj = assets.get_font('captain_80')
    info_1 = title_font_obj.render(string, True, TITLE_YELLOW_1)
    info_2 = title_font_obj.render(string, True, TITLE_YELLOW_2)
    textrect = info_1.get_rect()
    textrect.center = (x, y)
    textrect_2 = info_2.get_rect()
    textrect_2.center = (x+4, y+4)
    surf.blit(info_2, textrect_2)
    surf.blit(info_1, textrect)

def draw_text(surf, string, x, y, assets, color=(200, 200, 200), use_smaller_font=False):
    min_width_for_large_font = 1920
    font_large_name = 'captain_42'
    font_small_name = 'captain_32'
    should_use_smaller = use_smaller_font or config.INTERNAL_RESOLUTION[0] < min_width_for_large_font

    font_name = font_small_name if should_use_smaller else font_large_name
    font_obj = assets.get_font(font_name)

    text_surface = font_obj.render(str(string), True, color)
    textrect = text_surface.get_rect()
    textrect.center = (x, y)
    surf.blit(text_surface, textrect)
    
    
def find_key_by_value(dict, target_value):
    for key, value in dict.items():
        if value == target_value:
            return key
    return None


def get_on_off_status(is_on):
    return 'ON' if is_on else 'OFF'


def vertical(surf, is_square=True, start_color=BACKGROUND_COLOR_1, end_color=BACKGROUND_COLOR_2):
    if not is_square:
        size = config.INTERNAL_RESOLUTION
        axis_x, axis_y = 0, 0
    else:
        size = (config.INTERNAL_RESOLUTION[0] * 0.2, config.INTERNAL_RESOLUTION[0] * 0.2)
        center = (config.INTERNAL_RESOLUTION[0] / 2, config.INTERNAL_RESOLUTION[1] / 2)
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
    for y in range(int(height)):
        big_surf.set_at((0, y),
                       (int(sr + rm * y),
                        int(sg + gm * y),
                        int(sb + bm * y),
                        int(sa + am * y)))
    v = pygame.transform.scale(big_surf, size)
    surf.blit(v, (axis_x, axis_y))

def menu_maker(options, title, selected, surf, assets):
    half_internal_res_width = config.INTERNAL_RESOLUTION[0] / 2
    half_internal_res_height = config.INTERNAL_RESOLUTION[1] / 2
    five_percent_internal_res = config.INTERNAL_RESOLUTION[0]*0.05
    ten_percent_internal_res = config.INTERNAL_RESOLUTION[0]*0.1
    five_percent_internal_res_height = config.INTERNAL_RESOLUTION[1]*0.05
    
    vertical(surf)
    for i in range(200):
        # Title background
        title_background_rect_x = half_internal_res_width - five_percent_internal_res
        title_background_rect_y = half_internal_res_height - five_percent_internal_res_height * 4.15
        title_background_rect_width = ten_percent_internal_res + 5
        title_background_rect_height = five_percent_internal_res_height
        pygame.draw.rect(surf, BACKGROUND_COLOR_MENU_1, (title_background_rect_x, title_background_rect_y, title_background_rect_width, title_background_rect_height))
           
    draw_text(surf, title, half_internal_res_width, half_internal_res_height - ten_percent_internal_res*1.0, assets)

    pygame.draw.line(surf, (200, 200, 200),
                     (half_internal_res_width - five_percent_internal_res, half_internal_res_height - five_percent_internal_res*1.8),      # Title Bottom outline
                     (half_internal_res_width + five_percent_internal_res, half_internal_res_height - five_percent_internal_res*1.8), 4)   # Title Bottom outline
    pygame.draw.line(surf, (200, 200, 200),
                     (half_internal_res_width + five_percent_internal_res, half_internal_res_height - five_percent_internal_res*1.8),      # Title Top-left outline
                     (half_internal_res_width + five_percent_internal_res, half_internal_res_height - five_percent_internal_res*2.3), 4)   # Title Top-left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (half_internal_res_width - five_percent_internal_res, half_internal_res_height - five_percent_internal_res*1.8),      # Title Top-right outline
                     (half_internal_res_width - five_percent_internal_res, half_internal_res_height - five_percent_internal_res*2.3), 4)   # Title Top-right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (half_internal_res_width - five_percent_internal_res, half_internal_res_height - five_percent_internal_res*2.3),      # Title Top outline
                     (half_internal_res_width + five_percent_internal_res, half_internal_res_height - five_percent_internal_res*2.3), 4)   # Title Top outline

    pygame.draw.line(surf, (200, 200, 200),
                     (half_internal_res_width + five_percent_internal_res, half_internal_res_height - ten_percent_internal_res),      # Top-right outline
                     (half_internal_res_width + ten_percent_internal_res, half_internal_res_height - ten_percent_internal_res), 4)   # Top-right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (half_internal_res_width - five_percent_internal_res, half_internal_res_height - ten_percent_internal_res),      # Top-left outline
                     (half_internal_res_width - ten_percent_internal_res, half_internal_res_height - ten_percent_internal_res), 4)   # Top-left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (half_internal_res_width + ten_percent_internal_res, half_internal_res_height - ten_percent_internal_res),      # Left outline
                     (half_internal_res_width + ten_percent_internal_res, half_internal_res_height + ten_percent_internal_res), 4)   # Left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (half_internal_res_width - ten_percent_internal_res, half_internal_res_height - ten_percent_internal_res),      # Right outline
                     (half_internal_res_width - ten_percent_internal_res, half_internal_res_height + ten_percent_internal_res), 4)   # Right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (half_internal_res_width - ten_percent_internal_res, half_internal_res_height + ten_percent_internal_res),      # Bottom outline
                     (half_internal_res_width + ten_percent_internal_res, half_internal_res_height + ten_percent_internal_res), 4)   # Bottom outline

    options_items_quantity = len(options)
    if options_items_quantity >= 4: y_gap = five_percent_internal_res*0.9
    elif options_items_quantity >= 6: y_gap = five_percent_internal_res*1.1
    else: y_gap = five_percent_internal_res/2

    for option in options:
        if selected == options.index(option):
            draw_text(surf, option, half_internal_res_width, (half_internal_res_height - y_gap) + five_percent_internal_res/2 * options.index(option), assets, GAME_COLOR)
            if len(option) < 10:
                draw_text(surf, '|', half_internal_res_width + five_percent_internal_res, (half_internal_res_height - y_gap - 5) + five_percent_internal_res/2 * options.index(option), assets, GAME_COLOR)
                draw_text(surf, '|', half_internal_res_width - five_percent_internal_res, (half_internal_res_height - y_gap - 5) + five_percent_internal_res/2 * options.index(option), assets, GAME_COLOR)
            elif len(option) < 20:
                draw_text(surf, '|', half_internal_res_width + five_percent_internal_res*1.5, (half_internal_res_height - y_gap - 5) + five_percent_internal_res/2 * options.index(option), assets, GAME_COLOR)
                draw_text(surf, '|', half_internal_res_width - five_percent_internal_res*1.5, (half_internal_res_height - y_gap - 5) + five_percent_internal_res/2 * options.index(option), assets, GAME_COLOR)
            else:
                draw_text(surf, '|', half_internal_res_width + five_percent_internal_res*1.9, (half_internal_res_height - y_gap - 5) + five_percent_internal_res/2 * options.index(option), assets, GAME_COLOR)
                draw_text(surf, '|', half_internal_res_width - five_percent_internal_res*1.9, (half_internal_res_height - y_gap - 5) + five_percent_internal_res/2 * options.index(option), assets, GAME_COLOR)
        else:
            draw_text(surf, option, half_internal_res_width, (half_internal_res_height - y_gap) + five_percent_internal_res/2 * options.index(option), assets)


