from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys, time

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

window = 0
rtri = 0.0
rquad = 0.0
counter = 0
cubelist = None

def InitGL(Width, Height):				# We call this right after our OpenGL window is created.
    global cubelist
    glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black
    glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
    glEnable(GL_TEXTURE_2D)
    glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
	
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    cubelist = glGenLists(1)
    glNewList(cubelist, GL_COMPILE)
    cube(0.3)
    glEndList()

def ReSizeGLScene(Width, Height):
    if Height == 0:
	    Height = 1

    glViewport(0, 0, Width, Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def cube(c):
    glBegin(GL_QUADS)			# Start Drawing The Cube
    glColor3f(0.0,1.0,0.0)			# Set The Color To Blue
    glVertex3f( c, c,-c)		# Top Right Of The Quad (Top)
    glVertex3f(-c, c,-c)		# Top Left Of The Quad (Top)
    glVertex3f(-c, c, c)		# Bottom Left Of The Quad (Top)
    glVertex3f( c, c, c)		# Bottom Right Of The Quad (Top)

    glColor3f(1.0,0.5,0.0)			# Set The Color To Orange
    glVertex3f( c,-c, c)		# Top Right Of The Quad (Bottom)
    glVertex3f(-c,-c, c)		# Top Left Of The Quad (Bottom)
    glVertex3f(-c,-c,-c)		# Bottom Left Of The Quad (Bottom)
    glVertex3f( c,-c,-c)		# Bottom Right Of The Quad (Bottom)

    glColor3f(1.0,0.0,0.0)			# Set The Color To Red
    glVertex3f( c, c, c)		# Top Right Of The Quad (Front)
    glVertex3f(-c, c, c)		# Top Left Of The Quad (Front)
    glVertex3f(-c,-c, c)		# Bottom Left Of The Quad (Front)
    glVertex3f( c,-c, c)		# Bottom Right Of The Quad (Front)

    glColor3f(1.0,1.0,0.0)			# Set The Color To Yellow
    glVertex3f( c,-c,-c)		# Bottom Left Of The Quad (Back)
    glVertex3f(-c,-c,-c)		# Bottom Right Of The Quad (Back)
    glVertex3f(-c, c,-c)		# Top Right Of The Quad (Back)
    glVertex3f( c, c,-c)		# Top Left Of The Quad (Back)

    glColor3f(0.0,0.0,1.0)			# Set The Color To Blue
    glVertex3f(-c, c, c)		# Top Right Of The Quad (Left)
    glVertex3f(-c, c,-c)		# Top Left Of The Quad (Left)
    glVertex3f(-c,-c,-c)		# Bottom Left Of The Quad (Left)
    glVertex3f(-c,-c, c)		# Bottom Right Of The Quad (Left)

    glColor3f(1.0,0.0,1.0)			# Set The Color To Violet
    glVertex3f( c, c,-c)		# Top Right Of The Quad (Right)
    glVertex3f( c, c, c)		# Top Left Of The Quad (Right)
    glVertex3f( c,-c, c)		# Bottom Left Of The Quad (Right)
    glVertex3f( c,-c,-c)		# Bottom Right Of The Quad (Right)
    glEnd()				# Done Drawing The Quad
    
# The main drawing function. 
def DrawGLScene():
    global rquad, counter, cubelist
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    w = h = 3
    sc = 1.0
    dep = 5
    xoff = 0
    
    for x in range(w):
        for y in range(h):
            # Evenly spaced, centered grid
            tx = -(w-1) * sc / 2 + sc * x
            ty = -(h-1) * sc / 2 + sc * y

            glTranslatef(tx + xoff, ty, -dep)
            glRotatef(rquad,1.0,1.0,1.0)
            glCallList(cubelist)
            glRotatef(-rquad,1.0,1.0,1.0)
            glTranslatef(-tx - xoff, -ty, dep)

    rquad = rquad - 0.20

    glFinish()
    glutSwapBuffers()

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
	# If escape is pressed, kill everything.
    if args[0] == ESCAPE:
	    glutDestroyWindow(window)
	    sys.exit()
	    
lasttime = time.time()
def idle():
    glutPostRedisplay()

def main():
	global window

	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
	glutInitWindowSize(640, 480)
	glutInitWindowPosition(0, 0)
	window = glutCreateWindow("StreamGrid")

	glutFullScreen()
	glutDisplayFunc(DrawGLScene)
	glutIdleFunc(idle)
	glutReshapeFunc(ReSizeGLScene)
	glutKeyboardFunc(keyPressed)
	InitGL(640, 480)

	
# Print message to console, and kick off the main to get it rolling.
print "Hit ESC key to quit."

if __name__ == '__main__':
	try:
		GLU_VERSION_1_2
	except:
		print "Need GLU 1.2 to run this demo"
		sys.exit(1)
	main()
	glutMainLoop()
    	
