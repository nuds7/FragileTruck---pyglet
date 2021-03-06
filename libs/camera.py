import pyglet
from pyglet.gl import *
glEnable(GL_TEXTURE_2D)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
from math import sin,cos,tan
import pymunk
from pymunk import Vec2d

def worldMouse(mX, mY, cameraPosX, cameraPosY, camera_scale, screen_size):
	aspect = screen_size[0]/screen_size[1]
	wmX = (cameraPosX - (camera_scale*aspect)) + mX*((camera_scale*aspect)/screen_size[0])*2
	wmY = (cameraPosY - (camera_scale)) + mY*((camera_scale)/screen_size[1])*2
	wmPos = wmX, wmY
	return wmPos

class Camera(object):
	def __init__ (self, screen_size, map_size, position):
		self.position = position
		self.screen_size = screen_size
		self.aspect = self.screen_size[0] / self.screen_size[1]
		self.map_size = map_size
		self.newPositionX = map_size[0]//2
		self.newPositionY = map_size[1]//2
		self.newAngle = 0
		self.newWeightedScale = 0
		self.newTarget = [0,0]
		self.scale = map_size[1]/4
		
	def update(self, target, scale, angle, rate, scaleRate):
		self.target = target
		self.scale = scale
		self.scaleRate = scaleRate
		self.rate = rate
		
		if self.target[0] > self.newWeightedScale * self.aspect:
			self.newTarget[0] = self.target[0]
		else: 
			self.newTarget[0] = self.newWeightedScale * self.aspect
		if self.target[1] > self.newWeightedScale:
			self.newTarget[1] = self.target[1]
		else: 
			self.newTarget[1] = self.newWeightedScale
		
		if self.target[0] < self.map_size[0] - (self.newWeightedScale * self.aspect) and self.target[0] > self.newWeightedScale * self.aspect:
			self.newTarget[0] = self.target[0]
		elif self.target[0] > self.newWeightedScale * self.aspect: 
			self.newTarget[0] = self.map_size[0] - self.newWeightedScale * self.aspect

		if self.target[1] < self.map_size[1] - self.newWeightedScale and self.target[1] > self.newWeightedScale:
			self.newTarget[1] = self.target[1]
		elif self.target[1] > self.newWeightedScale: 
			self.newTarget[1] = self.map_size[1] - self.newWeightedScale

		''' # Uncomment to bind zooming to the map size
		# Keep the scale smaller than the map unless the map is smaller than the screen res
		if self.map_size[1] > self.screen_size[1]:
			if self.scale >= self.map_size[1]/2:
				self.scale = self.map_size[1]/2
		if self.map_size[0] > self.screen_size[0]:
			if self.scale*self.aspect >= self.map_size[0]/2:
				self.scale = (self.map_size[0]/2) / self.aspect
		'''
		# Make the camera center the map if the map is smaller than the screen
		if self.scale * self.aspect >= self.map_size[0]/2:
			self.newTarget[0] = self.map_size[0]/2
		if self.scale >= self.map_size[1]/2:
			self.newTarget[1] = self.map_size[1]/2
			

		self.newPositionX = ((self.newPositionX*(self.rate[0]-1))+self.newTarget[0]) / self.rate[0]
		self.newPositionY = ((self.newPositionY*(self.rate[1]-1))+self.newTarget[1]) / self.rate[1]
		self.newWeightedScale = ((self.newWeightedScale*(self.scaleRate-1))+self.scale) / self.scaleRate
		
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		
		gluOrtho2D(
			-self.newWeightedScale * self.aspect,
			+self.newWeightedScale * self.aspect,
			-self.newWeightedScale,
			+self.newWeightedScale)

		self.newAngle = ((self.newAngle*(10-1))+angle) / 10
		glRotatef(self.newAngle,0.0,0.0,1.0)
		gluLookAt(self.newPositionX, self.newPositionY, +1,
				  self.newPositionX, self.newPositionY, -1,
				  sin(0),cos(0),0.0)

		glMatrixMode(GL_MODELVIEW)

		
		#glTranslatef(self.newPositionX*-1, self.newPositionY*-1, 0)
		glLoadIdentity()
		#self.mouseScale = self.newWeightedScale * self.aspect


	def edge_bounce(self, dx, dy, cameraPos):
		if (self.scale*self.aspect)*2 < self.map_size[0]:
			if cameraPos[0] < self.newWeightedScale*self.aspect:
				self.newPositionX -= dx*((self.newWeightedScale*self.aspect)/(self.screen_size[0]/2))
				cameraPos[0] = self.newWeightedScale*self.aspect
			if cameraPos[0] > self.map_size[0] - self.newWeightedScale*self.aspect:
				self.newPositionX -= dx*((self.newWeightedScale*self.aspect)/(self.screen_size[0]/2))
				cameraPos[0] = self.map_size[0] - self.newWeightedScale*self.aspect

		if self.scale*2 < self.map_size[1]:
			if cameraPos[1] < self.newWeightedScale:
				self.newPositionY -= dy*((self.newWeightedScale)/(self.screen_size[1]/2))
				cameraPos[1] = (self.newWeightedScale)
			if cameraPos[1] > self.map_size[1] - self.newWeightedScale:
				self.newPositionY -= dy*((self.newWeightedScale)/(self.screen_size[1]/2))
				cameraPos[1] = self.map_size[1] - self.newWeightedScale
		return cameraPos
	def zoom(self, zoom):
		pass

	def hud_mode(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.screen_size[0], 0, self.screen_size[1])
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

