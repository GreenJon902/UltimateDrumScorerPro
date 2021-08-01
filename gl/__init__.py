import time

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import app_info
from app_info.gl import default_window_size


def setup():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(*default_window_size)

    wind = glutCreateWindow(app_info.name)
    glutDisplayFunc(showScreen)
    glutIdleFunc(showScreen)


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)



def start():
    glutMainLoop()


__all__ = ["setup", "start"]
