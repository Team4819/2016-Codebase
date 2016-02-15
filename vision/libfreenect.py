from ctypes import *

libfreenect = CDLL('libfreenect2.so')

libfreenect.freenect2.openDevice(1)