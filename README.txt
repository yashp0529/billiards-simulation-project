============================================================
  2D Billiards Physics Simulation
  CSCI 3010U - Simulation and Modeling
  Yash Patel | 100785833
  yash.patel@ontariotechu.net
============================================================

PROJECT FILES
-------------
  ball.py          - Ball class (Euler method, wall collisions, damping)
  physics.py       - Ball-ball collision detection and response
  main.py          - Interactive Pygame simulation (run this to play)
  analysis.py      - Headless experiment runner (generates PNG graphs)
  requirements.txt - Python package dependencies
  README.txt       - This file


------------------------------------------------------------
STEP 1 - REQUIREMENTS
------------------------------------------------------------
You need Python 3.10 or higher installed on your system.
Download Python from: https://www.python.org/downloads/

To check your Python version, open a terminal and run:
  python --version

The following Python packages are required:
  - pygame    (for the interactive simulation window)
  - matplotlib (for generating experiment graphs)
  - numpy     (used internally by matplotlib)


------------------------------------------------------------
STEP 2 - INSTALL DEPENDENCIES
------------------------------------------------------------
Open a terminal (Command Prompt or PowerShell on Windows).

Navigate to the project folder:
  cd c:\Users\DEFECTIVE\.gemini\antigravity\playground\billiards-sim

Install all required packages at once using:
  pip install -r requirements.txt

Wait for the installation to finish. You should see a message
like "Successfully installed pygame matplotlib numpy ..."

If pip is not found, try:
  python -m pip install -r requirements.txt


------------------------------------------------------------
STEP 3 - RUN THE INTERACTIVE SIMULATION
------------------------------------------------------------
Make sure you are in the project folder, then run:
  python main.py

A window titled "2D Billiards Simulation" will open showing:
  - A green billiards table with 8 coloured balls
  - A right-hand panel (HUD) displaying:
      * Total kinetic energy of the system
      * Elapsed simulation time
      * Number of ball-ball collisions
      * Current damping and restitution values
      * A live kinetic energy graph

KEYBOARD CONTROLS (inside the simulation window):
  SPACE       - Pause or resume the simulation
  R           - Reset with new random ball positions and velocities
  UP arrow    - Increase damping (more friction)
  DOWN arrow  - Decrease damping (less friction)
  RIGHT arrow - Increase restitution (more elastic/bouncy collisions)
  LEFT arrow  - Decrease restitution (more energy lost per collision)
  ESC         - Quit the simulation

TIP: Try pressing SPACE to pause, then LEFT arrow several times to
lower the restitution to 0.4, then SPACE again to resume and watch
how balls lose energy much faster after collisions.


------------------------------------------------------------
STEP 4 - RUN THE ANALYSIS / GENERATE GRAPHS
------------------------------------------------------------
To run the experiments and generate the PNG graph files, run:
  python analysis.py

This will run the simulation three times in the background
(no window will open) and save the following PNG files to the
project folder:

  experiment1_restitution.png
      - Shows total kinetic energy over time for three different
        restitution values: e=1.0, e=0.7, and e=0.4
      - Demonstrates: elastic collisions conserve energy; inelastic
        collisions show step-like energy drops at each collision

  experiment2_damping.png
      - Shows total kinetic energy over time for three different
        damping coefficients: lambda=0.0, 0.2, and 0.6
      - Demonstrates: higher friction causes faster exponential decay

  experiment3_momentum.png
      - Shows total momentum magnitude over time (elastic, no friction)
      - Demonstrates: momentum changes only due to wall reflections

  experiment_summary.png
      - A single combined figure with all three plots above
      - Best one to include in your project report

Each experiment uses the same fixed random seed (seed=7) so the
results are reproducible and consistent every time you run it.


------------------------------------------------------------
TROUBLESHOOTING
------------------------------------------------------------

Problem: "ModuleNotFoundError: No module named 'pygame'"
Solution: Run:  pip install -r requirements.txt

Problem: The simulation window is blank or freezes immediately
Solution: Make sure you are running Python 3.10+. Try:
          python --version

Problem: "python" is not recognized as a command
Solution: On some systems use "python3" instead of "python":
          python3 main.py
          python3 analysis.py

Problem: Graphs are not generated / analysis.py crashes
Solution: Make sure matplotlib is installed:
          pip install matplotlib


------------------------------------------------------------
PROJECT STRUCTURE EXPLAINED
------------------------------------------------------------

ball.py
  - Defines the Ball class
  - Each ball has: x, y (position), vx, vy (velocity),
    radius, mass, and color
  - update(dt, damping): moves the ball using the Euler method
    and applies friction each time step
  - wall_collision(): detects and reflects the ball off table walls
  - kinetic_energy(): returns 0.5 * mass * (vx^2 + vy^2)

physics.py
  - resolve_ball_collision(b1, b2, restitution):
    detects overlap between two balls and resolves it using
    Newton's Law of Restitution with impulse-based response
  - total_kinetic_energy(balls): sums KE across all balls
  - total_momentum_vector(balls): computes system momentum

main.py
  - Initializes Pygame and creates the simulation window
  - Renders the table, balls, and HUD each frame at 120 FPS
  - Handles keyboard input for real-time parameter tuning
  - Stores the last 340 KE values and plots them live

analysis.py
  - Runs the simulation without Pygame (headless mode)
  - Performs three experiments varying restitution and damping
  - Saves results as PNG plots using matplotlib


============================================================
  Project for CSCI 3010U - Simulation and Modeling
  Ontario Tech University | Winter 2026
============================================================
