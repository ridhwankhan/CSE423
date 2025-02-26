import random
import time
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ==========================
# Configuration and Constants
# ==========================

# Window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Spaceship (rocket) properties
SPACESHIP_WIDTH = 100
SPACESHIP_HEIGHT = 40

# Projectile properties
PROJECTILE_RADIUS = 5
PROJECTILE_SPEED = 400.0  # pixels per second

# Falling circles
BASE_CIRCLE_RADIUS = 15
CIRCLE_FALL_SPEED = 100.0  # pixels per second
CIRCLE_SPAWN_PROB = 0.015  # Probability per frame of spawning a new circle
UNIQUE_CIRCLE_PROB = 0.15  # Probability that a spawned circle is "unique"
UNIQUE_CIRCLE_BONUS = 3    # Extra points for hitting unique circles

# Game thresholds for ending conditions
CONSECUTIVE_MISS_THRESHOLD = 3  # Miss 3 falling circles in a row => Game Over
MISFIRE_THRESHOLD = 3            # Fire 3 times without hitting a circle => Game Over

# Button sizes and positions
BUTTON_SIZE = 40
RESTART_BUTTON_BOUNDS = (10, WINDOW_HEIGHT - 50, 40, 40)
play_button_x = WINDOW_WIDTH//2 - BUTTON_SIZE//2
PLAY_BUTTON_BOUNDS = (play_button_x, WINDOW_HEIGHT - 50, 40, 40)
quit_button_x = WINDOW_WIDTH - 50
QUIT_BUTTON_BOUNDS = (quit_button_x, WINDOW_HEIGHT - 50, 40, 40)

# ==========================
# Global Game State Variables
# ==========================
score = 0
consecutive_misses = 0
misfires = 0
GAME_OVER = False
PAUSED = False

spaceship_x = WINDOW_WIDTH // 2
spaceship_y = 50

last_frame_time = time.time()

falling_circles = []
projectiles = []

# ==========================
# Drawing Utility Functions
# ==========================

def draw_pixel(x, y):
    """Draw a single pixel (point) at (x, y)."""
    glVertex2f(x, y)

def draw_midpoint_circle(cx, cy, r):
    """Draw a circle using the midpoint circle algorithm and GL_POINTS."""
    x = 0
    y = r
    p = 1 - r

    def plot_circle_points(cx, cy, x, y):
        # 8-way symmetry of a circle
        draw_pixel(cx + x, cy + y)
        draw_pixel(cx - x, cy + y)
        draw_pixel(cx + x, cy - y)
        draw_pixel(cx - x, cy - y)
        draw_pixel(cx + y, cy + x)
        draw_pixel(cx - y, cy + x)
        draw_pixel(cx + y, cy - x)
        draw_pixel(cx - y, cy - x)

    plot_circle_points(cx, cy, x, y)
    while x < y:
        x += 1
        if p < 0:
            p += 2*x + 1
        else:
            y -= 1
            p += 2*(x - y) + 1
        plot_circle_points(cx, cy, x, y)

def draw_midpoint_line(x0, y0, x1, y1):
    """Draw a line using the midpoint line algorithm."""
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = abs(y1 - y0)
    error = dx / 2.0
    y = y0
    ystep = 1 if y0 < y1 else -1

    for x in range(x0, x1+1):
        if steep:
            draw_pixel(y, x)
        else:
            draw_pixel(x, y)
        error -= dy
        if error < 0:
            y += ystep
            error += dx

def draw_line(x0, y0, x1, y1):
    """Helper to draw a line using the midpoint line function."""
    draw_midpoint_line(x0, y0, x1, y1)

def draw_button(x, y, w, h):
    """Draw a simple filled rectangle for buttons using points."""
    for row in range(y, y+h):
        for col in range(x, x+w):
            draw_pixel(col, row)

def draw_projectile(px, py, r=PROJECTILE_RADIUS):
    """Draw the projectile as a small circle."""
    glColor3f(1.0, 1.0, 0.0)  # Yellow projectile
    draw_midpoint_circle(px, py, r)

