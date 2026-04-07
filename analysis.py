"""
analysis.py - Experiment runner and graph generator
CSCI 3010U - Simulation and Modeling
Yash Patel - 100785833

Runs three headless experiments (no Pygame window) and saves PNG plots:
  1. KE vs time for different restitution values (elastic vs inelastic)
  2. KE vs time for different damping coefficients
  3. Total momentum magnitude over time (conservation check)

Run with:  python analysis.py
"""

import math
import random
import copy
import matplotlib
matplotlib.use("Agg")          # non-interactive backend - no display needed
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from ball    import Ball
from physics import resolve_ball_collision, total_kinetic_energy, total_momentum_vector

# ─────────────────────────────────────────────────────────────────────────────
# Simulation parameters
# ─────────────────────────────────────────────────────────────────────────────
DT         = 1.0 / 120.0    # same time step as main.py
SIM_TIME   = 12.0            # seconds to simulate
STEPS      = int(SIM_TIME / DT)

# Table boundaries (same as main.py)
T_LEFT, T_TOP, T_RIGHT, T_BOTTOM = 72, 92, 782, 618

NUM_BALLS = 8
BALL_R    = 18

# ─────────────────────────────────────────────────────────────────────────────
# Headless ball factory
# ─────────────────────────────────────────────────────────────────────────────

def spawn_balls(seed=42):
    """Create a reproducible set of balls (fixed seed for fair comparison)."""
    rng = random.Random(seed)
    balls, placed = [], []
    r   = BALL_R
    pad = r + 6

    colors = [(200, 50, 50)] * NUM_BALLS   # colour irrelevant for analysis

    for i in range(NUM_BALLS):
        for _ in range(20_000):
            x = rng.uniform(T_LEFT + pad, T_RIGHT  - pad)
            y = rng.uniform(T_TOP  + pad, T_BOTTOM - pad)
            if all(math.hypot(x - px, y - py) >= r + pr + 4
                   for px, py, pr in placed):
                spd   = rng.uniform(80, 240)
                angle = rng.uniform(0, 2 * math.pi)
                balls.append(Ball(x, y,
                                  spd * math.cos(angle),
                                  spd * math.sin(angle),
                                  radius=r, mass=1.0, color=colors[i]))
                placed.append((x, y, r))
                break
    return balls


def deep_copy_balls(balls):
    """Return a fresh independent copy of a ball list."""
    return [Ball(b.x, b.y, b.vx, b.vy,
                 radius=b.radius, mass=b.mass, color=b.color)
            for b in balls]


# ─────────────────────────────────────────────────────────────────────────────
# Core simulation step
# ─────────────────────────────────────────────────────────────────────────────

def simulate(balls, damping=0.0, restitution=1.0, steps=STEPS):
    """
    Run a headless simulation and return time series data.

    Returns
    -------
    times      : list of float  - time values
    ke_series  : list of float  - total KE at each step
    p_series   : list of float  - total momentum magnitude at each step
    """
    times     = []
    ke_series = []
    p_series  = []

    t = 0.0
    for _ in range(steps):
        # Euler step + wall collisions
        for b in balls:
            b.update(DT, damping)
            b.wall_collision(T_LEFT, T_TOP, T_RIGHT, T_BOTTOM)

        # Ball-ball collisions
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                resolve_ball_collision(balls[i], balls[j], restitution)

        t += DT
        times.append(t)
        ke_series.append(total_kinetic_energy(balls))
        px, py = total_momentum_vector(balls)
        p_series.append(math.sqrt(px * px + py * py))

    return times, ke_series, p_series


# ─────────────────────────────────────────────────────────────────────────────
# Plot styling
# ─────────────────────────────────────────────────────────────────────────────

DARK_BG  = "#0a0f1a"
PANEL_BG = "#10162a"
GRID_COL = "#1e2a45"
TEXT_COL = "#c8deff"
DIM_COL  = "#5a7aa8"

PALETTE = ["#41c880", "#5398ff", "#f5c842", "#e05555", "#c855c8"]


