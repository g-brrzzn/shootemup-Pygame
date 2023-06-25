from constants.global_var import *
from constants.global_imports import *

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
font = pygame.font.Font('assets/American Captain.ttf', 42)


def text(string, x, y, color=(255, 255, 255)):
    string = str(string)
    info = font.render(string, True, color)
    textrect = info.get_rect()
    textrect.center = (x, y)
    screen.blit(info, textrect)


def bool2Switch(bool):
    if bool: return 'ON'
    else: return 'OFF'


def delta_time(last_time):
    dt = time() - last_time
    dt *= FRAME_RATE
    last_time = time()
    return dt, last_time


def vertical(surf, is_square=True, start_color=(80, 10, 60, 200), end_color=(30, 5, 20, 200)):
    if not is_square:
        size = WINDOW_SIZE
        axis_x, axis_y = 0, 0
    else:
        size = (400, 400)
        center = (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2)
        x, y = center
        axis_x = x - size[0] / 2
        axis_y = y - size[0] / 2

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
                        int(sa + am * y))
                       )
    v = pygame.transform.scale(big_surf, size)
    surf.blit(v, (axis_x, axis_y))


def MenuMaker(options, title, selected, surf):
    vertical(surf)
    for i in range(200):
        pygame.draw.line(surf, (80, 10, 60),
                         (WINDOW_SIZE[0] / 2 - 100 + i, WINDOW_SIZE[1] / 2 - 179),      # Title background
                         (WINDOW_SIZE[0] / 2 - 100 + i, WINDOW_SIZE[1] / 2 - 230), 4)   # Title background
    text(title, WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2 - 200)

    pygame.draw.line(surf, (200, 200, 200),
                     (WINDOW_SIZE[0] / 2 - 100, WINDOW_SIZE[1] / 2 - 180),      # Title Bottom outline
                     (WINDOW_SIZE[0] / 2 + 100, WINDOW_SIZE[1] / 2 - 180), 4)   # Title Bottom outline
    pygame.draw.line(surf, (200, 200, 200),
                     (WINDOW_SIZE[0] / 2 + 100, WINDOW_SIZE[1] / 2 - 179),      # Title Top-left outline
                     (WINDOW_SIZE[0] / 2 + 100, WINDOW_SIZE[1] / 2 - 230), 4)   # Title Top-left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (WINDOW_SIZE[0] / 2 - 100, WINDOW_SIZE[1] / 2 - 179),      # Title Top-right outline
                     (WINDOW_SIZE[0] / 2 - 100, WINDOW_SIZE[1] / 2 - 230), 4)   # Title Top-right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (WINDOW_SIZE[0] / 2 - 100, WINDOW_SIZE[1] / 2 - 230),      # Title Top outline
                     (WINDOW_SIZE[0] / 2 + 100, WINDOW_SIZE[1] / 2 - 230), 4)   # Title Top outline

    pygame.draw.line(surf, (200, 200, 200),
                     (WINDOW_SIZE[0] / 2 + 100, WINDOW_SIZE[1] / 2 - 200),      # Top-right outline
                     (WINDOW_SIZE[0] / 2 + 200, WINDOW_SIZE[1] / 2 - 200), 4)   # Top-right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (WINDOW_SIZE[0] / 2 - 100, WINDOW_SIZE[1] / 2 - 200),      # Top-left outline
                     (WINDOW_SIZE[0] / 2 - 200, WINDOW_SIZE[1] / 2 - 200), 4)   # Top-left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (WINDOW_SIZE[0] / 2 + 200, WINDOW_SIZE[1] / 2 - 200),      # Left outline
                     (WINDOW_SIZE[0] / 2 + 200, WINDOW_SIZE[1] / 2 + 200), 4)   # Left outline
    pygame.draw.line(surf, (200, 200, 200),
                     (WINDOW_SIZE[0] / 2 - 200, WINDOW_SIZE[1] / 2 - 200),      # Right outline
                     (WINDOW_SIZE[0] / 2 - 200, WINDOW_SIZE[1] / 2 + 200), 4)   # Right outline
    pygame.draw.line(surf, (200, 200, 200),
                     (WINDOW_SIZE[0] / 2 - 200, WINDOW_SIZE[1] / 2 + 200),      # Bottom outline
                     (WINDOW_SIZE[0] / 2 + 200, WINDOW_SIZE[1] / 2 + 200), 4)   # Bottom outline

    if len(options) >= 4: y_gap = 90
    elif len(options) >= 6: y_gap = 120
    else: y_gap = 50

    for option in options:
        if selected == options.index(option):
            text(option, WINDOW_SIZE[0] / 2, (WINDOW_SIZE[1] / 2 - y_gap) + 50 * options.index(option), (100, 40, 80))
            if len(option) < 10:
                text('|', WINDOW_SIZE[0] / 2 + 100, (WINDOW_SIZE[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
                text('|', WINDOW_SIZE[0] / 2 - 100, (WINDOW_SIZE[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
            elif len(option) < 20:
                text('|', WINDOW_SIZE[0] / 2 + 150, (WINDOW_SIZE[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
                text('|', WINDOW_SIZE[0] / 2 - 150, (WINDOW_SIZE[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
            else:
                text('|', WINDOW_SIZE[0] / 2 + 180, (WINDOW_SIZE[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
                text('|', WINDOW_SIZE[0] / 2 - 180, (WINDOW_SIZE[1] / 2 - y_gap - 5) + 50 * options.index(option), (100, 40, 80))
        else:
            text(option, WINDOW_SIZE[0] / 2, (WINDOW_SIZE[1] / 2 - y_gap) + 50 * options.index(option))