class PhysicsCamera(object):
	def __init__ (self, screen_size, map_size, position):
		self.position = position
		self.screen_size = screen_size
		self.aspect = self.screen_size[0] / self.screen_size[1]
		self.map_size = map_size
		self.newPositionX = map_size[0]//2
		self.newPositionY = map_size[1]//2
		self.newAngle = 0
		self.newWeightedScale = map_size[1]/4
		self.newTarget = [0,0]
		self.scale = map_size[1]/4


		self.camera_space = pymunk.Space()


		self.p_bod = pymunk.Body()
		self.a_bod = pymunk.Body(.01,pymunk.inf)

		rest_ln     = 3
		stiff       = 4
		damp        = 8

		left_spring   = pymunk.constraint.DampedSpring(self.p_bod, self.a_bod, (0,0),  (0,0), rest_ln, stiff, damp)
		left_spring.error_bias = pow(.5,60)
		self.camera_space.add(self.a_bod, left_spring)

		self.x = 0
		self.y = 0
		
	def update(self, target, scale, angle, rate, scaleRate):
		self.camera_space.step(.015)
		self.target = target
		self.scale = scale
		self.scaleRate = scaleRate
		self.rate = rate
		
		if self.target[0] > self.newWeightedScale * self.aspect:
			self.newTarget[0] = self.target[0]
		else: 
			self.newTarget[0] = self.newWeightedScale * self.aspect
		if self.target[1] > self.newWeightedScale:
			self.newTarget[1] = self.target[1]
		else: 
			self.newTarget[1] = self.newWeightedScale
		
		if self.target[0] < self.map_size[0] - (self.newWeightedScale * self.aspect) and self.target[0] > self.newWeightedScale * self.aspect:
			self.newTarget[0] = self.target[0]
		elif self.target[0] > self.newWeightedScale * self.aspect: 
			self.newTarget[0] = self.map_size[0] - self.newWeightedScale * self.aspect

		if self.target[1] < self.map_size[1] - self.newWeightedScale and self.target[1] > self.newWeightedScale:
			self.newTarget[1] = self.target[1]
		elif self.target[1] > self.newWeightedScale: 
			self.newTarget[1] = self.map_size[1] - self.newWeightedScale

		''' # Uncomment to bind zooming to the map size
		# Keep the scale smaller than the map unless the map is smaller than the screen res
		if self.map_size[1] > self.screen_size[1]:
			if self.scale >= self.map_size[1]/2:
				self.scale = self.map_size[1]/2
		if self.map_size[0] > self.screen_size[0]:
			if self.scale*self.aspect >= self.map_size[0]/2:
				self.scale = (self.map_size[0]/2) / self.aspect
		'''
		# Make the camera center the map if the map is smaller than the screen
		if self.scale * self.aspect >= self.map_size[0]/2:
			self.newTarget[0] = self.map_size[0]/2
		if self.scale >= self.map_size[1]/2:
			self.newTarget[1] = self.map_size[1]/2
			

		self.x = ((self.x*(self.rate[0]-1))+self.newTarget[0]) / self.rate[0]
		self.y = ((self.y*(self.rate[1]-1))+self.newTarget[1]) / self.rate[1]

		self.p_bod.position = Vec2d(self.x,self.y)
		self.p_bod.velocity = Vec2d(0,0)
		self.newPositionX,self.newPositionY = self.a_bod.position

		self.newWeightedScale = ((self.newWeightedScale*(self.scaleRate-1))+self.scale) / self.scaleRate
		
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		
		gluOrtho2D(
			-self.newWeightedScale * self.aspect,
			+self.newWeightedScale * self.aspect,
			-self.newWeightedScale,
			+self.newWeightedScale)

		self.newAngle = ((self.newAngle*(10-1))+angle) / 10
		glRotatef(self.newAngle,0.0,0.0,1.0)
		gluLookAt(self.newPositionX, self.newPositionY, +1,
				  self.newPositionX, self.newPositionY, -1,
				  sin(0),cos(0),0.0)

		glMatrixMode(GL_MODELVIEW)

		
		#glTranslatef(self.newPositionX*-1, self.newPositionY*-1, 0)
		glLoadIdentity()
		#self.mouseScale = self.newWeightedScale * self.aspect

	def zoom(self, zoom):
		pass

	def hud_mode(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.screen_size[0], 0, self.screen_size[1])
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()