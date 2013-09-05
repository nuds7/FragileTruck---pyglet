import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import configparser
import zipfile
import bridge
import mobi
import box
from box import Boxes
from random import randrange,uniform
import time
import collectable
import trigger
import loaders
import glob
import os
import shutil

class State_Button:
	def __init__(self, 
				 position, 
				 image,
				 padding=(0,0,0,0), 
				 action='No action', 
				 camera_target=None,
				 physical=False,
				 physical_padding=(0,0)):
		#self.padding = padding
		self.position = position
		self.padding = padding
		self.action = action
		self.physical = physical

		image = pyglet.resource.image(image)
		
		normal_image 	= image.get_region(0,	image.height*2//3,	image.width,	image.height*1//3)
		hover_image 	= image.get_region(0,	image.height*1//3,	image.width,	image.height*1//3)
		press_image 	= image.get_region(0,	0,					image.width,	image.height*1//3)

		self.box_size = normal_image.width+physical_padding[0], normal_image.height+physical_padding[1]
		self.sprite = loaders.image_sprite_loader(normal_image,
														anchor = ('center','center'),
														pos = position,
														linear_interpolation = True)
		self.hover_sprite = loaders.image_sprite_loader(hover_image,
														placeholder = 'empty.png',
														anchor = ('center','center'),
														pos = position,
														linear_interpolation = True)
		self.hover_sprite.visible = False
		self.press_sprite = loaders.image_sprite_loader(press_image,
														placeholder = 'empty.png',
														anchor = ('center','center'),
														pos = position,
														linear_interpolation = True)
		self.press_sprite.visible = False

		
		alpha = 255
		self.color = (200,0,0,alpha)
		self.color2 = (0,200,0,alpha)
		self.color3 = (200,200,0,alpha)

		self.clicked = False

		if camera_target != None:
			self.camera_target_x = camera_target[0]
			self.camera_target_y = camera_target[1]
		else:
			self.camera_target_x = None
			self.camera_target_y = None
		self.camera_move = False
		self.do_action = False
		self.pressed = False
		
	def setup_pyglet_batch(self, debug_batch, level_batch, ordered_group, ordered_group2, ordered_group3):
		self.debug_batch 		= debug_batch
		self.ordered_group3 	= ordered_group3

		self.padding_left 		= self.sprite.image.width//2  + self.padding[0]
		self.padding_bottom 	= self.sprite.image.height//2 + self.padding[1]
		self.padding_right 		= self.sprite.image.width//2  + self.padding[2]
		self.padding_top 		= self.sprite.image.height//2 + self.padding[3]

		self.left 	= (self.position[0] - self.padding_left,  self.position[1] + self.padding_top)
		self.bottom = (self.position[0] - self.padding_left,  self.position[1] - self.padding_bottom)
		self.right 	= (self.position[0] + self.padding_right, self.position[1] - self.padding_bottom)
		self.top 	= (self.position[0] + self.padding_right, self.position[1] + self.padding_top)

		self.bb = pymunk.BB(self.position[0] - self.padding_left, #- hinge_pos[0], # left
							self.position[1] - self.padding_bottom, #  - hinge_pos[1], # bottom
							self.position[0] + self.padding_right, # - hinge_pos[0], # right
							self.position[1] + self.padding_top) # - hinge_pos[1]) # top

		self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
		self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group3, [0,1,1,2,2,3,3,0], 
											('v2f', (self.left[0],self.left[1],
													 self.bottom[0],self.bottom[1],
													 self.right[0],self.right[1],
													 self.top[0],self.top[1])),
											('c4B', (0,0,0,0)*4))
		
		self.sprite.batch 	= level_batch
		self.sprite.group 	= ordered_group
		
		self.hover_sprite.batch = level_batch
		self.hover_sprite.group = ordered_group

		self.press_sprite.batch = level_batch
		self.press_sprite.group = ordered_group
	def press(self, mouse_pos, button):
		self.bb_outline.colors = (self.color*4)
		if self.bb.contains_vect(mouse_pos):
			if button == 1:
				print('honk')
				self.bb_outline.colors = (self.color3*4)
				self.press_sprite.visible = True
				self.sprite.visible = False
				self.hover_sprite.visible = False
				self.pressed = True
				print(self.action+" pressed!")
		else:
			self.pressed = False
			self.sprite.visible = True
			self.press_sprite.visible = False

	def release(self, mouse_pos, button, camera_pos):
		if self.bb.contains_vect(mouse_pos):
			self.hover_sprite.visible = True
			self.press_sprite.visible = False
			if button == 1:
				if self.pressed:
					self.do_action = True
					if self.camera_target_x != None and self.camera_target_y != None:
						self.camera_move = True
		else:
			self.do_action = False
			self.sprite.visible = True
			self.press_sprite.visible = False

		if self.camera_target_x != None and self.camera_target_y != None:
			if abs(camera_pos[0]-self.camera_target_x) < 500 and \
			   abs(camera_pos[0]-self.camera_target_x) < 500:
				self.camera_move = False

		if self.do_action and self.action == 'exit':
				print('Button action: %s. Purseging temp folder and exiting.' % (self.action))
				shutil.rmtree('temp')
				pyglet.app.exit()
				self.do_action = False
			
	def hover(self, mouse_pos):
		self.bb_outline.colors = (self.color*4)
		if self.bb.contains_vect(mouse_pos):
			self.bb_outline.colors = (self.color2*4)
			self.sprite.visible = False
			self.hover_sprite.visible = True
			if self.pressed:
				self.press_sprite.visible = False
		elif not self.bb.contains_vect(mouse_pos): 
			self.sprite.visible = True
			self.press_sprite.visible = False
			self.hover_sprite.visible = False

	def physical_box(self, space):
		if self.physical:
			body = pymunk.Body()
			body.position = (self.position)
			shape = pymunk.Poly.create_box(body, self.box_size)
			shape.friction = .1
			space.add(shape)

	def scroll(self, y):
		self.sprite.y 		= self.sprite.y      	+ y
		self.hover_sprite.y = self.hover_sprite.y 	+ y
		self.press_sprite.y = self.press_sprite.y 	+ y

	def update_bb(self):
		self.bb = pymunk.BB(self.sprite.x - self.padding_left,
							self.sprite.y - self.padding_bottom,
							self.sprite.x + self.padding_right,
							self.sprite.y + self.padding_top)

		self.left 	= (self.sprite.x - self.padding_left,  self.sprite.y + self.padding_top)
		self.bottom = (self.sprite.x - self.padding_left,  self.sprite.y - self.padding_bottom)
		self.right 	= (self.sprite.x + self.padding_right, self.sprite.y - self.padding_bottom)
		self.top 	= (self.sprite.x + self.padding_right, self.sprite.y + self.padding_top)

		self.bb_outline.vertices = (self.left[0],self.left[1],
									self.bottom[0],self.bottom[1],
									self.right[0],self.right[1],
									self.top[0],self.top[1])


class Scrollable_Button:
	def __init__(self, 
				 position, 
				 image,
				 padding=(0,0,0,0), 
				 action='No action', 
				 camera_target=None,
				 physical=False):
		#self.padding = padding
		self.position = position
		self.action = action
		self.physical = physical

		image = pyglet.resource.image(image)
		
		normal_image 	= image.get_region(0,	image.height*2//3,	image.width,	image.height*1//3)
		hover_image 	= image.get_region(0,	image.height*1//3,	image.width,	image.height*1//3)
		press_image 	= image.get_region(0,	0,					image.width,	image.height*1//3)

		self.box_size = normal_image.width,normal_image.height
		'''
		normal_image 	= image.get_region(0,74,103,37)
		hover_image 	= image.get_region(0,37,103,37)
		press_image 	= image.get_region(0,0,103,37)
		'''
		self.sprite = loaders.image_sprite_loader(normal_image,
														anchor = ('center','center'),
														pos = position,
														linear_interpolation = True)
		self.hover_sprite = loaders.image_sprite_loader(hover_image,
														placeholder = 'empty.png',
														anchor = ('center','center'),
														pos = position,
														linear_interpolation = True)
		self.hover_sprite.visible = False
		self.press_sprite = loaders.image_sprite_loader(press_image,
														placeholder = 'empty.png',
														anchor = ('center','center'),
														pos = position,
														linear_interpolation = True)
		self.press_sprite.visible = False

		padding_left = self.sprite.image.width//2 + padding[0]
		padding_bottom = self.sprite.image.height//2 + padding[1]
		padding_right = self.sprite.image.width//2 + padding[2]
		padding_top = self.sprite.image.height//2 + padding[3]

		self.left = (position[0] - padding_left, position[1] + padding_top)
		self.bottom = (position[0] - padding_left, position[1]- padding_bottom)
		self.right = (position[0] + padding_right, position[1]- padding_bottom)
		self.top = (position[0] + padding_right, position[1] + padding_top)

		self.bb = pymunk.BB(position[0] - padding_left, #- hinge_pos[0], # left
							position[1] - padding_bottom, #  - hinge_pos[1], # bottom
							position[0] + padding_right, # - hinge_pos[0], # right
							position[1] + padding_top) # - hinge_pos[1]) # top
		alpha = 255
		self.color = (200,0,0,alpha)
		self.color2 = (0,200,0,alpha)
		self.color3 = (200,200,0,alpha)

		self.clicked = False

		if camera_target != None:
			self.camera_target_x = camera_target[0]
			self.camera_target_y = camera_target[1]
		else:
			self.camera_target_x = None
			self.camera_target_y = None
		self.camera_move = False
		self.do_action = False
		self.pressed = False
		self.n_scroll = 0
		
	def setup_pyglet_batch(self, debug_batch, level_batch, ordered_group, ordered_group2, ordered_group3):
		self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
		self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
											('v2f', (self.left[0],self.left[1],
													 self.bottom[0],self.bottom[1],
													 self.right[0],self.right[1],
													 self.top[0],self.top[1])),
											('c4B', (0,0,0,0)*4))
		
		self.sprite.batch 	= level_batch
		self.sprite.group 	= ordered_group
		
		self.hover_sprite.batch = level_batch
		self.hover_sprite.group = ordered_group

		self.press_sprite.batch = level_batch
		self.press_sprite.group = ordered_group
	def press(self, mouse_pos, button):
		self.bb_outline.colors = (self.color*4)
		if self.bb.contains_vect(mouse_pos):
			if button == 1:
				self.bb_outline.colors = (self.color3*4)
				self.press_sprite.visible = True
				self.sprite.visible = False
				self.hover_sprite.visible = False
				self.pressed = True
				print(self.action+" pressed!")
		else:
			self.pressed = False
			self.sprite.visible = True
			self.press_sprite.visible = False

	def release(self, mouse_pos, button, camera_pos):
		if self.bb.contains_vect(mouse_pos):
			if button == 1:
				if self.pressed:
					self.do_action = True
					if self.camera_target_x != None and self.camera_target_y != None:
						self.camera_move = True
		else:
			self.do_action = False
			self.sprite.visible = True
			self.press_sprite.visible = False

		if self.camera_target_x != None and self.camera_target_y != None:
			if abs(camera_pos[0]-self.camera_target_x) < 500 and \
			   abs(camera_pos[0]-self.camera_target_x) < 500:
				self.camera_move = False

		if self.do_action and self.action == 'exit':
				print('Button action: %s. Purging temp folder and exiting.' % (self.action))
				shutil.rmtree('temp')
				pyglet.app.exit()
				self.do_action = False
			
	def hover(self, mouse_pos):
		self.bb_outline.colors = (self.color*4)
		if self.bb.contains_vect(mouse_pos):
			self.bb_outline.colors = (self.color2*4)
			self.sprite.visible = False
			self.hover_sprite.visible = True
		elif not self.bb.contains_vect(mouse_pos): 
			self.sprite.visible = True
			self.press_sprite.visible = False
			self.hover_sprite.visible = False

class Scrollable(object):
	def __init__(self, 
				 debug_batch, 
				 level_batch, 
				 ordered_group, 
				 ordered_group2, 
				 ordered_group3,
				 position, 
				 width, 
				 height, 
				 level_list, 
				 padding=(0,0,0,0)):
		self.position = position
		self.width 	= width
		self.height = height

		padding_left 	= 	width 	+ padding[0]
		padding_bottom 	= 	height 	+ padding[1]
		padding_right 	= 	width 	+ padding[2]
		padding_top 	=   height 	+ padding[3]

		self.left = (position[0] - padding_left, position[1] + padding_top)
		self.bottom = (position[0] - padding_left, position[1]- padding_bottom)
		self.right = (position[0] + padding_right, position[1]- padding_bottom)
		self.top = (position[0] + padding_right, position[1] + padding_top)

		self.bb = pymunk.BB(position[0] - padding_left,
							position[1] - padding_bottom,
							position[0] + padding_right,
							position[1] + padding_top)

		self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
											('v2f', (self.left[0],self.left[1],
													 self.bottom[0],self.bottom[1],
													 self.right[0],self.right[1],
													 self.top[0],self.top[1])),
											('c4B', (0,0,0,0)*4))
		alpha = 255
		self.color = (200,0,0,alpha)
		self.color2 = (0,200,0,alpha)
		self.color3 = (200,200,0,alpha)

		self.buttons = []
		b_space = 0
		for item in level_list:
			button = Scrollable_Button((position[0],position[1]+height-20+b_space), 
									   'back.png',)
			button.setup_pyglet_batch(debug_batch, level_batch, ordered_group, ordered_group2, ordered_group3)
			self.buttons.append(button)
			b_space -= button.sprite.height + 5

		self.contains = False
		self.n_scroll = 0
		self.scrolled = 0
	def scroll(self, scroll):
		if self.contains:
			self.n_scroll = scroll*10
			
	def update(self):
		self.n_scroll = ((self.n_scroll*(20-1))+(0)) / 20
		for button in self.buttons:
			
			button.sprite.y += self.n_scroll
			button.hover_sprite.y += self.n_scroll
			button.press_sprite.y += self.n_scroll

			padding_left = button.sprite.image.width//2
			padding_bottom = button.sprite.image.height//2
			padding_right = button.sprite.image.width//2
			padding_top = button.sprite.image.height//2
	
			self.left = (button.sprite.x - padding_left, button.sprite.y + padding_top)
			self.bottom = (button.sprite.x - padding_left, button.sprite.y- padding_bottom)
			self.right = (button.sprite.x + padding_right, button.sprite.y- padding_bottom)
			self.top = (button.sprite.x + padding_right, button.sprite.y + padding_top)
	
			button.bb = pymunk.BB(button.sprite.x - padding_left,
								  button.sprite.y - padding_bottom,
								  button.sprite.x + padding_right,
								  button.sprite.y + padding_top)
		
			button.bb_outline.vertices = (self.left[0],self.left[1],
												 self.bottom[0],self.bottom[1],
												 self.right[0],self.right[1],
												 self.top[0],self.top[1])

	def hover(self, mouse_pos):
		self.bb_outline.colors = (self.color*4)
		if self.bb.contains_vect(mouse_pos):
			self.contains = True
			self.bb_outline.colors = (self.color2*4)
		elif not self.bb.contains_vect(mouse_pos): 
			self.contains = False
			pass

'''
class ScrollableGroup(pyglet.graphics.Group):
	"""
	We restrict what's shown within a Scrollable by performing a scissor
	test.
	"""
	def __init__(self, x, y, width, height, parent=None):
		"""Create a new ScrollableGroup

		@param x X coordinate of lower left corner
		@param y Y coordinate of lower left corner
		@param width Width of scissored region
		@param height Height of scissored region
		@param parent Parent group
		"""
		pyglet.graphics.Group.__init__(self, parent)
		self.x, self.y, self.width, self.height = x, y, width, height
		self.was_scissor_enabled = False

	def set_state(self):
		"""
		Enables a scissor test on our region
		"""
		gl.glPushAttrib(gl.GL_ENABLE_BIT | gl.GL_TRANSFORM_BIT |
						gl.GL_CURRENT_BIT)
		self.was_scissor_enabled = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
		gl.glEnable(gl.GL_SCISSOR_TEST)
		gl.glScissor(int(self.x), int(self.y),
					 int(self.width), int(self.height))

	def unset_state(self):
		"""
		Disables the scissor test
		"""
		if not self.was_scissor_enabled:
			gl.glDisable(gl.GL_SCISSOR_TEST)
		gl.glPopAttrib()
'''
'''
class ProgressBar(object):
	def __init__(self,
				 total,
				 position=(0,0),
				 image=None,
				 batch=None,
				 group1=None,
				 group2=None):
		bg_bar 	= image.get_region(0,0,7,6)
		pr_bar 	= image.get_region(0,6,7,6)
		bg_l 	= bg_bar.get_region(0,0,3,6)
		bg_r 	= bg_bar.get_region(0,4,3,6)
		bg_m	= bg_bar.get_region(3,0,1,6)
		pr_l 	= pr_bar.get_region(0,0,3,6)
		pr_r 	= pr_bar.get_region(0,4,3,6)
		pr_m	= pr_bar.get_region(3,0,1,6)
		tip		= image.get_region(7,0,21,14)

		##
		self.bg_s_l = loaders.image_sprite_loader(bg_l,
												  anchor = (0,'center'),
												  pos = position,
												  batch = batch,
												  group = group1,
												  linear_interpolation = True)
		self.bg_s_r = loaders.image_sprite_loader(bg_r,
												  anchor = (0,'center'),
												  pos = (position[0]+294,position[1]),
												  batch = batch,
												  group = group1,
												  linear_interpolation = True)
		bg_m_sprites = []
		self.pr_m_sprites = []
		for i in range(294):
			bg_m_sprites.append(
				loaders.image_sprite_loader(bg_m,
											anchor = (0,'center'),
											pos = (position[0]+i+bg_l.width,position[1]),
											batch = batch,
											group = group2,
											linear_interpolation = True))
		for i in range(22):
			self.pr_m_sprites.append(
				loaders.image_sprite_loader(pr_m,
											anchor = (0,'center'),
											pos = (position[0]+i+bg_l.width,position[1]),
											batch = batch,
											group = group2,
											linear_interpolation = True))

		self.pos = position
		self.total = total
		##
	
	def update(self, current):
		p = current//self.total
		self.pr_m_sprites[current].set_position(self.pos[0]+current,self.pos[1])
		print(current)
		return p
'''

'''
class Game_Menu:
	def __init__(self, map_zip, space, screen_res, debug_batch, background_batch, level_batch, ui_batch, 
				ordered_group_bg, 
				ordered_group_pbg, 
				ordered_group_pbg2, 
				ordered_group_pbg3,
				ordered_group_pbg4,
				ordered_group_lbg, 
				ordered_group_lfg, 
				ordered_group_lfg2, 
				ordered_group_lfg3):
		self.debugBatch = debug_batch
		self.levelBatch = level_batch
		self.ordered_group_bg = ordered_group_bg
		self.ordered_group_pbg = ordered_group_pbg
		self.ordered_group_lbg = ordered_group_lbg
		self.ordered_group_lfg = ordered_group_lfg
		self.ordered_group_lfg2 = ordered_group_lfg2
		self.ordered_group_lfg3 = ordered_group_lfg3

		################################ Map Config
		self.map_zip = zipfile.ZipFile(map_zip)
		#self.map_config_file = self.map_zip.extract('map_config.cfg', path = 'temp')
		self.map_zip.extractall('resources/temp')
		pyglet.resource.reindex()
		#print(self.map_zip.namelist())

		# Read the map's config
		self.mapConfig = configparser.RawConfigParser()
		self.mapConfig.read('resources/temp/map_config.cfg')
		self.mapName = self.mapConfig.get("MapConfig", "Name")
		self.mapWidth = int(self.mapConfig.get("MapConfig","Width"))
		self.mapHeight = int(self.mapConfig.get("MapConfig","Height"))
		self.cameraStartX = int(self.mapConfig.get("MapConfig", "cameraStartX"))
		self.cameraStartY = int(self.mapConfig.get("MapConfig", "cameraStartY"))
		#self.lowres = str(self.mapConfig.get("MapConfig", "LowRes"))
		print("Name: "+self.mapName)
		print("Map size: "+str(self.mapWidth)+", "+str(self.mapHeight))
		#print("Starting Position: "+str(self.start_Position_X),str(self.start_Position_Y))
		#print("LowRes: "+str(self.lowres))
		# Unzip failsafe placeholder image.
		# Unzip map specific images.
		# Tell pyglet to reindex its searchable paths
		# without pyglet.resource.reindex(), the program
		# will crash because self.resource.image() does not
		# know that a new bg.png/pbg.png or whatever image
		# has emerged in the path. Pyglet only indexed its
		# searchable paths when the program started so
		# as far as pyglet knows, resources/temp is (was) empty.
		# Now that I extracted the images to the path resources/temp,
		# resources/temp is not empty. That is why we reindex with 
		# pyglet.resource.reindex after every time we unzip an image.


		################################ End Map Config

		################################ Adding Static Lines
		self.map_file = open('resources/temp/map_layout.map')
		self.space = space
		self.screen_res = screen_res
		static_body = pymunk.Body()
		dirt_body = pymunk.Body()

		self.map_segments = [] # creates a list to hold segments contained in map file
		#self.elevators = []
		#self.bridges = []
		#self.jellies = []
		#self.mobis = []
		#self.boxes = []
		#self.collectables = []
		#self.detectors = []
		#self.triggers = []
		self.buttons = []

		for line in self.map_file:
			line = line.strip() # refer to http://programarcadegames.com/index.php?chapter=searching
			#print(line)
			if line == "": continue # skip blank lines
			if line.startswith("#"): continue # skip comments

			#====================================#
			if line.startswith("pymunk.Segment"): # Add static segments and objects first
				line = eval(line) # converts string to an object ('segment' -> <segment>)
				#print(line)
				line.friction = .5
				
				line.group = 2
				if line.body == dirt_body:
					line.collision_type = 2
				else: line.collision_type = 3
				self.map_segments.append(line)
				continue
			if line.startswith("Button"):
				#print(line)
				line = eval(line)
				self.buttons.append(line)
				continue

		self.map_zip.close()

		self.space.add(self.map_segments)
		for line in self.map_segments:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
			self.stuff = self.debugBatch.add(2, pyglet.gl.GL_LINES, ordered_group_lfg,
										('v2f/static', (p1[0],p1[1],p2[0],p2[1])),
										('c3B/static', (125,10,160,200,20,60)))

		
		
		levels = [l for l in os.listdir('levels/') if l.endswith('.zip')]
		#print(levels)
		self.level_boxes = []
		iter_num = 0
		for level in levels:
			level_box = Boxes(self.space, ((self.mapWidth//2)+uniform(-5,5),self.mapHeight+200+uniform(-5,5)), 
									(128,128), .5, .5, 1, (0,0), 
									level.replace('.zip', '.png'), 
									menu_box = True,
									placeholder = 'preview_placeholder.png', 
									scale = 1,
									point_query = True,
									name = level)
			self.level_boxes.append(level_box)
			iter_num += 1

		for line in self.buttons:
			line.setup_pyglet_batch(debug_batch, level_batch, ordered_group_lfg, ordered_group_lfg2, ordered_group_lfg3)
		for box in self.level_boxes:
			box.setup_pyglet_batch(debug_batch, level_batch, ordered_group_lfg, ordered_group2 = ordered_group_lfg2)

		self.background = loaders.spriteloader('menu_bg.png', 
												anchor=(4,4),
												#size = (100,100),
												batch=level_batch,
												group=ordered_group_bg,
												linear_interpolation=True)

		self.mouse_pos = [0,0]
		self.buttons_pressed = 0
		self.emitter_L = particle.SimpleEmitter('menu_streamer.png', level_batch,  
												#stretch = (80,8), 
												ordered_group = ordered_group_lbg,
												#rainbow_mode = True, 
												max_active = 80,
												random_scale = True,
												fade_out = True)


	def update(self):
		self.camera_offset = camera_offset
		self.scale = scale

		for line in self.buttons:
			line.update(self.mouse_pos, self.buttons_pressed, camera_offset)
		
		for box in self.level_boxes:
			box.draw()
			box.mouse_pos = self.mouse_pos
			box.mouse_buttons = self.buttons_pressed
		if self.buttons_pressed != 0:
			self.buttons_pressed = 0
		self.emitter_L.emit(1, (300,360), 
								(0,0), [(-1,1),(-1,1)], (-2,2), 180)
		self.emitter_L.update()
'''