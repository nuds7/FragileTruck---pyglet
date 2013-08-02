import pyglet
from pyglet.gl import *
import pymunk
from math import sqrt,sin,cos,atan2
from random import uniform
import loaders
import copy

class GroupWithMask(pyglet.graphics.Group):
	def __init__(self, x, y, width, height, parent=None):
		super(GroupWithMask, self).__init__(parent)
		self.x = x
		self.y = y
		self.width = width
		self.height = height

	def set_state(self):
		pyglet.gl.glScissor(self.x, self.y, self.width, self.height)
		pyglet.gl.glEnable(pyglet.gl.GL_SCISSOR_TEST)

	def unset_state(self):
		pyglet.gl.glDisable(pyglet.gl.GL_SCISSOR_TEST)

class PowerUp(object):
	def __init__(self, position, image_file, pwr_type='None', grav_mod_dir=(0,0), grav_finish_dir=(0,-800), accel_mod_amount=0, accel_finish_amount=4, duration=0):
		self.position 			 = position
		self.pwr_type			 = pwr_type
		self.grav_mod_dir 		 = grav_mod_dir
		self.grav_finish_dir 	 = grav_finish_dir
		self.accel_mod_amount 	 = accel_mod_amount
		self.accel_finish_amount = accel_finish_amount
		self.duration 			 = duration
		self.orig_dur = self.duration

		self.sprite = loaders.spriteloader(image_file, 
										   pos 					= position,
										   anchor 				= ('center','center'),
										   scale 				= .5,
										   linear_interpolation = True)

		self.collected = False
		self.do_action = False
		self.action_done = True
		self.bar_pos = 0
	def setup_modifiers(self, player, space):
		self.player 	= player
		self.space 		= space

	def setup_pyglet_batch(self, level_batch, ui_batch, ordered_group, ordered_group2, screen_res):
		self.sprite.batch = level_batch
		self.sprite.group = ordered_group

		self.mask_width = 300
		self.mask_height = 10
		self.mask_x = (screen_res[0]//2)-(self.mask_width//2)
		self.mask_y = self.bar_pos

		self.float_width = self.mask_width
		self.orig_mask_width = self.mask_width

		self.decay_rate = (self.mask_width/self.duration)

		###

		self.mask_group = GroupWithMask(self.mask_x,self.mask_y,self.mask_width,self.mask_height, parent=ordered_group2)

		img = pyglet.resource.image('p_b.png')
		bar_height = img.height//2
		bar_width = (img.width//2)
		l_cap_b_img = img.get_region(0,0,img.width//2,bar_height)
		self.l_cap_b = loaders.image_sprite_loader(l_cap_b_img, 
												   pos 						= (self.mask_x,self.mask_y),
												   batch 					= ui_batch,
												   group 					= ordered_group,
												   anchor 				    = (bar_width,0),
												   linear_interpolation 	= True)
		r_cap_b_img = img.get_region(bar_width+1,0,bar_width,bar_height)
		self.r_cap_b = loaders.image_sprite_loader(r_cap_b_img, 
												   pos 						= (self.mask_x+self.mask_group.width,self.mask_y),
												   batch 					= ui_batch,
												   group 					= ordered_group,
												   anchor 				    = (0,0),
												   linear_interpolation 	= True)

		b_meter = pyglet.image.Texture.create(self.mask_group.width,6)
		b_meter_img = img.get_region(bar_width,0,1,bar_height).get_image_data()
		offset = 0
		while offset <= self.mask_group.width:
			b_meter.blit_into(b_meter_img,offset,0,0)
			offset += 1
		self.b_meter = loaders.image_sprite_loader(b_meter, 
												   pos 						= (self.mask_x,self.mask_y),
												   batch 					= ui_batch,
												   group 					= ordered_group,
												   anchor 					= (0,0),
												   linear_interpolation 	= True)

		##

		l_cap_f_img = img.get_region(0,bar_height,bar_width,bar_height)
		self.l_cap_f = loaders.image_sprite_loader(l_cap_f_img, 
												   pos 						= (self.mask_x,self.mask_y),
												   batch 					= ui_batch,
												   group 					= ordered_group2,
												   anchor 				    = (bar_width,0),
												   linear_interpolation 	= True)
		r_cap_f_img = img.get_region(bar_width+1,bar_height,bar_width,bar_height)
		self.r_cap_f = loaders.image_sprite_loader(r_cap_f_img, 
												   pos 						= (self.mask_x+self.mask_group.width,self.mask_y),
												   batch 					= ui_batch,
												   group 					= ordered_group2,
												   anchor 				    = (0,0),
												   linear_interpolation 	= True)

		f_meter = pyglet.image.Texture.create(self.mask_group.width,6)
		f_meter_img = img.get_region(bar_width,bar_height,1,bar_height).get_image_data()
		offset = 0
		while offset <= self.mask_group.width:
			f_meter.blit_into(f_meter_img,offset,0,0)
			offset += 1
		self.f_meter = loaders.image_sprite_loader(f_meter, 
												   pos 						= (self.mask_x,self.mask_y),
												   batch 					= ui_batch,
												   group 					= self.mask_group,
												   anchor 					= (0,0),
												   linear_interpolation 	= True)

		self.sprite_list = [self.l_cap_b,self.r_cap_b,self.b_meter,
							self.l_cap_f,self.r_cap_f,self.f_meter]

		
	def update(self, player):
		distance = sqrt((player.chassis_body.position[0] - self.position[0])**2 + (player.chassis_body.position[1] - self.position[1])**2)
		if distance < 100:
			self.collected = True
		
		if self.collected:
			if self.duration >= 1:
				#print(self.pwr_type)
				self.do_action = True
				self.duration -= 1
			elif self.duration == 0:
				self.duration -= 1 # makes duration == -1 so this only fires once
				self.do_action = False
				self.action_done = False

			## Animate the bar
			if self.bar_pos < 5 and self.do_action:
				self.bar_pos += 1
				self.mask_group.y = self.bar_pos
				for sprite in self.sprite_list:
					sprite.y = self.bar_pos
		if not self.do_action:
			if self.bar_pos >= -5:
				self.bar_pos -= 1
				self.mask_group.y = self.bar_pos
				for sprite in self.sprite_list:
					sprite.y = self.bar_pos

		if self.do_action:
			if self.pwr_type == 'Gravity':
				self.space.gravity = self.grav_mod_dir
			elif self.pwr_type == 'Boost':
				self.player.accel_amount = self.accel_mod_amount

			if self.mask_group.width > 0: # animate the bar and mask
				self.float_width -= self.decay_rate
				self.mask_group.width = int(self.float_width)
				self.r_cap_f.x = self.mask_group.x+self.float_width

		# reset the powerup
		if not self.action_done:
			self.space.gravity = self.grav_finish_dir
			self.player.accel_amount = self.accel_finish_amount
			self.action_done = True
			self.collected = False
			# reset the bar anim
			self.duration = self.orig_dur
			self.mask_group.width = self.orig_mask_width
			self.float_width = self.orig_mask_width
			self.r_cap_f.x = self.mask_group.x+self.float_width
			print("Done.")

		#if player.point_query(self.position):
		#	self.collected = True