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
		self.newAngle = 0
		self.newWeightedScale = 200
		self.newTarget = [0,0]
	def update(self, target, scale, angle, rate):
		self.target = target
		self.scale = scale
		#self.angle = angle
		self.rate = rate
		aspect = self.screen_size[0] / self.screen_size[1]

		if self.target[0] > self.newWeightedScale * aspect:
			self.newTarget[0] = self.target[0]
		else: 
			self.newTarget[0] = self.newWeightedScale * aspect
		if self.target[1] > self.newWeightedScale:
			self.newTarget[1] = self.target[1]
		else: 
			self.newTarget[1] = self.newWeightedScale

		if self.target[0] < self.map_size[0] - (self.newWeightedScale * aspect) and self.target[0] > self.newWeightedScale * aspect:
			self.newTarget[0] = self.target[0]
		elif self.target[0] > self.newWeightedScale * aspect: 
			self.newTarget[0] = self.map_size[0] - self.newWeightedScale * aspect

		if self.target[1] < self.map_size[1] - self.newWeightedScale and self.target[1] > self.newWeightedScale:
			self.newTarget[1] = self.target[1]
		elif self.target[1] > self.newWeightedScale: 
			self.newTarget[1] = self.map_size[1] - self.newWeightedScale


		self.newPositionX = ((self.newPositionX*(self.rate[0]-1))+self.newTarget[0]) / self.rate[0]
		self.newPositionY = ((self.newPositionY*(self.rate[1]-1))+self.newTarget[1]) / self.rate[1]
		self.newWeightedScale = ((self.newWeightedScale*(30-1))+self.scale) / 30
		
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		
		gluOrtho2D(
			-self.newWeightedScale * aspect,
			+self.newWeightedScale * aspect,
			-self.newWeightedScale,
			+self.newWeightedScale)

		self.newAngle = ((self.newAngle*(50-1))+angle) / 50
		glRotatef(self.newAngle,0.0,0.0,1.0)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glTranslatef(self.newPositionX*-1, self.newPositionY*-1, 0)
		
		#self.mouseScale = self.newWeightedScale * aspect
		
	def hud_mode(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.screen_size[0], 0, self.screen_size[1])
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()