def style_axes(ax, title, xlabel, ylabel):
    ax.set_facecolor(PANEL_BG)
    ax.set_title(title, color=TEXT_COL, fontsize=12, pad=10)
    ax.set_xlabel(xlabel, color=DIM_COL, fontsize=10)
    ax.set_ylabel(ylabel, color=DIM_COL, fontsize=10)
    ax.tick_params(colors=DIM_COL)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID_COL)
    ax.grid(True, color=GRID_COL, linestyle="--", alpha=0.6)
    ax.legend(facecolor=PANEL_BG, edgecolor=GRID_COL,
              labelcolor=TEXT_COL, fontsize=9)


# ─────────────────────────────────────────────────────────────────────────────
# Experiment 1 – Restitution comparison (no damping)
# ─────────────────────────────────────────────────────────────────────────────

def experiment_restitution():
    print("Running Experiment 1: Restitution comparison ...")
    base_balls = spawn_balls(seed=7)

    restitution_values = [1.0, 0.7, 0.4]
    labels             = ["e = 1.0  (perfectly elastic)",
                          "e = 0.7  (moderately inelastic)",
                          "e = 0.4  (highly inelastic)"]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(DARK_BG)

    for e, lbl, col in zip(restitution_values, labels, PALETTE):
        balls = deep_copy_balls(base_balls)
        times, ke_series, _ = simulate(balls, damping=0.0, restitution=e)
        # Downsample for plotting (~500 points)
        step = max(1, len(times) // 500)
        ax.plot(times[::step], ke_series[::step], label=lbl, color=col, linewidth=1.8)

    style_axes(ax,
               "Experiment 1 – Effect of Restitution on Kinetic Energy\n"
               "(no damping; same initial conditions)",
               "Time (s)", "Total Kinetic Energy  [px²/s²]")

    fig.tight_layout()
    fig.savefig("experiment1_restitution.png", dpi=150, bbox_inches="tight",
                facecolor=DARK_BG)
    plt.close(fig)
    print("  -> Saved experiment1_restitution.png")


# ─────────────────────────────────────────────────────────────────────────────
# Experiment 2 – Damping comparison (elastic collisions)
# ─────────────────────────────────────────────────────────────────────────────

def experiment_damping():
    print("Running Experiment 2: Damping comparison ...")
    base_balls = spawn_balls(seed=7)

    damping_values = [0.0, 0.2, 0.6]
    labels         = ["λ = 0.0  (no friction)",
                      "λ = 0.2  (light friction)",
                      "λ = 0.6  (heavy friction)"]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(DARK_BG)

    for d, lbl, col in zip(damping_values, labels, PALETTE):
        balls = deep_copy_balls(base_balls)
        times, ke_series, _ = simulate(balls, damping=d, restitution=1.0)
        step = max(1, len(times) // 500)
        ax.plot(times[::step], ke_series[::step], label=lbl, color=col, linewidth=1.8)

    style_axes(ax,
               "Experiment 2 – Effect of Damping (Friction) on Kinetic Energy\n"
               "(elastic collisions; same initial conditions)",
               "Time (s)", "Total Kinetic Energy  [px²/s²]")

    fig.tight_layout()
    fig.savefig("experiment2_damping.png", dpi=150, bbox_inches="tight",
                facecolor=DARK_BG)
    plt.close(fig)
    print("  -> Saved experiment2_damping.png")


# ─────────────────────────────────────────────────────────────────────────────
# Experiment 3 – Momentum conservation check
# ─────────────────────────────────────────────────────────────────────────────

def experiment_momentum():
    print("Running Experiment 3: Momentum conservation check ...")
    balls = spawn_balls(seed=7)

    # Elastic, no damping -> momentum should be roughly conserved
    # (walls change momentum, so we track magnitude as a sanity check)
    times, _, p_series = simulate(balls, damping=0.0, restitution=1.0)

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(DARK_BG)

    step = max(1, len(times) // 500)
    ax.plot(times[::step], p_series[::step],
            color=PALETTE[2], linewidth=1.5, label="|p|  (elastic, no friction)")

    # Normalise to initial value so we can see relative change
    ax2 = ax.twinx()
    p0  = p_series[0] if p_series[0] != 0 else 1.0
    norm = [p / p0 for p in p_series]
    ax2.plot(times[::step], norm[::step],
             color=PALETTE[0], linewidth=1.2, linestyle="--",
             label="Normalised |p|")
    ax2.set_ylabel("Normalised momentum  (p / p₀)", color=DIM_COL, fontsize=10)
    ax2.tick_params(colors=DIM_COL)
    ax2.spines[["top"]].set_visible(False)
    ax2.spines[["right"]].set_color(GRID_COL)

    style_axes(ax,
               "Experiment 3 – Total Momentum Magnitude Over Time\n"
               "(elastic collisions, no friction; changes due to wall reflections)",
               "Time (s)", "Total Momentum Magnitude  [px·kg/s]")

    # Merge legends
    lines1, lbls1 = ax.get_legend_handles_labels()
    lines2, lbls2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, lbls1 + lbls2,
              facecolor=PANEL_BG, edgecolor=GRID_COL,
              labelcolor=TEXT_COL, fontsize=9)

    fig.tight_layout()
    fig.savefig("experiment3_momentum.png", dpi=150, bbox_inches="tight",
                facecolor=DARK_BG)
    plt.close(fig)
    print("  -> Saved experiment3_momentum.png")


# ─────────────────────────────────────────────────────────────────────────────
# Summary figure (3 subplots on one page for the report)
# ─────────────────────────────────────────────────────────────────────────────

def experiment_summary():
    print("Generating combined summary figure ...")
    base = spawn_balls(seed=7)

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle("2D Billiards Simulation – Experimental Results\n"
                 "CSCI 3010U  |  Yash Patel  |  100785833",
                 color=TEXT_COL, fontsize=13)

    gs   = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32)
    ax1  = fig.add_subplot(gs[0, 0])
    ax2  = fig.add_subplot(gs[0, 1])
    ax3  = fig.add_subplot(gs[1, :])

    # --- Subplot 1: Restitution ---
    for e, lbl, col in zip([1.0, 0.7, 0.4],
                            ["e=1.0 (elastic)", "e=0.7", "e=0.4 (inelastic)"],
                            PALETTE):
        balls = deep_copy_balls(base)
        t, ke, _ = simulate(balls, damping=0.0, restitution=e)
        step = max(1, len(t) // 300)
        ax1.plot(t[::step], ke[::step], label=lbl, color=col, linewidth=1.6)
    style_axes(ax1, "Effect of Restitution on KE", "Time (s)", "KE [px²/s²]")

    # --- Subplot 2: Damping ---
    for d, lbl, col in zip([0.0, 0.2, 0.6],
                            ["λ=0.0 (no friction)", "λ=0.2", "λ=0.6 (heavy)"],
                            PALETTE):
        balls = deep_copy_balls(base)
        t, ke, _ = simulate(balls, damping=d, restitution=1.0)
        step = max(1, len(t) // 300)
        ax2.plot(t[::step], ke[::step], label=lbl, color=col, linewidth=1.6)
    style_axes(ax2, "Effect of Damping on KE", "Time (s)", "KE [px²/s²]")

    # --- Subplot 3: Momentum ---
    balls = deep_copy_balls(base)
    t, ke, p = simulate(balls, damping=0.0, restitution=1.0)
    step = max(1, len(t) // 500)
    ax3.plot(t[::step], p[::step], color=PALETTE[2], linewidth=1.4,
             label="|p|  magnitude (elastic, no friction)")
    style_axes(ax3,
               "Total Momentum Magnitude Over Time  "
               "(changes caused by elastic wall reflections)",
               "Time (s)", "|p|  [px·kg/s]")

    fig.savefig("experiment_summary.png", dpi=150, bbox_inches="tight",
                facecolor=DARK_BG)
    plt.close(fig)
    print("  -> Saved experiment_summary.png")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("2D Billiards Simulation – Analysis")
    print("CSCI 3010U | Yash Patel | 100785833")
    print("=" * 60)

    experiment_restitution()
    experiment_damping()
    experiment_momentum()
    experiment_summary()

    print("\nAll experiments complete. PNG files saved to current directory.")