def draw_filling_row(cx, base_y, y_off, x_start, x_end):
    """Draw a horizontal line of pixels (for the spaceship) at a specific row."""
    # Note: Ensure all values are integers
    y = int(base_y + y_off)
    start_x = int(cx + x_start)
    end_x = int(cx + x_end)
    for x in range(start_x, end_x + 1):
        draw_pixel(x, y)

def draw_spaceship():
    """Draw a rocket-like spaceship using only points."""
    cx = int(spaceship_x)  # Ensure integer for drawing
    base_y = int(spaceship_y)

    # Red cone at top
    glColor3f(1.0, 0.0, 0.0)
    draw_filling_row(cx, base_y, 38, 0, 0)    # Tip
    draw_filling_row(cx, base_y, 36, -2, 2)
    draw_filling_row(cx, base_y, 34, -2, 2)
    draw_filling_row(cx, base_y, 32, -4, 4)

    # White body
    glColor3f(1.0, 1.0, 1.0)
    for y_off in [30,28,26,24,22]:
        draw_filling_row(cx, base_y, y_off, -4, 4)

    # Blue fins
    glColor3f(0.0, 0.0, 1.0)
    draw_filling_row(cx, base_y, 18, -6, 6)
    draw_filling_row(cx, base_y, 16, -6, 6)
    draw_filling_row(cx, base_y, 14, -8, 8)
    draw_filling_row(cx, base_y, 12, -6, 6)

    # More white body
    glColor3f(1.0, 1.0, 1.0)
    for y_off in [10,8,6,4]:
        draw_filling_row(cx, base_y, y_off, -4, 4)

    # Taper bottom
    draw_filling_row(cx, base_y, 2, -2, 2)
    # Bottom nozzle
    draw_filling_row(cx, base_y, 0, 0, 0)

def draw_falling_circle(circle):
    """Draw a falling circle. Unique circles oscillate in radius."""
    base_radius = circle["radius"]
    if circle["unique"]:
        elapsed = time.time() - circle["spawn_time"]
        oscillation = math.sin(elapsed * 5) * 5
        draw_radius = int(base_radius + oscillation)
        glColor3f(1.0, 0.5, 0.0)  # Orange for unique
    else:
        draw_radius = base_radius
        glColor3f(0.0, 0.0, 1.0)  # Blue for normal

    draw_midpoint_circle(circle["x"], circle["y"], max(1, draw_radius))

def draw_buttons():
    """Draw the three top buttons: Restart, Play/Pause, Quit."""
    # Restart (Back) button - white box with arrow
    glColor3f(1.0, 1.0, 1.0)
    draw_button(*RESTART_BUTTON_BOUNDS)
    glColor3f(0.0, 0.0, 0.0)
    (bx, by, bw, bh) = RESTART_BUTTON_BOUNDS
    arrow_center_x = bx + bw//2
    arrow_center_y = by + bh//2
    draw_line(arrow_center_x+10, arrow_center_y, arrow_center_x-10, arrow_center_y)
    draw_line(arrow_center_x-10, arrow_center_y, arrow_center_x-5, arrow_center_y+5)
    draw_line(arrow_center_x-10, arrow_center_y, arrow_center_x-5, arrow_center_y-5)

    # Play/Pause button - amber box with play/pause icons
    glColor3f(1.0, 0.7, 0.0)
    draw_button(*PLAY_BUTTON_BOUNDS)
    glColor3f(0.0, 0.0, 0.0)
    (px, py, pw, ph) = PLAY_BUTTON_BOUNDS
    if PAUSED:
        # Play icon (triangle)
        draw_line(px+15, py+10, px+15, py+30)
        draw_line(px+15, py+30, px+25, py+20)
        draw_line(px+25, py+20, px+15, py+10)
    else:
        # Pause icon (two vertical lines)
        draw_line(px+15, py+10, px+15, py+30)
        draw_line(px+20, py+10, px+20, py+30)

    # Quit button - red box with a cross
    glColor3f(1.0, 0.0, 0.0)
    draw_button(*QUIT_BUTTON_BOUNDS)
    glColor3f(0.0, 0.0, 0.0)
    (qx, qy, qw, qh) = QUIT_BUTTON_BOUNDS
    draw_line(qx+10, qy+10, qx+30, qy+30)
    draw_line(qx+10, qy+30, qx+30, qy+10)

