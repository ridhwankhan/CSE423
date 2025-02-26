from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Global variables
points = []
speed = 1.0
freeze = False
blink = False
last_blink_time = time.time()


BOX_SIZE = 500

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.choice([-1, 1]) * speed * random.random()
        self.dy = random.choice([-1, 1]) * speed * random.random()
        self.color = [random.random(), random.random(), random.random()]

    def move(self):
        if not freeze:
            # Move point based on speed and direction
            self.x += self.dx
            self.y += self.dy
            
            # boundary collision and bounce
            if self.x <= -BOX_SIZE or self.x >= BOX_SIZE:
                self.dx = -self.dx
            if self.y <= -BOX_SIZE or self.y >= BOX_SIZE:
                self.dy = -self.dy
    
    def draw(self):
        glColor3f(*self.color)
        glBegin(GL_POINTS)
        glVertex2f(self.x, self.y)
        glEnd()

    def toggle_blink(self):
        # Change color to background color or original
        self.color = [0, 0, 0] if self.color != [0, 0, 0] else [random.random(), random.random(), random.random()]

def init():
    # Initialize OpenGL settings
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(5.0)

def display():
    global last_blink_time
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    # Draw all points
    for point in points:
        if blink and time.time() - last_blink_time > 0.5:
            point.toggle_blink()
        point.draw()
    
    if blink and time.time() - last_blink_time > 0.5:
        last_blink_time = time.time()  # Reset blink timer
    
    glutSwapBuffers()

def update(value):
    # Move points if not frozen
    if not freeze:
        for point in points:
            point.move()
    
    glutPostRedisplay()
    glutTimerFunc(33, update, 0)

def mouse(button, state, x, y):
    global blink
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Convert screen coordinates to OpenGL coordinates
        x_gl = (x - 250)
        y_gl = (250 - y)
        
        # Generate a new random point at the click position
        new_point = Point(x_gl, y_gl)
        points.append(new_point)
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Toggle blink
        blink = not blink

def keyboard(key, x, y):
    global speed, freeze
    if key == b' ':
        # Toggle freeze state
        freeze = not freeze
    glutPostRedisplay()

def special_keys(key, x, y):
    global speed
    if key == GLUT_KEY_UP:
        # Increase speed
        speed += 0.1
        for point in points:
            point.dx *= 1.1
            point.dy *= 1.1
    elif key == GLUT_KEY_DOWN:
        # Decrease speed
        speed = max(0.1, speed - 0.1)  # Prevent negative speed
        for point in points:
            point.dx *= 0.9
            point.dy *= 0.9
    glutPostRedisplay()

def setup():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-BOX_SIZE, BOX_SIZE, -BOX_SIZE, BOX_SIZE, -1, 1)
    glMatrixMode(GL_MODELVIEW)

# Program entry point
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(500, 500)
glutCreateWindow(b"Amazing Box")
glutDisplayFunc(display)
glutTimerFunc(33, update, 0)
glutMouseFunc(mouse)
glutKeyboardFunc(keyboard)
glutSpecialFunc(special_keys)
init()
setup()
glutMainLoop()
