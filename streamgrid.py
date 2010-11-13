from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image
import sys
import time
import glob
import pickle
import random

rtri = 0.0
counter = 0
full = False
format = 'jpg'
diffs = {}
tex_index = {}
lasttime = time.time()

class Channel:
    
    def __init__(self, name):
        self.textures = []
        self.current_texture = None
        self.loop_length = 0.0
        self.loop_delay = 0.03
        self.last_frame_time = time.time()
        self.name = name
        self.width = 0
        self.height = 0
        self.prefix = 'frames/'
        self.window_id = -1
        self.frame_files = glob.glob(self.prefix + self.name + '*')
        self.frame_files.sort()
        try:
            self.loop_delay = pickle.load(open(self.prefix + self.name + '.dat', 'r'))
        except:
            self.loop_delay = 0.03 # 30fps
        self.frames = len(self.frame_files)
        self.frame_index = random.randint(1, self.frames) - 1
        
    def __repr__(self):
        return "<Channel '%s'>" % self.name
        
    def load_frame(self, frame_id):
        try:
            image = Image.open(self.frame_files[frame_id])
        except:
            return None
        self.width, self.height = image.size[0:2]
        data = image.tostring("raw", "RGBX", 0, -1)
        return data

    def load_texture(self, data):
        tex = glGenTextures(1)
        self.textures.append(tex)
        glBindTexture(GL_TEXTURE_2D, tex)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        return tex
        
class Stream:
    
    def __init__(self, grid):
        self.grid = grid
        self.r = 0.0
        self.dr = random.randint(-30, 30)
        self.channel = None
        self.z = 1.0
        self.dz = 0.0
        self.initddz = 0.001
        self.ddz = self.initddz
        
    def tick(self, tx, ty, dep, diff):
        glTranslatef(tx, ty, -dep)
        # SPIN
        if self.grid.modes.get('spinning', False):
            self.r += diff * self.dr
            glRotatef(self.r,1.0,1.0,1.0)
        else:
            self.r = 0.0
        # ZOOM
        if self.grid.modes.get('zooming', False):
            self.z = self.z + self.dz
            if self.z > 2.0 and self.ddz > 0:
                self.ddz = -self.ddz
            if self.z < 0 and self.ddz < 0:
                self.ddz = -self.ddz
            self.dz += self.ddz
            self.dz = min(self.dz, 0.05)
            self.dz = max(self.dz, -0.05)
            glTranslatef(0, 0, -(self.z - 1))
        else:
            self.z = 1.0
            self.dz = 0.0
            self.ddz = self.initddz
        
    def untick(self, tx, ty, dep, diff):
        # UNZOOM
        if self.grid.modes.get('zooming', False):
            glTranslatef(0, 0, (self.z - 1))
        # UNSPIN
        if self.grid.modes.get('spinning', False):
            glRotatef(-self.r,1.0,1.0,1.0)
        glTranslatef(-tx, -ty, dep)
        
class StreamGrid:
    
    def __init__(self):
        self.channels = []
        self.modes = {}
        self.rquad = 0.0
        self.grid_w = 6
        self.grid_h = 4
        self.last_render = time.time()
        # Identify available channels
        prefix = 'frames/'
        all_files = glob.glob('%s*.%s' % (prefix, format))
        for name in set([f.split('-')[0].replace(prefix, '') for f in all_files]):
            chan = Channel(name)
            self.channels.append(chan)
            random.shuffle(self.channels)
        self.streams = [Stream(self) for s in range(self.grid_w * self.grid_h)]
        for s in self.streams:
            s.channel = random.choice(self.channels)
        
    def init_gl(self, w, h):
        glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black
        glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
        glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
        glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
	
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(w)/float(h), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def resize(self, w, h):
        if h == 0:
	        h = 1
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(w)/float(h), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        sc = self.grid_w / 8.0
        dep = 8.0 * sc
        c = sc / 2.0
        
        diff = time.time() - self.last_render
        self.last_render = time.time()
        
        i = 0
        for x in range(self.grid_w):
            for y in range(self.grid_h):

                stream = self.streams[i]
                channel = stream.channel
                if time.time() - channel.last_frame_time > 0.03:#channel.loop_delay:
                    channel.last_frame_time = time.time()
                    channel.frame_index += 1
                    if channel.frame_index >= channel.frames:
                        channel.frame_index = 0
                    glDeleteTextures(channel.current_texture)
                    channel.current_texture = None

                if not channel.current_texture:
                    channel.current_texture = channel.load_texture(channel.load_frame(channel.frame_index))
                    
                # Evenly spaced, centered grid
                tx = -(self.grid_w-1) * sc / 2 + sc * x
                ty = -(self.grid_h-1) * sc / 2 + sc * y
                    
                stream.tick(tx, ty, dep, diff)
                
                glBindTexture(GL_TEXTURE_2D, channel.current_texture)            
                glBegin(GL_QUADS)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(-c, -c, 0.0)
                glTexCoord2f(1.0, 0.0)
                glVertex3f(c, -c, 0.0)
                glTexCoord2f(1.0, 1.0)
                glVertex3f(c, c, 0.0)
                glTexCoord2f(0.0, 1.0)
                glVertex3f(-c, c, 0.0)
                glEnd()
                
                stream.untick(tx, ty, dep, diff)
                i += 1

        glFinish()
        glutSwapBuffers()
    
    def key_pressed(self, *args):
        global full
        # If escape is pressed, kill everything.
        if args[0] == '\033':
            glutDestroyWindow(self.window_id)
            sys.exit()
        elif args[0] == 'f':
            full = not full
            if full:
                glutFullScreen(full)
        elif args[0] == 's':
            self.modes['spinning'] = not self.modes.get('spinning', False)
        elif args[0] == 'z':
            self.modes['zooming'] = not self.modes.get('zooming', False)
	    
    def idle(self):
        glutPostRedisplay()

# Print message to console, and kick off the main to get it rolling.
print "Hit ESC key to quit."

if __name__ == '__main__':
    grid = StreamGrid()
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow("StreamGrid - \"Copyright violation from every angle!\"")
    grid.window_id = window
    glutDisplayFunc(grid.draw)
    glutIdleFunc(grid.idle)
    glutReshapeFunc(grid.resize)
    glutKeyboardFunc(grid.key_pressed)

    grid.init_gl(640, 480)
    glutMainLoop()
    	