# ==========================
# Collision and Utility
# ==========================

def get_spaceship_aabb():
    """Get Axis-Aligned Bounding Box (AABB) for the spaceship."""
    return {
        "x": spaceship_x - SPACESHIP_WIDTH//2,
        "y": spaceship_y,
        "width": SPACESHIP_WIDTH,
        "height": SPACESHIP_HEIGHT
    }

def get_projectile_aabb(proj):
    """Get AABB for a projectile."""
    r = PROJECTILE_RADIUS
    return {
        "x": proj["x"] - r,
        "y": proj["y"] - r,
        "width": r*2,
        "height": r*2
    }

def get_circle_aabb(circle):
    """Get AABB for a circle. Unique circles have oscillating radius."""
    base_radius = circle["radius"]
    if circle["unique"]:
        elapsed = time.time() - circle["spawn_time"]
        oscillation = math.sin(elapsed * 5)*5
        draw_radius = int(base_radius + oscillation)
    else:
        draw_radius = base_radius
    return {
        "x": circle["x"] - draw_radius,
        "y": circle["y"] - draw_radius,
        "width": draw_radius * 2,
        "height": draw_radius * 2
    }

def has_collided(a, b):
    """Check if two AABBs collide."""
    return (a["x"] < b["x"] + b["width"] and
            a["x"] + a["width"] > b["x"] and
            a["y"] < b["y"] + b["height"] and
            a["y"] + a["height"] > b["y"])

def point_in_rect(px, py, rect):
    """Check if a point (px, py) is inside a rectangle defined by rect."""
    x, y, w, h = rect
    return (px >= x and px <= x+w and py >= y and py <= y+h)

# ==========================
# Drawing and Update Callbacks
# ==========================

def draw_game():
    """Main drawing function called by OpenGL each frame."""
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_POINTS)
    
    if not GAME_OVER:
        # Draw all falling circles
        for circle in falling_circles:
            draw_falling_circle(circle)
        
        # Draw all projectiles
        for proj in projectiles:
            draw_projectile(proj["x"], proj["y"])

        # Draw the spaceship (rocket)
        draw_spaceship()

        # Draw UI buttons (Restart, Play/Pause, Quit)
        draw_buttons()

    glEnd()
    glutSwapBuffers()

def update_game():
    """Update game state each frame (idle callback)."""
    global last_frame_time, GAME_OVER, PAUSED, score, misfires, consecutive_misses

    if GAME_OVER or PAUSED:
        # If game over or paused, no updates to movement or spawning
        return

    # Calculate delta time for frame-rate independent movement
    current_time = time.time()
    delta_time = current_time - last_frame_time
    last_frame_time = current_time

    # Update falling circles (move down)
    for circle in falling_circles[:]:
        circle["y"] -= CIRCLE_FALL_SPEED * delta_time

        # Check if circle hits spaceship
        if has_collided(get_spaceship_aabb(), get_circle_aabb(circle)):
            GAME_OVER = True
            print(f"Game Over! Final Score: {score}")
            return

        # Check if circle missed (passed below bottom)
        if circle["y"] < 0:
            falling_circles.remove(circle)
            consecutive_misses += 1
            print(f"Consecutive Misses: {consecutive_misses}")
            if consecutive_misses >= CONSECUTIVE_MISS_THRESHOLD:
                GAME_OVER = True
                print(f"Game Over! Final Score: {score}")
                return

    # Update projectiles (move up)
    for proj in projectiles[:]:
        proj["y"] += PROJECTILE_SPEED * delta_time
        if proj["y"] > WINDOW_HEIGHT:
            # Projectile off screen
            if not proj.get("hit_something", False):
                # Counts as a misfire if it never hit a circle
                misfires += 1
                print(f"Misfires: {misfires}")
                if misfires >= MISFIRE_THRESHOLD:
                    GAME_OVER = True
                    print(f"Game Over! Final Score: {score}")
                    return
            projectiles.remove(proj)

    # Check projectile-circle collisions
    for proj in projectiles[:]:
        for circle in falling_circles[:]:
            if has_collided(get_projectile_aabb(proj), get_circle_aabb(circle)):
                # On hit: increase score, remove projectile and circle
                proj["hit_something"] = True
                add_score = UNIQUE_CIRCLE_BONUS if circle["unique"] else 1
                score += add_score
                print(f"Score: {score}")
                falling_circles.remove(circle)
                projectiles.remove(proj)
                # Reset consecutive misses after successful hit
                consecutive_misses = 0
                break

    # Possibly spawn a new circle
    if random.random() < CIRCLE_SPAWN_PROB:
        unique = (random.random() < UNIQUE_CIRCLE_PROB)
        falling_circles.append({
            "x": random.randint(BASE_CIRCLE_RADIUS, WINDOW_WIDTH - BASE_CIRCLE_RADIUS),
            "y": WINDOW_HEIGHT - BASE_CIRCLE_RADIUS,
            "radius": BASE_CIRCLE_RADIUS,
            "unique": unique,
            "spawn_time": time.time()
        })

    # Request to draw again
    glutPostRedisplay()

