import pyglet
from pyglet.gl import *
from math import sin,cos,tan
class Camera(object):
	def __init__ (self, screen_size, map_size, position):
		self.position = position
		self.screen_size = screen_size
		self.map_size = map_size
		self.newPositionX = 0
		self.newPositionY = 0
		self.newWeightedScale = 200
	def update(self, target, scale, angle, rate):
		self.target = target
		self.scale = scale
		self.angle = angle
		self.rate = rate
		
		self.newPositionX = ((self.newPositionX*(self.rate[0]-1))+self.target[0]) / self.rate[0]
		self.newPositionY = ((self.newPositionY*(self.rate[1]-1))+self.target[1]) / self.rate[1]

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glTranslatef(self.newPositionX*-1, self.newPositionY*-1, 0)
		glRotatef(self.angle,1.0,0.0,0.0)
		
		'''
		gluLookAt(
			self.newPositionX-self.screen_size[0]/2, self.newPositionY-self.screen_size[1]/2, +1.0,
			self.newPositionX-self.screen_size[0]/2, self.newPositionY-self.screen_size[1]/2, -1.0,
			sin(0), cos(0), 0.0
			)
		'''

		self.newWeightedScale = ((self.newWeightedScale*(30-1))+self.scale) / 30
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		aspect = self.screen_size[0] / self.screen_size[1]
		gluOrtho2D(
			-self.newWeightedScale * aspect,
			+self.newWeightedScale * aspect,
			-self.newWeightedScale,
			+self.newWeightedScale)

		self.mouseScale = self.newWeightedScale * aspect
		

		
	def hud_mode(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.screen_size[0], 0, self.screen_size[1])
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()