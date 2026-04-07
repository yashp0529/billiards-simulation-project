"""
screenshot.py - Captures a single frame of the simulation and saves it as PNG.
Run with: python screenshot.py
"""

import pygame
import sys
import math
import random
from ball    import Ball
from physics import resolve_ball_collision, total_kinetic_energy

# Same constants as main.py
WIN_W, WIN_H = 1130, 710
FPS          = 120
DT           = 1.0 / FPS
T_LEFT, T_TOP, T_RIGHT, T_BOTTOM = 72, 92, 782, 618
T_W = T_RIGHT - T_LEFT
T_H = T_BOTTOM - T_TOP
NUM_BALLS = 8
BALL_R    = 18

POCKET_R = 22
POCKETS  = [
    (T_LEFT,                    T_TOP),
    ((T_LEFT + T_RIGHT) // 2,   T_TOP    - 10),
    (T_RIGHT,                   T_TOP),
    (T_LEFT,                    T_BOTTOM),
    ((T_LEFT + T_RIGHT) // 2,   T_BOTTOM + 10),
    (T_RIGHT,                   T_BOTTOM),
]

C_BG        = (10,  15,  26)
C_RAIL_D    = (72,  44,  12)
C_RAIL_L    = (108, 66,  22)
C_FELT      = (25,  92,  44)
C_FELT_L    = (30,  102, 50)
C_POCKET    = (5,    5,   5)
C_HUD_BG    = (16,  22,  38)
C_HUD_BR    = (40,  62, 112)
C_TITLE     = (100, 158, 255)
C_TEXT      = (210, 222, 248)
C_DIM       = (108, 128, 170)
C_ACCENT    = (68,  148, 255)
C_GREEN     = (55,  215,  95)
C_KE_LINE   = (65,  200, 128)
C_KE_FILL   = (15,   68,  44)
C_SEP       = (35,  52,  92)
HUD_X   = 800
HUD_PAD = 16

BALL_COLORS = [
    (218,  52,  52),
    ( 52, 148, 222),
    (205, 170,  28),
    ( 65, 192,  65),
    (192,  65, 192),
    (222, 130,  40),
    (178,  58, 138),
    (242, 242, 238),
]

def spawn_balls(seed=99):
    rng = random.Random(seed)
    balls, placed = [], []
    r = BALL_R; pad = r + 6
    colors = list(BALL_COLORS)
    for i in range(NUM_BALLS):
        for _ in range(20000):
            x = rng.uniform(T_LEFT + pad, T_RIGHT - pad)
            y = rng.uniform(T_TOP  + pad, T_BOTTOM - pad)
            if all(math.hypot(x-px, y-py) >= r+pr+4 for px,py,pr in placed):
                spd = rng.uniform(60, 260)
                angle = rng.uniform(0, 2*math.pi)
                balls.append(Ball(x, y, spd*math.cos(angle), spd*math.sin(angle),
                                  radius=r, mass=1.0, color=colors[i]))
                placed.append((x, y, r))
                break
    return balls

def draw_table(surf):
    rail_out = pygame.Rect(40, 60, 782, 600)
    pygame.draw.rect(surf, C_RAIL_D, rail_out, border_radius=14)
    pygame.draw.rect(surf, C_RAIL_L, rail_out, width=4, border_radius=14)
    rail_in = pygame.Rect(58, 78, 748, 564)
    pygame.draw.rect(surf, C_RAIL_D, rail_in, border_radius=10)
    felt = pygame.Rect(T_LEFT, T_TOP, T_W, T_H)
    pygame.draw.rect(surf, C_FELT, felt)
    cx = (T_LEFT + T_RIGHT) // 2
    pygame.draw.line(surf, C_FELT_L, (cx, T_TOP+8), (cx, T_BOTTOM-8), 1)
    cy = (T_TOP + T_BOTTOM) // 2
    pygame.draw.circle(surf, C_FELT_L, (cx, cy), 5, 1)
    for px, py in POCKETS:
        pygame.draw.circle(surf, C_POCKET, (px, py), POCKET_R)
        pygame.draw.circle(surf, (22, 22, 22), (px, py), POCKET_R, 2)

def draw_ball(surf, ball):
    cx, cy = int(ball.x), int(ball.y)
    r = int(ball.radius)
    pygame.draw.circle(surf, (5, 8, 14), (cx+3, cy+4), r)
    pygame.draw.circle(surf, ball.color, (cx, cy), r)
    dark = tuple(max(0, c-80) for c in ball.color)
    shade = pygame.Surface((r*2, r), pygame.SRCALPHA)
    pygame.draw.ellipse(shade, (*dark, 160), (0, 0, r*2, r))
    surf.blit(shade, (cx-r, cy))
    hi_surf = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.circle(hi_surf, (255, 255, 255, 150), (r//3, r//3), max(2, r//4))
    surf.blit(hi_surf, (cx-r+2, cy-r+2))
    pygame.draw.circle(surf, (0, 0, 0), (cx, cy), r, 1)

def draw_hud_simple(surf, balls, damping, restitution, collisions, ke_history):
    from collections import deque
    hud_w = WIN_W - HUD_X - 6
    hud_rect = pygame.Rect(HUD_X, 6, hud_w, WIN_H - 12)
    pygame.draw.rect(surf, C_HUD_BG, hud_rect, border_radius=10)
    pygame.draw.rect(surf, C_HUD_BR, hud_rect, width=2, border_radius=10)

    def mfont(size, bold=False):
        return pygame.font.SysFont("Segoe UI", size, bold=bold)

    x0 = HUD_X + HUD_PAD
    col = hud_w - HUD_PAD * 2
    y = 20

    title = mfont(22, bold=True).render("2D BILLIARDS", True, C_TITLE)
    surf.blit(title, (x0, y)); y += title.get_height() + 4
    sub = mfont(13).render("Physics Simulation", True, C_DIM)
    surf.blit(sub, (x0, y)); y += sub.get_height() + 8
    pygame.draw.line(surf, C_SEP, (x0, y), (HUD_X + HUD_PAD + col, y), 1); y += 10

    status = mfont(15, bold=True).render("● RUNNING", True, C_GREEN)
    surf.blit(status, (x0, y)); y += status.get_height() + 6
    pygame.draw.line(surf, C_SEP, (x0, y), (HUD_X + HUD_PAD + col, y), 1); y += 10

    ke = total_kinetic_energy(balls)
    for label, val, col_v in [
        ("Total KE",   f"{ke:,.1f}",     C_GREEN),
        ("Balls",      f"{len(balls)}",  C_TEXT),
        ("Collisions", f"{collisions}",  C_TEXT),
    ]:
        sl = mfont(13).render(label, True, C_DIM)
        sv = mfont(15, bold=True).render(val, True, col_v)
        surf.blit(sl, (x0, y))
        surf.blit(sv, (HUD_X + HUD_PAD + col - sv.get_width(), y))
        y += max(sl.get_height(), sv.get_height()) + 5

    pygame.draw.line(surf, C_SEP, (x0, y), (HUD_X + HUD_PAD + col, y), 1); y += 10
    pline = mfont(15, bold=True).render("Parameters", True, C_ACCENT)
    surf.blit(pline, (x0, y)); y += pline.get_height() + 4
    for label, val in [("Damping", f"{damping:.2f}"), ("Restitution", f"{restitution:.2f}")]:
        sl = mfont(13).render(label, True, C_DIM)
        sv = mfont(15, bold=True).render(val, True, C_TEXT)
        surf.blit(sl, (x0, y))
        surf.blit(sv, (HUD_X + HUD_PAD + col - sv.get_width(), y))
        y += max(sl.get_height(), sv.get_height()) + 5

    pygame.draw.line(surf, C_SEP, (x0, y), (HUD_X + HUD_PAD + col, y), 1); y += 10
    glabel = mfont(13).render("Kinetic Energy Over Time", True, C_DIM)
    surf.blit(glabel, (x0, y)); y += glabel.get_height() + 4
    gh, gw = 108, col
    gr = pygame.Rect(x0, y, gw, gh)
    pygame.draw.rect(surf, (8, 12, 22), gr, border_radius=4)
    pygame.draw.rect(surf, C_HUD_BR, gr, width=1, border_radius=4)
    if len(ke_history) >= 2:
        max_ke = max(ke_history) or 1
        pts = []
        n = len(ke_history)
        for i, k in enumerate(ke_history):
            px_ = x0 + int(i / max(n-1, 1) * gw)
            py_ = y  + gh - int(k / max_ke * (gh-6)) - 3
            pts.append((px_, py_))
        fill = pygame.Surface((gw, gh), pygame.SRCALPHA)
        poly = ([(pts[0][0]-x0, gh)] + [(p[0]-x0, p[1]-y) for p in pts] + [(pts[-1][0]-x0, gh)])
        pygame.draw.polygon(fill, (*C_KE_FILL, 190), poly)
        surf.blit(fill, (x0, y))
        pygame.draw.lines(surf, C_KE_LINE, False, pts, 2)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Screenshot Capture")
    clock = pygame.time.Clock()

    balls = spawn_balls(seed=42)
    ke_history = []
    collisions = 0
    damping = 0.2
    restitution = 1.0

    # Run simulation for 3 seconds to get balls moving, then screenshot
    steps = int(3.0 / DT)
    for step in range(steps):
        for b in balls:
            b.update(DT, damping)
            b.wall_collision(T_LEFT, T_TOP, T_RIGHT, T_BOTTOM)
        for i in range(len(balls)):
            for j in range(i+1, len(balls)):
                if resolve_ball_collision(balls[i], balls[j], restitution):
                    collisions += 1
        ke_history.append(total_kinetic_energy(balls))

    # Draw one frame
    screen.fill(C_BG)
    draw_table(screen)
    for b in balls:
        draw_ball(screen, b)
    draw_hud_simple(screen, balls, damping, restitution, collisions, ke_history[-200:])

    pygame.display.flip()
    pygame.image.save(screen, "simulation_screenshot.png")
    print("Screenshot saved: simulation_screenshot.png")
    pygame.quit()

if __name__ == "__main__":
    main()
