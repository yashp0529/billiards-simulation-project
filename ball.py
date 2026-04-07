"""
ball.py - Ball class for the 2D Billiards Simulation
CSCI 3010U - Simulation and Modeling
Yash Patel - 100785833
"""

import math


class Ball:
    """
    Represents a 2D billiard ball modelled as a rigid disk.

    Attributes
    ----------
    x, y     : float - position (pixels)
    vx, vy   : float - velocity (pixels/second)
    radius   : float - radius (pixels)
    mass     : float - mass (kg, normalised to 1.0)
    color    : tuple - RGB display colour
    """

    def __init__(self, x, y, vx=0.0, vy=0.0, radius=18, mass=1.0, color=(255, 255, 255)):
        self.x      = float(x)
        self.y      = float(y)
        self.vx     = float(vx)
        self.vy     = float(vy)
        self.radius = float(radius)
        self.mass   = float(mass)
        self.color  = color

    # ── Physics ────────────────────────────────────────────────────────────────

    def kinetic_energy(self):
        """
        Compute kinetic energy: KE = (1/2) * m * v^2
        where v^2 = vx^2 + vy^2
        """
        return 0.5 * self.mass * (self.vx ** 2 + self.vy ** 2)

    def speed(self):
        """Scalar speed: |v| = sqrt(vx^2 + vy^2)"""
        return math.sqrt(self.vx ** 2 + self.vy ** 2)

    def update(self, dt, damping=0.0):
        """
        Advance the ball by one time step using the Euler method.

        The Euler method approximates the ODE solution as:
            v(t+dt) = v(t) * (1 - lambda * dt)   <- damping (friction)
            x(t+dt) = x(t) + v(t) * dt           <- Euler position update

        Parameters
        ----------
        dt      : float - time step in seconds
        damping : float - friction coefficient lambda (s^-1)
        """
        # Apply friction: velocity decays proportionally each step
        decay   = max(0.0, 1.0 - damping * dt)
        self.vx *= decay
        self.vy *= decay

        # Euler forward integration
        self.x += self.vx * dt
        self.y += self.vy * dt

    def wall_collision(self, left, top, right, bottom):
        """
        Detect and respond to ball-wall collisions.

        When a ball hits a wall the velocity component perpendicular
        to that wall is reversed (elastic wall reflection).
        The ball is also repositioned to prevent tunnelling.

        Returns True if any wall was hit.
        """
        hit = False
        r   = self.radius

        # Left wall
        if self.x - r < left:
            self.x  = left + r
            self.vx = abs(self.vx)
            hit = True
        # Right wall
        elif self.x + r > right:
            self.x  = right - r
            self.vx = -abs(self.vx)
            hit = True

        # Top wall
        if self.y - r < top:
            self.y  = top + r
            self.vy = abs(self.vy)
            hit = True
        # Bottom wall
        elif self.y + r > bottom:
            self.y  = bottom - r
            self.vy = -abs(self.vy)
            hit = True

        return hit

    def __repr__(self):
        return (f"Ball(pos=({self.x:.1f}, {self.y:.1f}), "
                f"v=({self.vx:.1f}, {self.vy:.1f}), "
                f"KE={self.kinetic_energy():.2f})")
