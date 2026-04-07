"""
main.py - Interactive 2D Billiards Simulation (Pygame)
CSCI 3010U - Simulation and Modeling
Yash Patel - 100785833

Controls
--------
  SPACE      Pause / Resume
  R          Reset simulation
  UP / DOWN  Increase / decrease damping (friction)
  LEFT/RIGHT Decrease / increase restitution (elasticity)
  ESC        Quit
"""

import pygame
import sys
import math
import random
from collections import deque

from ball    import Ball
from physics import resolve_ball_collision, total_kinetic_energy

# ─────────────────────────────────────────────────────────────────────────────
# Window & timing
# ─────────────────────────────────────────────────────────────────────────────
WIN_W, WIN_H = 1130, 710
FPS          = 120
DT           = 1.0 / FPS      # simulation time-step (seconds)

# ─────────────────────────────────────────────────────────────────────────────
# Table layout  (felt playing area boundaries)
# ─────────────────────────────────────────────────────────────────────────────
T_LEFT, T_TOP, T_RIGHT, T_BOTTOM = 72, 92, 782, 618
T_W = T_RIGHT  - T_LEFT
T_H = T_BOTTOM - T_TOP

# Pocket positions and radius
POCKET_R = 22
POCKETS  = [
    (T_LEFT,                    T_TOP),
    ((T_LEFT + T_RIGHT) // 2,   T_TOP    - 10),
    (T_RIGHT,                   T_TOP),
    (T_LEFT,                    T_BOTTOM),
    ((T_LEFT + T_RIGHT) // 2,   T_BOTTOM + 10),
    (T_RIGHT,                   T_BOTTOM),
]

# HUD panel
HUD_X   = 800
HUD_PAD = 16

# ─────────────────────────────────────────────────────────────────────────────
# Colours
# ─────────────────────────────────────────────────────────────────────────────
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
C_RED       = (255,  78,  78)
C_KE_LINE   = (65,  200, 128)
C_KE_FILL   = (15,   68,  44)
C_SEP       = (35,  52,  92)

BALL_COLORS = [
    (218,  52,  52),   # red
    ( 52, 148, 222),   # blue
    (205, 170,  28),   # yellow
    ( 65, 192,  65),   # green
    (192,  65, 192),   # purple
    (222, 130,  40),   # orange
    (178,  58, 138),   # pink
    (242, 242, 238),   # white (cue ball)
]

# ─────────────────────────────────────────────────────────────────────────────
# Ball factory
# ─────────────────────────────────────────────────────────────────────────────
NUM_BALLS = 8
BALL_R    = 18

def spawn_balls():
    """Spawn balls at random non-overlapping positions with random velocities."""
    balls, placed = [], []
    colors = list(BALL_COLORS)
    r   = BALL_R
    pad = r + 6

    for i in range(NUM_BALLS):
        for _ in range(20_000):
            x = random.uniform(T_LEFT + pad, T_RIGHT  - pad)
            y = random.uniform(T_TOP  + pad, T_BOTTOM - pad)
            if all(math.hypot(x - px, y - py) >= r + pr + 4
                   for px, py, pr in placed):
                spd   = random.uniform(60, 260)
                angle = random.uniform(0, 2 * math.pi)
                ball  = Ball(x, y,
                             spd * math.cos(angle),
                             spd * math.sin(angle),
                             radius=r, mass=1.0, color=colors[i])
                balls.append(ball)
                placed.append((x, y, r))
                break

    return balls

# ─────────────────────────────────────────────────────────────────────────────
# Drawing helpers
# ─────────────────────────────────────────────────────────────────────────────

def draw_table(surf):
    """Render rail, felt surface, grid lines, and pockets."""
    # Outer rail
    rail_out = pygame.Rect(40, 60, 782, 600)
    pygame.draw.rect(surf, C_RAIL_D, rail_out, border_radius=14)
    pygame.draw.rect(surf, C_RAIL_L, rail_out, width=4, border_radius=14)

    # Inner rail shadow
    rail_in = pygame.Rect(58, 78, 748, 564)
    pygame.draw.rect(surf, C_RAIL_D, rail_in, border_radius=10)

    # Felt surface
    felt = pygame.Rect(T_LEFT, T_TOP, T_W, T_H)
    pygame.draw.rect(surf, C_FELT, felt)

    # Centre vertical line
    cx = (T_LEFT + T_RIGHT) // 2
    pygame.draw.line(surf, C_FELT_L, (cx, T_TOP + 8), (cx, T_BOTTOM - 8), 1)

    # Centre spot
    cy = (T_TOP + T_BOTTOM) // 2
    pygame.draw.circle(surf, C_FELT_L, (cx, cy), 5, 1)

    # Pockets
    for px, py in POCKETS:
        pygame.draw.circle(surf, C_POCKET, (px, py), POCKET_R)
        pygame.draw.circle(surf, (22, 22, 22), (px, py), POCKET_R, 2)


def draw_ball(surf, ball):
    """Draw a ball with shadow and specular highlight for 3-D look."""
    cx, cy = int(ball.x), int(ball.y)
    r      = int(ball.radius)

    # Drop shadow
    pygame.draw.circle(surf, (5, 8, 14), (cx + 3, cy + 4), r)

    # Main body
    pygame.draw.circle(surf, ball.color, (cx, cy), r)

    # Darker lower half (shading)
    dark = tuple(max(0, c - 80) for c in ball.color)
    shade = pygame.Surface((r * 2, r), pygame.SRCALPHA)
    pygame.draw.ellipse(shade, (*dark, 160), (0, 0, r * 2, r))
    surf.blit(shade, (cx - r, cy))

    # Specular highlight (top-left glint)
    hi_surf = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.circle(hi_surf, (255, 255, 255, 150), (r // 3, r // 3), max(2, r // 4))
    surf.blit(hi_surf, (cx - r + 2, cy - r + 2))

    # Outline
    pygame.draw.circle(surf, (0, 0, 0), (cx, cy), r, 1)


def draw_hud(surf, fonts, balls, elapsed, damping, restitution,
             paused, ke_history, collisions):
    """Render the right-hand information panel."""
    hud_w    = WIN_W - HUD_X - 6
    hud_rect = pygame.Rect(HUD_X, 6, hud_w, WIN_H - 12)
    pygame.draw.rect(surf, C_HUD_BG, hud_rect, border_radius=10)
    pygame.draw.rect(surf, C_HUD_BR, hud_rect, width=2, border_radius=10)

    x0  = HUD_X + HUD_PAD
    col = hud_w - HUD_PAD * 2
    y   = 20

    def txt(text, font, colour):
        nonlocal y
        s = font.render(text, True, colour)
        surf.blit(s, (x0, y))
        y += s.get_height() + 4

    def stat(label, val, val_col=C_TEXT):
        nonlocal y
        sl = fonts['sm'].render(label, True, C_DIM)
        sv = fonts['lb'].render(val,   True, val_col)
        surf.blit(sl, (x0, y))
        surf.blit(sv, (HUD_X + HUD_PAD + col - sv.get_width(), y))
        y += max(sl.get_height(), sv.get_height()) + 5

    def sep():
        nonlocal y
        y += 4
        pygame.draw.line(surf, C_SEP, (x0, y), (HUD_X + HUD_PAD + col, y), 1)
        y += 8

    # Title
    txt("2D BILLIARDS", fonts['title'], C_TITLE)
    txt("Physics Simulation", fonts['sm'], C_DIM)
    sep()

    # Status badge
    col_s = C_RED if paused else C_GREEN
    lbl_s = "PAUSED" if paused else "RUNNING"
    s = fonts['lb'].render(f"● {lbl_s}", True, col_s)
    surf.blit(s, (x0, y)); y += s.get_height() + 4
    sep()

    # Stats
    ke = total_kinetic_energy(balls)
    stat("Total KE",   f"{ke:,.1f}",      C_GREEN)
    stat("Time",       f"{elapsed:.2f} s")
    stat("Balls",      f"{len(balls)}")
    stat("Collisions", f"{collisions}")
    sep()

    # Parameters
    txt("Parameters", fonts['lb'], C_ACCENT)
    y += 2
    stat("Damping  [↑↓]",     f"{damping:.3f}")
    stat("Restitution  [←→]", f"{restitution:.2f}")
    sep()

    # KE mini-graph
    txt("Kinetic Energy Over Time", fonts['sm'], C_DIM)
    y += 2
    gh = 108
    gw = col
    gr = pygame.Rect(x0, y, gw, gh)
    pygame.draw.rect(surf, (8, 12, 22), gr, border_radius=4)
    pygame.draw.rect(surf, C_HUD_BR, gr, width=1, border_radius=4)

    if len(ke_history) >= 2:
        max_ke = max(ke_history) or 1
        pts    = []
        n      = len(ke_history)
        for i, k in enumerate(ke_history):
            px_ = x0 + int(i / max(n - 1, 1) * gw)
            py_ = y  + gh - int(k / max_ke * (gh - 6)) - 3
            pts.append((px_, py_))

        # Fill under curve
        fill = pygame.Surface((gw, gh), pygame.SRCALPHA)
        poly = ([(pts[0][0] - x0, gh)]
                + [(p[0] - x0, p[1] - y) for p in pts]
                + [(pts[-1][0] - x0, gh)])
        pygame.draw.polygon(fill, (*C_KE_FILL, 190), poly)
        surf.blit(fill, (x0, y))

        # Line
        pygame.draw.lines(surf, C_KE_LINE, False, pts, 2)

    y += gh + 10
    sep()

    # Controls
    txt("Controls", fonts['lb'], C_ACCENT)
    y += 2
    controls = [
        ("[SPACE]", "Pause / Resume"),
        ("[R]",     "Reset simulation"),
        ("[↑↓]",    "Damping ± 0.05"),
        ("[←→]",    "Restitution ± 0.1"),
        ("[ESC]",   "Quit"),
    ]
    for key, desc in controls:
        sk = fonts['sm'].render(key,  True, C_ACCENT)
        sd = fonts['sm'].render(desc, True, C_DIM)
        surf.blit(sk, (x0, y))
        surf.blit(sd, (x0 + 82, y))
        y += sk.get_height() + 3


# ─────────────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────────────

MAX_KE_HIST = 340

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("2D Billiards Simulation – CSCI 3010U | Yash Patel")
    clock  = pygame.time.Clock()

    # Load fonts (fall back gracefully)
    def mfont(size, bold=False):
        for name in ("Segoe UI", "Arial", "Helvetica"):
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                return f
            except Exception:
                pass
        return pygame.font.SysFont(None, size, bold=bold)

    fonts = {
        'title': mfont(22, bold=True),
        'lb':    mfont(15, bold=True),
        'sm':    mfont(13),
    }

    # Simulation state
    damping     = 0.20
    restitution = 1.00
    balls       = spawn_balls()
    paused      = False
    elapsed     = 0.0
    collisions  = 0
    ke_history  = deque(maxlen=MAX_KE_HIST)

    # Pre-render static table onto its own surface
    table_surf = pygame.Surface((WIN_W, WIN_H))
    table_surf.fill(C_BG)
    draw_table(table_surf)

    while True:
        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    balls = spawn_balls()
                    elapsed = 0.0
                    collisions = 0
                    ke_history.clear()
                elif event.key == pygame.K_UP:
                    damping = min(5.0, round(damping + 0.05, 3))
                elif event.key == pygame.K_DOWN:
                    damping = max(0.0, round(damping - 0.05, 3))
                elif event.key == pygame.K_RIGHT:
                    restitution = min(1.0, round(restitution + 0.10, 2))
                elif event.key == pygame.K_LEFT:
                    restitution = max(0.0, round(restitution - 0.10, 2))

        # ── Physics update ────────────────────────────────────────────────────
        if not paused:
            elapsed += DT

            # Euler step + wall collisions
            for b in balls:
                b.update(DT, damping)
                b.wall_collision(T_LEFT, T_TOP, T_RIGHT, T_BOTTOM)

            # Ball-ball collision detection (brute-force O(n^2))
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    if resolve_ball_collision(balls[i], balls[j], restitution):
                        collisions += 1

            ke_history.append(total_kinetic_energy(balls))

        # ── Render ────────────────────────────────────────────────────────────
        screen.blit(table_surf, (0, 0))

        for b in balls:
            draw_ball(screen, b)

        draw_hud(screen, fonts, balls, elapsed,
                 damping, restitution, paused, ke_history, collisions)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
