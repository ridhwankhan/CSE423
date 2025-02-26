#22301143 -- Ridhwanur Rahman Khan
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Global Variables
rain_drops = []
num_drops = 100  # Number of rain drops

rain_angle = 0  
bg_color = [0.96, 0.87, 0.70]  
house_color = [0.4, 0.2, 0.1]  
is_day = True 


day_color = [0.96, 0.87, 0.70]  
night_color = [0.15, 0.15, 0.18]  
night_house_color = [0.2, 0.5, 0.7]  

def init_rain():
    global rain_drops
    # Create rain drops at random positions
    rain_drops = [[random.randint(0, 500), random.randint(250, 500)] for _ in range(num_drops)]

def draw_house():
    global house_color
    glColor3f(*house_color)  #  current color for the house
    glLineWidth(5)

    # main part of the house
    glBegin(GL_LINE_LOOP)
    glVertex2f(150, 100)
    glVertex2f(150, 300)
    glVertex2f(450, 300)
    glVertex2f(450, 100)
    glEnd()

    #  roof
    glBegin(GL_TRIANGLES)
    glVertex2f(130, 300)
    glVertex2f(470, 300)
    glVertex2f(300, 400)
    glEnd()

    # door 
    glBegin(GL_LINES)
    glVertex2f(200, 100)
    glVertex2f(200, 200)
    glVertex2f(250, 100)
    glVertex2f(250, 200)
    glVertex2f(200, 200)
    glVertex2f(250, 200)
    glEnd()

    # Door handle 
    glPointSize(5)
    glBegin(GL_POINTS)
    glVertex2f(240, 150)  # Position of the door handle
    glEnd()

    #  window 
    glBegin(GL_LINE_LOOP)
    glVertex2f(350, 220)
    glVertex2f(390, 220)
    glVertex2f(390, 260)
    glVertex2f(350, 260)
    glEnd()

    # 4 squares inside the window
    glBegin(GL_LINES)
    glVertex2f(370, 220)  
    glVertex2f(370, 260)  
    glVertex2f(350, 240)  
    glVertex2f(390, 240)  
    glEnd()

def draw_rain():
    # rain color based on day or night mode
    rain_color = (0.0, 0.5, 1.0) if is_day else (0.7, 0.7, 1.0)
    glColor3f(*rain_color)
    glBegin(GL_LINES)
    for drop in rain_drops:
        x, y = drop
        # Calculate the end point of the rain drop based on angle
        drop_angle = rain_angle * 0.1  # Reduce angle for smooth effect
        glVertex2f(x, y)
        glVertex2f(x + drop_angle, y - 10)  # Adjust the drop's angle and length
    glEnd()

def update_rain():
    # Move rain drops based on the rain_angle
    for drop in rain_drops:
        drop[0] += rain_angle * 0.1  # Slowly move the rain drop in the x direction
        drop[1] -= 5  # Move the rain drop downward
        # Reset position if it goes off the screen
        if drop[1] < 0:
            drop[1] = random.randint(250, 500)
            drop[0] = random.randint(0, 500)

def change_bg_color(target_color):
    global bg_color, is_day
    # Smoothly transition to the target color (day or night)
    for i in range(3):
        bg_color[i] += (target_color[i] - bg_color[i]) * 0.05  # Gradual change

    # Determine if it's day or night
    if target_color == day_color:
        is_day = True
    else:
        is_day = False

def change_house_color(target_color):
    global house_color
    # Smoothly transition the house color to the target color
    for i in range(3):
        house_color[i] += (target_color[i] - house_color[i]) * 0.05  # Gradual change

def handle_keys(key, x, y):
    global rain_angle
    if key == GLUT_KEY_LEFT: 
        rain_angle -= 1  
    elif key == GLUT_KEY_RIGHT:  
        rain_angle += 1 
    elif key == b'b':  
        change_bg_color(day_color)
        change_house_color((0.4, 0.2, 0.1)) 
    elif key == b'n':  
        change_bg_color(night_color)
        change_house_color(night_house_color)  
    glutPostRedisplay()

def show_screen():
    glClearColor(*bg_color, 1.0)  
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    draw_house()
    draw_rain()
    glFlush()
    glutSwapBuffers()

def update(value):
    update_rain()
    glutPostRedisplay()  
    glutTimerFunc(33, update, 0)  # 30 FPS

def setup():
    # viewport and projection
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

#start and execution
glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(500, 500)
glutInitWindowPosition(0, 0)
glutCreateWindow(b"House with Rain and Day/Night Mode")
setup()
init_rain()
glutDisplayFunc(show_screen)
glutTimerFunc(0, update, 0)
glutSpecialFunc(handle_keys)  # Use arrow keys
glutKeyboardFunc(handle_keys)  # Use 'b' and 'n' keys
glutMainLoop()