# ==========================
# Input Handling
# ==========================
# Add a global cooldown variable
last_fire_time = 0.0   # Keeps track of the last time we fired a projectile
FIRE_COOLDOWN = 0.02    # Minimum time in seconds between consecutive shots

def handle_keyboard(key, x, y):
    global spaceship_x, GAME_OVER, PAUSED, last_fire_time

    if GAME_OVER:
        return

    current_time = time.time()

    # Check if space is pressed for firing
    if key == b' ':
        # Only fire if cooldown has passed
        if current_time - last_fire_time >= FIRE_COOLDOWN:
            projectiles.append({
                "x": spaceship_x,
                "y": spaceship_y + SPACESHIP_HEIGHT,
                "hit_something": False
            })
            last_fire_time = current_time

    if PAUSED:
        # If paused, ignore movement
        return

    # Movement keys
    if key == b'a':
        spaceship_x = max(spaceship_x - 20, SPACESHIP_WIDTH // 2)
    elif key == b'd':
        spaceship_x = min(spaceship_x + 20, WINDOW_WIDTH - SPACESHIP_WIDTH // 2)

def handle_mouse(button, state, mx, my):
    """Handle mouse clicks for buttons."""
    if state == GLUT_DOWN:
        converted_y = WINDOW_HEIGHT - my
        if point_in_rect(mx, converted_y, RESTART_BUTTON_BOUNDS):
            restart_game()
        elif point_in_rect(mx, converted_y, PLAY_BUTTON_BOUNDS):
            toggle_pause()
        elif point_in_rect(mx, converted_y, QUIT_BUTTON_BOUNDS):
            print(f"Goodbye! Final Score: {score}")
            glutLeaveMainLoop()

# ==========================
# Game Control Functions
# ==========================

def restart_game():
    """Reset all game variables and start over."""
    global GAME_OVER, PAUSED, score, consecutive_misses, misfires, falling_circles, projectiles, last_frame_time, spaceship_x
    GAME_OVER = False
    PAUSED = False
    score = 0
    consecutive_misses = 0
    misfires = 0
    falling_circles = []
    projectiles = []
    spaceship_x = WINDOW_WIDTH // 2
    last_frame_time = time.time()
    print("Starting Over!")

def toggle_pause():
    """Toggle between paused and playing states."""
    global PAUSED
    PAUSED = not PAUSED
    print("Paused" if PAUSED else "Resumed")

# ==========================
# Main Function
# ==========================

def main():
    global last_frame_time
    # Initialize GLUT
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Shoot the Circles Game")

    # Set clear color (background)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    # Set up an orthographic projection
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    # Register callback functions
    glutDisplayFunc(draw_game)
    glutIdleFunc(update_game)
    glutKeyboardFunc(handle_keyboard)
    glutMouseFunc(handle_mouse)

    last_frame_time = time.time()
    print("Game Started!")
    print("Use 'a' and 'd' to move, 'space' to fire. Make sure the window is focused!")

    # Start the main loop
    glutMainLoop()

if __name__ == "__main__":
    main()
