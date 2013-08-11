import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
from math import sqrt,sin,cos,atan2
from random import uniform
import loaders
import copy
import PiTweener

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
				 rot_pwr_img=False,
				 blend_img=(255,255,255),
				 blend_bar=(255,255,255),
				 pwr_type='None', 
				 grav_mod_dir=(0,-800), grav_fin_dir=(0,-800), 
				 accel_mod_amount=4, accel_fin_amount=4,
				 dur=0,
				 activ_dist=75,
				 *args,**kwargs):
		self.rot_pwr_img 		 = rot_pwr_img
		self.bar_blend 			 = blend_bar
		self.position 			 = position
		self.pwr_type			 = pwr_type
		self.grav_mod_dir 		 = grav_mod_dir
		self.grav_finish_dir 	 = grav_fin_dir
		self.accel_mod_amount 	 = accel_mod_amount
		self.accel_finish_amount = accel_fin_amount
		self.duration 			 = dur
		self.activation_dist 	 = activ_dist

		self.orig_dur = self.duration

		self.sprite = loaders.spriteloader(image_file, 
										   pos 					= position,
										   anchor 				= ('center','center'),
										   scale 				= .5,
										   linear_interpolation = False)
		self.sprite.color = blend_img
		if rot_pwr_img:
			self.sprite.rotation = -Vec2d(grav_mod_dir).get_angle_degrees()+90

		self.sprite_grav_rotation = -Vec2d(grav_mod_dir).get_angle_degrees()+90

		self.collected = False
		self.do_action = False
		self.action_done = True

		self.bar_pos = -30

		self.sprite_opacity = 255
		self.sprite_scale = .5
		self.sprite_rotation = self.sprite_grav_rotation

		self.placed_in_queue = False
		self.modded = False
		

		self.scale_tweener = PiTweener.Tweener()
		self.tween_added = False
		
	def setup_modifiers(self, player, space):
		self.player 	= player
		self.space 		= space

	def setup_pyglet_batch(self, level_batch, ui_batch, ordered_group, ordered_group2, ordered_group3, screen_res, ordered_group_bg=None):
		self.ui_batch = ui_batch
		self.sprite.batch = level_batch
		self.sprite.group = ordered_group3
		self.screen_res = screen_res


		self.mask_width = 200
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

		if self.bar_blend != (255,255,255):
			self.l_cap_f.color,self.r_cap_f.color,self.f_meter.color = self.bar_blend,self.bar_blend,self.bar_blend

		self.sprite_list = [self.l_cap_b,self.r_cap_b,self.b_meter,
							self.l_cap_f,self.r_cap_f,self.f_meter]


		self.power_label = pyglet.text.Label(text = self.pwr_type,
											 font_name = 'Calibri', font_size = 8, bold = True,
											 x = screen_res[0]//2, y = self.mask_y+16, 
											 anchor_x = 'center', anchor_y = 'center',
											 color = (255,255,255,255),
											 batch = ui_batch,
											 group=ordered_group2)

		self.power_label_shadow = pyglet.text.Label(text = self.pwr_type,
											 		font_name = 'Calibri', font_size = 8, bold = True,
											 		x = screen_res[0]//2, y = self.mask_y+16, 
											 		anchor_x = 'center', anchor_y = 'center',
											 		color = (0,0,0,240),
											 		batch = ui_batch,
											 		group=ordered_group)

		self.background_sprite = loaders.spriteloader('progress_bar_container.png', 
								  					  pos 						= (screen_res[0]//2,-20),
								  					  anchor 					= ('center','center'),
								  					  batch 					= ui_batch,
								  					  group 					= ordered_group_bg,
								  					  linear_interpolation 	=	 True)

		self.smooth = 0

		self.a = 1
				
	def update(self, player):

		if player==None:
			pass
		else:
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
	
			if self.do_action:
				if self.pwr_type == 'Gravity':
					self.space.gravity = self.grav_mod_dir
				elif self.pwr_type == 'Boost':
					self.player.accel_amount = self.accel_mod_amount
				if self.mask_group.width > 0: # animate the bar and mask
					self.float_width -= self.decay_rate
					self.mask_group.width = int(self.float_width)
			if not self.do_action:
				if self.smooth >= -25:
					self.bar_pos = -30
					self.a = ((self.a*(20-1))+self.mask_width) / 20
					self.mask_group.width = int(self.a)
				else:
					self.a = 1
					self.mask_group.width = self.orig_mask_width
	
			# reset the powerup
			if not self.action_done:
				self.action_done = True
				self.collected = False
				self.duration = self.orig_dur
				self.float_width = self.orig_mask_width # reset the mask width
				# Reset the mods
				if self.pwr_type == 'Gravity':
					self.space.gravity = self.grav_finish_dir
				elif self.pwr_type == 'Boost':
					self.player.accel_amount = self.accel_finish_amount
				print("Done.")
	
			self.r_cap_f.x = self.mask_group.x+self.mask_group.width
			self.smooth = ((self.smooth*(15-1))+self.bar_pos) / 15
			for sprite in self.sprite_list:
				sprite.y 				= int(self.smooth) + 2
			self.mask_group.y 			= int(self.smooth) + 2
			self.power_label.y 			= int(self.smooth) + 16
			self.power_label_shadow.y 	= int(self.smooth) + 15
			self.background_sprite.y 	= int(self.smooth) + 10

			if self.collected:
				self.background_sprite.color = (255,255,255)
			if self.duration <= 125 and self.duration > 100:
				self.background_sprite.color = (255,0,0)
			if self.duration <= 100 and self.duration > 75:
				self.background_sprite.color = (255,255,255)
			if self.duration <= 75 and self.duration > 50:
				self.background_sprite.color = (255,0,0)
			if self.duration <= 50 and self.duration > 25:
				self.background_sprite.color = (255,255,255)
			if self.duration <= 25:
				self.background_sprite.color = (255,0,0)

			if self.collected:
				if not self.tween_added:
					self.scale_tweener.add_tween(self,
									 sprite_scale 			= 1,
									 tween_time 			= 1.5,
									 tween_type 			= self.scale_tweener.OUT_ELASTIC,
									 on_update_function 	= self.tween_update,
									 on_complete_function 	= self.tween_complete)
					self.scale_tweener.add_tween(self,
									 sprite_opacity 		= 0,
									 tween_time 			= 1.5,
									 tween_type 			= self.scale_tweener.IN_OUT_QUART,
									 on_update_function 	= self.tween_update,
									 on_complete_function 	= self.tween_complete)
					self.tween_added = True

			if not self.collected:
				if self.tween_added:
					self.sprite_scale = .001
					self.sprite_rotation = 0
					self.scale_tweener.add_tween(self,
									 			 sprite_scale 			= 0.5,
									 			 tween_time 			= 3,
									 			 tween_type 			= self.scale_tweener.OUT_ELASTIC,
									 			 on_update_function 	= self.tween_update,
									 			 on_complete_function 	= self.tween_complete)
					self.scale_tweener.add_tween(self,
												 sprite_rotation 		= self.sprite_grav_rotation,
												 tween_time 			= 3,
												 tween_type 			= self.scale_tweener.OUT_ELASTIC,
												 on_update_function 	= self.tween_update,
												 on_complete_function 	= self.tween_complete)
					self.scale_tweener.add_tween(self,
												 sprite_opacity 		= 255,
												 tween_time 			= .5,
												 tween_type 			= self.scale_tweener.IN_OUT_QUART,
												 on_update_function 	= self.tween_update,
												 on_complete_function 	= self.tween_complete)
					self.tween_added = False
				

			self.scale_tweener.update()
			self.sprite.scale 	= self.sprite_scale
			self.sprite.opacity = self.sprite_opacity
			if self.rot_pwr_img:
				self.sprite.rotation = self.sprite_rotation

	def tween_update(self):
		pass
	def tween_complete(self):
		pass
	def sprite_scale_update(self):
		pass
	def sprite_scale_finish(self):
		pass
		

class PowerUpQueue(object):
	def __init__(self):
		pass
	def update(self, list_of_powerups):
		amount = len(list_of_powerups)
		i_num = 0
		if amount > 0:
			for p in list_of_powerups:
				if p==list_of_powerups[-1]:
					p.bar_pos=12
				else:
					p.bar_pos=12+36*((amount-1)-i_num)
				i_num+=1