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
import particle
import loaders
import glob
import os
import shutil

class Button:
	def __init__(self, position, image, text, 
				 hover_image=None, 
				 padding=(0,0,0,0), 
				 action='No action.', 
				 camera_target=None,):
		#self.padding = padding
		self.position = position
		self.text = text
		self.action = action
		self.hover_image = hover_image

		self.sprite = loaders.spriteloader(image,
										   anchor = ('center','center'),
										   pos = position,
										   linear_interpolation = True)
		self.hover_sprite = loaders.spriteloader(hover_image,
										 		 placeholder = 'empty.png',
										 		 anchor = ('center','center'),
										 		 pos = position,
										 		 linear_interpolation = False)
		self.hover_sprite.visible = False

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
		self.hover_sprite.group = ordered_group2
		
		label = pyglet.text.Label(text = self.text,
								  font_name = 'Roboto',
								  italic = True,
								  font_size = 40, 
								  #bold = True,
								  width = self.sprite.width,
								  multiline = True,
								  align = 'center',
								  x = self.position[0], y = self.position[1], 
								  anchor_x = 'center', anchor_y = 'center',
								  color = (85,85,85,255),
								  batch = level_batch,
								  group = ordered_group3)
		'''=
		label2 = pyglet.text.Label(text = self.text,
								  font_name = 'RobotoRegular',
								  italic = True,
								  font_size = 41, 
								  bold = True,
								  width = self.sprite.width,
								  multiline = True,
								  align = 'center',
								  x = self.position[0], y = self.position[1], 
								  anchor_x = 'center', anchor_y = 'center',
								  color = (5,5,5,255),
								  batch = level_batch,
								  group = ordered_group2)
		'''
		if label.content_height > self.sprite.height:
			label.font_size = self.sprite.height / label.content_height * 38
		if label.content_width > self.sprite.width:
			label.font_size = self.sprite.width / label.content_width * 38
		'''
		if label2.content_height > self.sprite.height:
			label2.font_size = self.sprite.height / label2.content_height * 39
		if label2.content_width > self.sprite.width:
			label2.font_size = self.sprite.width / label2.content_width * 39
		'''
		if self.text == '':
			self.text = self.action
	def press(self, mouse_pos, button):
		self.bb_outline.colors = (self.color*4)
		if self.bb.contains_vect(mouse_pos):
			if button == 1:
				self.bb_outline.colors = (self.color3*4)
				print(self.text+" pressed!")

	def release(self, mouse_pos, button, camera_pos):
		if self.bb.contains_vect(mouse_pos):
			if button == 1:
				self.do_action = True
				if self.camera_target_x != None and self.camera_target_y != None:
					self.camera_move = True

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
			self.hover_sprite.visible = False

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