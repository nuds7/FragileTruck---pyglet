import pyglet
from pyglet.gl import *
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

def sprite_overlay(sprite, amount, target):
	if sprite.color[0] > target[0]:
		amount[0] = -amount[0]
	if sprite.color[1] > target[1]:
		amount[1] = -amount[1]
	if sprite.color[2] > target[2]:
		amount[2] = -amount[2]
	if sprite.color[0] - target[0] > 10:
		#if sprite.color[0] != target[0]:
		sprite.color[0] += amount[0]
	if sprite.color[1] - target[1] > 10:
		#if sprite.color[1] != target[1]:
		sprite.color[1] += amount[1]
	if sprite.color[2] - target[2] > 10:
		#if sprite.color[2] != target[2]:
		sprite.color[2] += amount[2]
	#sprite.color = (color[0],color[1],color[2])
	return sprite.color

class Collectable(object):
	def __init__(self, position, overlay_color, image):
		self.position = position
		#self.ui_batch = ui_batch
		
		self.image = imageloader(image, 'placeholder.png')
		self.image.anchor_x = self.image.width/2
		self.image.anchor_y = self.image.height/2
		self.sprite = pyglet.sprite.Sprite(self.image)
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
		self.angle_target = 90

		self.weightedX = position[0]
		self.weightedY = position[1]
		self.radiusTarget = 30 # uniform(25,50)
		self.stage1 = False
		self.done = False

		self.stage2 = False
		self.stage3 = False
		self.ui_batch_set = False
		self.opacity_set = False
		self.opacity = 255
		self.overlay_color = overlay_color
		self.sprite.color = overlay_color

		self.pos = 100

		self.countdown = 120 # uniform(120,140)
		#self.space_to_add = self.sprite.image.width/2
		#self.score = 0
	def setup_pyglet_batch(self, level_batch, ui_batch, ordered_group):
		self.sprite.batch = level_batch
		self.sprite.group = ordered_group
		self.ui_batch = ui_batch
		#, batch = level_batch, group = ordered_group
	def update(self, player_pos, x_offset):
		self.score = 0
		if not self.collected:
			distance = sqrt((player_pos[0] - self.position[0])**2 + (player_pos[1] - self.animateY)**2)
			if distance < 60:
				#self.score = self.score_to_add
				self.collected = True
				self.stage1 = True
				self.sprite.color = [250,250,250]

			if self.animateY - self.animateYTargetPos < .5:
				self.animateYTarget = self.animateYTargetNeg
			if self.animateY - self.animateYTargetNeg > -.5:
				self.animateYTarget = self.animateYTargetPos

			self.animateY = ((self.animateY*(50-1))+self.animateYTarget) / 50
			self.sprite.set_position(self.position[0],self.animateY)

			#self.weightedX = player_pos[0]
			#self.weightedY = player_pos[1]
			self.angle = -atan2((self.position[1]-self.animateY),(self.position[0]-player_pos[0]))
			self.radius = distance

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
				if distance < 4:
					self.stage1 = False
					self.stage2 = True

			self.weightedX = ((self.weightedX*(1-1))+player_pos[0]) / 1
			self.weightedY = ((self.weightedY*(1-1))+player_pos[1]) / 1
			self.x = self.radius *cos(self.angle) + self.weightedX
			self.y = self.radius *sin(self.angle) + self.weightedY

			self.angle += self.add

			self.sprite.color = sprite_overlay(self.sprite, [3,3,3], self.overlay_color) ###

			self.sprite.set_position(self.x,self.y)

		if self.stage2:
			if self.opacity > 10:
				self.opacity -= 5
			else:
				self.sprite.color = [250,250,250]
				self.stage2 = False
				self.stage3 = True
			self.sprite.opacity = self.opacity 

		if self.stage3:
			if self.ui_batch_set == False:
				self.sprite.batch = self.ui_batch
				self.sprite.scale = 5
				self.ui_batch_set = True
			if self.opacity < 255:
				self.opacity += 5
			if self.sprite.scale != 1:
				if self.sprite.scale > 1:
					self.sprite.scale -= 0.1
				if self.sprite.scale < 1:
					self.sprite.scale += 0.1

			self.sprite.opacity = self.opacity
			self.sprite.color = sprite_overlay(self.sprite, [4,4,4], self.overlay_color)
			self.sprite.set_position(16+x_offset,16)