import pygame
from pygame.locals import *
from game_engine import g_engine
from constants.global_var import (
    config,
    BACKGROUND_COLOR_1,
    BACKGROUND_COLOR_2,
    TITLE_YELLOW_1,
    TITLE_YELLOW_2,
    BACKGROUND_COLOR_MENU_1,
    GAME_COLOR,
)


def title_text(surf, string, x, y):
    string = str(string)
    title_font_obj = g_engine.assets.get_font("captain_80")
    info_1 = title_font_obj.render(string, True, TITLE_YELLOW_1)
    info_2 = title_font_obj.render(string, True, TITLE_YELLOW_2)
    textrect = info_1.get_rect()
    textrect.center = (x, y)
    textrect_2 = info_2.get_rect()
    textrect_2.center = (x + 4, y + 4)
    surf.blit(info_2, textrect_2)
    surf.blit(info_1, textrect)


def draw_text(surf, string, x, y, color=(200, 200, 200), use_smaller_font=False):
    min_width_for_large_font = 1920
    font_large_name = "captain_42"
    font_small_name = "captain_32"
    should_use_smaller = (
        use_smaller_font or config.INTERNAL_RESOLUTION[0] < min_width_for_large_font
    )

    font_name = font_small_name if should_use_smaller else font_large_name
    font_obj = g_engine.assets.get_font(font_name)

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
    return "ON" if is_on else "OFF"


def vertical(
    surf, is_square=True, start_color=BACKGROUND_COLOR_1, end_color=BACKGROUND_COLOR_2
):
    if not is_square:
        size = config.INTERNAL_RESOLUTION
        axis_x, axis_y = 0, 0
    else:
        size = (
            config.INTERNAL_RESOLUTION[0] * 0.2,
            config.INTERNAL_RESOLUTION[0] * 0.2,
        )
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
        big_surf.set_at(
            (0, y),
            (int(sr + rm * y), int(sg + gm * y), int(sb + bm * y), int(sa + am * y)),
        )
    v = pygame.transform.scale(big_surf, size)
    surf.blit(v, (axis_x, axis_y))


def menu_maker(options, title, selected, surf, is_settings):
    internal_w, internal_h = config.INTERNAL_RESOLUTION
    half_w = internal_w / 2
    half_h = internal_h / 2

    pct_5_w = internal_w * 0.05
    pct_10_w = internal_w * 0.1
    pct_15_w = internal_w * 0.15
    pct_5_h = internal_h * 0.05

    if is_settings:
        lowest_y = pct_15_w
    else:
        lowest_y = pct_10_w

    vertical(surf)

    # Title background
    title_bg_rect = (half_w - pct_5_w, half_h - pct_5_h * 4.15, pct_10_w + 5, pct_5_h)
    pygame.draw.rect(surf, BACKGROUND_COLOR_MENU_1, title_bg_rect)

    draw_text(surf, title, half_w, half_h - pct_10_w * 1.0)

    outline_color = (200, 200, 200)
    outline_thickness = 4

    # Title outline
    title_outline_rect = (
        half_w - pct_5_w,
        half_h - pct_5_w * 2.3,
        pct_5_w * 2,
        pct_5_w * 0.5,
    )
    pygame.draw.rect(surf, outline_color, title_outline_rect, outline_thickness)

    menu_lines = [
        (
            (half_w + pct_5_w, half_h - pct_10_w),
            (half_w + pct_10_w, half_h - pct_10_w),
        ),  # Top-right outline
        (
            (half_w - pct_5_w, half_h - pct_10_w),
            (half_w - pct_10_w, half_h - pct_10_w),
        ),  # Top-left outline
        (
            (half_w + pct_10_w, half_h - pct_10_w),
            (half_w + pct_10_w, half_h + lowest_y),
        ),  # Right outline
        (
            (half_w - pct_10_w, half_h - pct_10_w),
            (half_w - pct_10_w, half_h + lowest_y),
        ),  # Left outline
        (
            (half_w - pct_10_w, half_h + lowest_y),
            (half_w + pct_10_w, half_h + lowest_y),
        ),  # Bottom outline
    ]

    for start_pos, end_pos in menu_lines:
        pygame.draw.line(surf, outline_color, start_pos, end_pos, outline_thickness)

    options_qty = len(options)
    if options_qty >= 6:
        y_gap = pct_5_w * 1.1
    elif options_qty >= 4:
        y_gap = pct_5_w * 0.9
    else:
        y_gap = pct_5_w / 2

    for i, option in enumerate(options):
        item_y = (half_h - y_gap) + (pct_5_w / 2) * i

        if i == selected:
            draw_text(surf, option, half_w, item_y, GAME_COLOR)

            if len(option) < 10:
                x_offset = pct_5_w
            elif len(option) < 20:
                x_offset = pct_5_w * 1.5
            else:
                x_offset = pct_5_w * 1.9

            cursor_y = item_y - 5
            draw_text(surf, "|", half_w + x_offset, cursor_y, GAME_COLOR)
            draw_text(surf, "|", half_w - x_offset, cursor_y, GAME_COLOR)
        else:
            draw_text(surf, option, half_w, item_y)


def menu_select_next(menu, buttons):
    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
    menu.selected = (menu.selected + 1) % len(buttons)


def menu_select_prev(menu, buttons):
    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
    menu.selected = (menu.selected - 1) % len(buttons)


def select_prev_res(options):
    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
    if options.selected == 0:
        selected_res = config.RESOLUTIONS.index(options.config_res)
        selected_res = min(len(config.RESOLUTIONS) - 1, selected_res + 1)
        options.config_res = config.RESOLUTIONS[selected_res]
    config.window_size = options.config_res


def select_next_res(options):
    pygame.mixer.Sound.play(g_engine.assets.get_sound("menu_select"))
    if options.selected == 0:
        selected_res = config.RESOLUTIONS.index(options.config_res)
        selected_res = max(0, selected_res - 1)
        options.config_res = config.RESOLUTIONS[selected_res]
    config.window_size = options.config_res


def handle_analog_stick(menu, event):
    deadzone = 0.5

    if event.axis == 1:
        if event.value > deadzone and not getattr(menu, "axis_down", False):
            menu.axis_down = True
            pygame.event.post(pygame.event.Event(JOYHATMOTION, hat=0, value=(0, -1)))
        elif event.value < -deadzone and not getattr(menu, "axis_up", False):
            menu.axis_up = True
            pygame.event.post(pygame.event.Event(JOYHATMOTION, hat=0, value=(0, 1)))
        elif abs(event.value) < deadzone:
            menu.axis_down = False
            menu.axis_up = False

    if event.axis == 0:
        if event.value > deadzone and not getattr(menu, "axis_right", False):
            menu.axis_right = True
            pygame.event.post(pygame.event.Event(JOYHATMOTION, hat=0, value=(1, 0)))
        elif event.value < -deadzone and not getattr(menu, "axis_left", False):
            menu.axis_left = True
            pygame.event.post(pygame.event.Event(JOYHATMOTION, hat=0, value=(-1, 0)))
        elif abs(event.value) < deadzone:
            menu.axis_right = False
            menu.axis_left = False
