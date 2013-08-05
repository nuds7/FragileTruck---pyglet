import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
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
	def __init__(self, 
				 position, 
				 image_file,
				 bar_blend=(0,0,0),
				 pwr_type='None', 
				 grav_mod_dir=(0,0), grav_finish_dir=(0,-800), 
				 accel_mod_amount=0, accel_finish_amount=4,
				 duration=0,
				 activation_dist=75,
				 *args,**kwargs):

		self.bar_blend 			 = bar_blend
		self.position 			 = position
		self.pwr_type			 = pwr_type
		self.grav_mod_dir 		 = grav_mod_dir
		self.grav_finish_dir 	 = grav_finish_dir
		self.accel_mod_amount 	 = accel_mod_amount
		self.accel_finish_amount = accel_finish_amount
		self.duration 			 = duration
		self.activation_dist 	 = activation_dist

		self.orig_dur = self.duration

		self.sprite = loaders.spriteloader(image_file, 
										   pos 					= position,
										   anchor 				= ('center','center'),
										   scale 				= .5,
										   linear_interpolation = False
										   )
		if pwr_type=='Gravity':
			self.sprite.rotation = -Vec2d(grav_mod_dir).get_angle_degrees()+90

		self.sprite.ui_set = False

		self.collected = False
		self.do_action = False
		self.action_done = True
		
	def setup_modifiers(self, player, space):
		self.player 	= player
		self.space 		= space

	def setup_pyglet_batch(self, level_batch, ui_batch, ordered_group, ordered_group2, screen_res):
		self.ui_batch = ui_batch
		self.sprite.batch = level_batch
		self.sprite.group = ordered_group
		self.screen_res = screen_res

		self.queue_pos = 10

		self.bar_pos = -5

		self.mask_width = 500
		self.mask_height = 10
		self.mask_x = (screen_res[0]//2)-(self.mask_width//2)
		self.mask_y = self.bar_pos

		self.float_width = self.mask_width
		self.orig_mask_width = self.mask_width

		self.decay_rate = (self.mask_width/self.duration)

		###

		img = pyglet.resource.image('p_b.png')
		bar_height = img.height//2
		bar_width = (img.width//2)

		self.mask_group = GroupWithMask(self.mask_x,self.mask_y,
										self.mask_width,bar_height, 
										parent=ordered_group2)
		
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

		b_meter = pyglet.image.Texture.create(self.mask_group.width,bar_height)
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

		f_meter = pyglet.image.Texture.create(self.mask_group.width,bar_height)
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

		if self.bar_blend != (0,0,0):
			self.l_cap_f.color,self.r_cap_f.color,self.f_meter.color = self.bar_blend,self.bar_blend,self.bar_blend

		self.sprite_list = [self.l_cap_b,self.r_cap_b,self.b_meter,
							self.l_cap_f,self.r_cap_f,self.f_meter]


		self.power_label = pyglet.text.Label(text = self.pwr_type,
											 font_name = 'Calibri', font_size = 8, bold = True,
											 x = self.mask_x-self.l_cap_b.image.width+2, y = self.mask_y+16, 
											 anchor_x = 'left', anchor_y = 'center',
											 color = (255,255,255,200),
											 batch = ui_batch,
											 group=ordered_group2)

		self.power_label_shadow = pyglet.text.Label(text = self.pwr_type,
											 		font_name = 'Calibri', font_size = 8, bold = True,
											 		x = self.mask_x-self.l_cap_b.image.width+2, y = self.mask_y+16, 
											 		anchor_x = 'left', anchor_y = 'center',
											 		color = (25,25,25,200),
											 		batch = ui_batch,
											 		group=ordered_group)
				
	def update(self, player):
		distance = sqrt((player.chassis_body.position[0] - self.position[0])**2 + (player.chassis_body.position[1] - self.position[1])**2)

		if distance < self.activation_dist:
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
			if self.bar_pos <= self.queue_pos and self.do_action:
				self.bar_pos += 1
		if not self.do_action:
			if self.bar_pos > -self.queue_pos-10:
				self.bar_pos -= 1
				self.mask_group.width += 2
			else:
				self.mask_group.width = self.orig_mask_width
		##

		if self.do_action:
			if self.pwr_type == 'Gravity':
				self.space.gravity = self.grav_mod_dir
			elif self.pwr_type == 'Boost':
				self.player.accel_amount = self.accel_mod_amount

			if self.mask_group.width > 0: # animate the bar and mask
				self.float_width -= self.decay_rate
				self.mask_group.width = int(self.float_width)

		# reset the powerup
		if not self.action_done:
			self.action_done = True
			self.collected = False
			if self.pwr_type == 'Gravity':
				self.space.gravity = self.grav_finish_dir
			elif self.pwr_type == 'Boost':
				self.player.accel_amount = self.accel_finish_amount
			self.duration = self.orig_dur
			self.float_width = self.orig_mask_width # reset the mask width
			self.sprite.scale = 1.5
			print("Done.")

		self.r_cap_f.x = self.mask_group.x+self.mask_group.width
		for sprite in self.sprite_list:
			sprite.y = self.bar_pos
		self.power_label.y = self.bar_pos+13
		self.power_label_shadow.y = self.bar_pos+12
		self.mask_group.y = self.bar_pos

		if self.collected:
			if self.sprite.opacity >= 15:
				self.sprite.scale -= .05
				self.sprite.opacity -= 15

		if not self.collected:
			if self.sprite.opacity <= 250:
				self.sprite.opacity += 5
			if self.sprite.scale > .5:
				self.sprite.scale -= .025
			else:
				self.sprite.scale = .5

		#if player.point_query(self.position):
		#	self.collected = True