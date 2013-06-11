import pyglet
import pymunk
from math import sqrt,sin,cos,atan2
from random import uniform

def imageloader(image_file, placeholder):
	try:
		image = pyglet.resource.image(image_file)
	except:
		print('Missing "'+str(image_file)+'." Replacing with "'+str(placeholder)+'."')
		image = pyglet.resource.image(placeholder)
	return image

class Collectable:
	def __init__(self, position, score_to_add, image, level_batch, ui_batch, ordered_group):
		self.position = position
		self.ui_batch = ui_batch
		
		collectableImage = imageloader(image, 'placeholder.png')
		collectableImage.anchor_x = collectableImage.width/2
		collectableImage.anchor_y = collectableImage.height/2
		self.sprite = pyglet.sprite.Sprite(collectableImage, batch = level_batch, group = ordered_group)
		self.sprite.set_position(position[0],position[1])
		self.sprite.scale = .5

		self.collected = False
		
		self.animateY = position[1]
		self.animateYTargetNeg = position[1] + uniform(0,12)
		self.animateYTargetPos = position[1] - uniform(0,12)
		self.animateYTarget = self.animateYTargetPos
		self.animateFlip = True

		self.add = uniform(0.06,0.08)
		self.radius = 0
		self.angle = 0

		self.weightedX = position[0]
		self.weightedY = position[1]
		self.radiusTarget = uniform(30,50)
		self.stage1 = False
		self.done = False

		self.stage2 = False
		self.stage3 = False
		self.ui_batch_set = False
		self.opacity_set = False
		self.opacity = 255

		self.countdown = uniform(50,100)
		self.score_to_add = score_to_add
		self.score = 0

	def update(self, player_pos):
		self.score = 0
		if not self.collected:
			distance = sqrt((player_pos[0] - self.position[0])**2 + (player_pos[1] - self.animateY)**2)
			if distance < 60:
				self.score = self.score_to_add
				self.collected = True
				self.stage1 = True

			if self.animateY - self.animateYTargetPos < .5:
				self.animateYTarget = self.animateYTargetNeg
			if self.animateY - self.animateYTargetNeg > -.5:
				self.animateYTarget = self.animateYTargetPos

			self.animateY = ((self.animateY*(50-1))+self.animateYTarget) / 50
			self.sprite.set_position(self.position[0],self.animateY)

			#self.weightedX = player_pos[0]
			#self.weightedY = player_pos[1]
			self.angle = -atan2((self.position[1]-self.animateY),(self.position[0]-player_pos[0]))

		if self.stage1:
			self.radius = ((self.radius*(20-1))+self.radiusTarget) / 20
			if self.radius >= self.radiusTarget - 1 and self.countdown < 1:
				self.radiusTarget = 0
				self.done = True
			self.countdown -= 1
			if self.countdown < 1:
				self.countdown = 0
			if self.done:
				distance = sqrt((player_pos[0] - self.x)**2 + (player_pos[1] - self.y)**2)
				if distance < 10:
					self.stage1 = False
					self.stage2 = True

			self.weightedX = ((self.weightedX*(10-1))+player_pos[0]) / 10
			self.weightedY = ((self.weightedY*(10-1))+player_pos[1]) / 10
			self.x = self.radius *cos(self.angle) + self.weightedX
			self.y = self.radius *sin(self.angle) + self.weightedY

			self.angle += self.add

			self.sprite.set_position(self.x,self.y)

		if self.stage2:
			if self.opacity > 10:
				self.opacity -= 5
			else:
				self.stage2 = False
				self.stage3 = True
			self.sprite.opacity = self.opacity 

		if self.stage3:
			if self.ui_batch_set == False:
				self.sprite.batch = self.ui_batch
				self.sprite.scale = 1
				self.ui_batch_set = True
			if self.opacity < 255:
				self.opacity += 5
			self.sprite.opacity = self.opacity
			self.sprite.set_position(10,12)