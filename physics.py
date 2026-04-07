"""
physics.py - Collision detection and resolution functions
CSCI 3010U - Simulation and Modeling
Yash Patel - 100785833
"""

import math


def resolve_ball_collision(b1, b2, restitution=1.0):
    """
    Detect and resolve a collision between two balls using
    impulse-based rigid-body collision response.

    Algorithm
    ---------
    1. Compute the collision normal n (unit vector from b1 to b2).
    2. Compute the relative velocity along n:
           dvn = (v1 - v2) . n
    3. If dvn <= 0 the balls are already separating - skip.
    4. Compute impulse magnitude using Newton's Law of Restitution:
           J = -(1 + e) * dvn / (1/m1 + 1/m2)
    5. Apply impulse:
           v1 += (J / m1) * n
           v2 -= (J / m2) * n
    6. Positional correction: push balls apart to remove overlap.

    Parameters
    ----------
    b1, b2      : Ball  - the two balls
    restitution : float - coefficient of restitution e  (0 <= e <= 1)
                  e = 1 -> perfectly elastic  (no KE lost)
                  e = 0 -> perfectly inelastic (maximum KE lost)

    Returns True if a collision was resolved.
    """
    dx   = b2.x - b1.x
    dy   = b2.y - b1.y
    dist = math.sqrt(dx * dx + dy * dy)

    # Not touching
    if dist == 0 or dist >= b1.radius + b2.radius:
        return False

    # Unit normal from b1 -> b2
    nx = dx / dist
    ny = dy / dist

    # Relative velocity of b1 with respect to b2
    dvx = b1.vx - b2.vx
    dvy = b1.vy - b2.vy
    dvn = dvx * nx + dvy * ny        # component along normal

    # Balls are separating - no impulse needed
    if dvn <= 0:
        return False

    # Impulse scalar (Newton's law of restitution)
    inv_mass_sum = 1.0 / b1.mass + 1.0 / b2.mass
    J = -(1.0 + restitution) * dvn / inv_mass_sum

    # Update velocities
    b1.vx += (J / b1.mass) * nx
    b1.vy += (J / b1.mass) * ny
    b2.vx -= (J / b2.mass) * nx
    b2.vy -= (J / b2.mass) * ny

    # Positional correction - separate overlapping balls
    overlap = (b1.radius + b2.radius) - dist
    b1.x -= 0.5 * overlap * nx
    b1.y -= 0.5 * overlap * ny
    b2.x += 0.5 * overlap * nx
    b2.y += 0.5 * overlap * ny

    return True


def total_kinetic_energy(balls):
    """Return total system kinetic energy = sum(0.5 * m * v^2)."""
    return sum(b.kinetic_energy() for b in balls)


def total_momentum_vector(balls):
    """Return total linear momentum (px, py) = sum(m * v)."""
    px = sum(b.mass * b.vx for b in balls)
    py = sum(b.mass * b.vy for b in balls)
    return px, py
