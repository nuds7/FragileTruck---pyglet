import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import configparser
import zipfile
import player
import playernew
import bridge
import mobi
import box
from box import Boxes
import time
import collectable
import trigger
import particle
import loaders
import camera
import os,sys,shutil
from random import randrange,uniform
import menu
from menu import State_Button
import math
from math import sin,cos
import gametime
import particles2D
import time
import powerup
from tiler import BackgroundTiler

class Menu(object):
	def __init__(self, 
					map_zip,
					space,
					screen_res,
					debug_batch,
					background_batch,
					level_batch,
					ui_batch,
					lfg3,
					lfg2,
					lfg,
					lbg,
					pbg4,
					pbg3,
					pbg2,
					pbg,
					bg):
		self.debug_batch 		= debug_batch
		self.background_batch 	= background_batch
		self.level_batch 		= level_batch
		self.ui_batch 			= ui_batch
		self.lfg3 				= lfg3
		self.lfg2 				= lfg2
		self.lfg 				= lfg
		self.lbg 				= lbg
		self.pbg4				= pbg4
		self.pbg3				= pbg3
		self.pbg2 				= pbg2
		self.pbg 				= pbg
		self.bg 				= bg

		
		self.space = space
		self.screen_res = screen_res
		self.aspect = screen_res[0]/screen_res[1]
		self.map_zip = zipfile.ZipFile(map_zip, mode='r')
		#self.map_zip.extractall('resources/temp')
		self.map_zip.extract('map_config.cfg', path = 'temp')
		self.map_zip.extract('map_layout.map', path = 'temp')
		self.map_zip.close()

		pyglet.resource.path.append(map_zip)
		pyglet.resource.reindex()

		self.mapConfig 		= configparser.ConfigParser()
		self.mapConfig.read('temp/map_config.cfg')
		self.mapName 		= self.mapConfig.get("MapConfig", "Name")
		self.mapWidth 		= screen_res[0]*3
		self.mapHeight 		= screen_res[1]
		self.cameraHomeX 	= screen_res[0]/2
		self.cameraHomeY 	= screen_res[1]/2
		print("Name: "+self.mapName)
		print("Map size: "+str(self.mapWidth)+", "+str(self.mapHeight))
		################################

		################################ 
		static_body = pymunk.Body()
		dirt_body = pymunk.Body()
		self.map_segments = []
		self.buttons = []
		self.sprites = []

		self.map_file = open('temp/map_layout.map')

		for line in self.map_file:
			if line == "": continue
			if line.startswith("#"): continue

			#====================================#
			if line.startswith("pymunk.Segment"):
				line = eval(line)
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
			if line.startswith("State_Button"):
				#print(line)
				line = eval(line)
				line.physical_box(self.space)
				self.buttons.append(line)
				continue
			if line.startswith("loaders.spriteloader"):
				line = eval(line)
				self.sprites.append(line)
				continue
		self.map_file.close()

		self.space.add(self.map_segments)
		for line in self.map_segments:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
			self.stuff = self.debug_batch.add(2, pyglet.gl.GL_LINES, self.lfg,
										('v2f/static', (p1[0],p1[1],p2[0],p2[1])),
										('c3B/static', (125,10,160,200,20,60)))

		levels = [l for l in os.listdir('levels/') if l.endswith('.zip')]
		self.level_boxes = []
		iter_num = 0
		for level in levels:
			pyglet.resource.path.append('levels/'+level)
			pyglet.resource.reindex()
			level_box = Boxes(self.space, ((self.mapWidth//2)+uniform(-5,5),self.mapHeight+200+uniform(-5,5)), 
							  (128,128), 0.01, .5, 1, (0,0), 
							  'images/preview.png', # level.replace('.zip', '.png'), 
							  menu_box = True,
							  placeholder = 'preview_placeholder.png', 
							  scale = 1,
							  point_query = True,
							  name = level)
			self.level_boxes.append(level_box)
			pyglet.resource.path.pop(-1)
			iter_num += 1

		for line in self.buttons:
			line.setup_pyglet_batch(self.debug_batch, self.level_batch, self.lfg, self.lfg2, self.lfg3)
		for box in self.level_boxes:
			box.setup_pyglet_batch(self.debug_batch, self.level_batch, self.lfg, ordered_group2 = self.lfg2)

		pyglet.resource.reindex()

		self.emitter = particles2D.Emitter(pos=(self.screen_res[0]*2/3,self.mapHeight/2), 
										   max_num = 200)
		img = pyglet.resource.image('spark.png')

		self.emitter.add_factory(particles2D.spark_machine(580,
			                                               img,
			                                               batch=self.level_batch,
			                                               group=self.bg),
														   pre_fill = 100)

		
		pyglet.resource.path.pop(-1)
		pyglet.resource.reindex()

		self.level_selected = ''
		

	def update(self):
		#self.st.update()

		for box in self.level_boxes:
			box.draw()

		self.emitter.update()
		self.emitter.draw()


class Level(object):
	def __init__(self, 
					map_zip,
					space,
					screen_res,
					debug_batch,
					background_batch,
					level_batch,
					ui_batch,
					lfg3,
					lfg2,
					lfg,
					lbg,
					pbg4,
					pbg3,
					pbg2,
					pbg,
					bg,
					editor_mode = False):
		self.debug_batch 		= debug_batch
		self.background_batch 	= background_batch
		self.level_batch 		= level_batch
		self.ui_batch 			= ui_batch
		self.lfg3 				= lfg3
		self.lfg2 				= lfg2
		self.lfg 				= lfg
		self.lbg 				= lbg
		self.pbg4				= pbg4
		self.pbg3				= pbg3
		self.pbg2 				= pbg2
		self.pbg 				= pbg
		self.bg 				= bg
		self.editor_mode 		= editor_mode

		self.space = space
		self.screen_res = screen_res
		self.map_zip = zipfile.ZipFile(map_zip)

		self.map_zip.extract('map_config.cfg', path = 'temp')
		self.map_zip.extract('map_layout.map', path = 'temp')
		self.map_zip.close()

		self.mapConfig          = configparser.ConfigParser()
		self.mapConfig.read('temp/map_config.cfg')
		self.mapName            = self.mapConfig.get("MapConfig", "Name")
		self.mapAuthor          = self.mapConfig.get("MapConfig", "Author")
		self.mapWidth           = self.mapConfig.getint("MapConfig","Width")
		self.mapHeight          = self.mapConfig.getint("MapConfig","Height")
		self.playerType         = str(self.mapConfig.get("MapConfig", "Player_Type"))
		self.start_Position_X   = self.mapConfig.getint("MapConfig", "Player_Start_Position_X")
		self.start_Position_Y   = self.mapConfig.getint("MapConfig", "Player_Start_Position_Y")
		self.start_Position     = self.start_Position_X,self.start_Position_Y
		self.tile_size          = int(self.mapConfig.get("MapConfig", "Tile_Size"))
		print("Name: "+self.mapName+"by "+self.mapAuthor)
		print("Map size: "+str(self.mapWidth)+", "+str(self.mapHeight))
		print("Player Type: "+self.playerType)
		print("Starting Position: "+str(self.start_Position_X),str(self.start_Position_Y))
		print("Tile size: "+str(self.tile_size))
		################################ End Map Config
		self.map_file = open('temp/map_layout.map')
		self.screen_res = screen_res
		self.aspect = screen_res[0]/screen_res[1]
		static_body = pymunk.Body()
		dirt_body = pymunk.Body()

		self.map_segments = [] # creates a list to hold segments contained in map file
		self.elevators = []
		self.bridges = []
		self.jellies = []
		self.mobis = []
		self.boxes = []
		self.collectables = []
		self.detectors = []
		self.triggers = []
		self.powerups = []

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
			if line.startswith("elevator"):
				#print(line)
				line = eval(line)
				self.elevators.append(line)
				continue
			if line.startswith("bridge"):
				#print(line)
				line = eval(line)
				self.bridges.append(line)
				continue
			if line.startswith("jelly"):
				#print(line)
				line = eval(line)
				self.jellies.append(line)
				continue
			if line.startswith("mobi"):
				#print(line)
				line = eval(line)
				self.mobis.append(line)
				continue
			if line.startswith("box.Boxes"):
				#print(line)
				line = eval(line)
				self.boxes.append(line)
				continue
			if line.startswith("collectable.Collectable"):
				line = eval(line)
				self.collectables.append(line)
				continue
			if line.startswith("trigger"):
				line = eval(line)
				self.triggers.append(line)
				continue
			if line.startswith("playerdetector"):
				#print(line)
				line = eval(line)
				self.detectors.append(line)
				continue
			if line.startswith("powerup"):
				#print(line)
				line = eval(line)
				self.powerups.append(line)
				continue
		self.map_file.close()

		self.space.add(self.map_segments)
		for line in self.map_segments:
			p1 = line.a 
			p2 = line.b 
			self.stuff = self.debug_batch.add(2, pyglet.gl.GL_LINES, self.lfg,
										('v2f/static', (p1[0],p1[1],p2[0],p2[1])),
										('c3B/static', (125,10,160,200,20,60)))
		for line in self.collectables:
			line.setup_pyglet_batch(self.level_batch, self.ui_batch, self.lfg3)
		for line in self.boxes:
			line.setup_pyglet_batch(self.debug_batch, self.level_batch, self.lfg)
		for line in self.bridges:
			line.setup_pyglet_batch(self.debug_batch, self.level_batch, self.lfg)
		for line in self.mobis:
			line.setup_pyglet_batch(self.debug_batch, self.level_batch, self.lfg2)
		for line in self.triggers:
			line.setup_pyglet_batch(self.debug_batch, self.level_batch, self.ui_batch, self.lfg3, screen_res)

		'''
		Alright, in case if I forget. What I'm about to do is temporarly add 
		the map's zip file to the resource path and directly load the zip's
		contained images. That way I do not have to extract everything from 
		within the zip every time I want to load the map's images. This should
		not only help with speed, but make everything relatively cleaner. But
		since each image is within a subdirectory within the zip file, I have
		to navigate to that directory directly by putting 'images/' before
		the image. Once I'm done loading all of that, I pop the zip from the
		resource module's searchable path.
		'''

		pyglet.resource.path.append(map_zip)
		pyglet.resource.reindex()
		'''
		self.background 		= loaders.spriteloader('images/bg.png', 
														anchor=('center','center'),
														pos = (self.mapWidth/2,self.mapHeight/2),
														batch=self.level_batch,
														group=self.bg,
														linear_interpolation=hiRes
														)
		self.parallax_sprite_1  = loaders.spriteloader('images/bottom.png', 
														anchor=('center','center'),
														pos = (self.mapWidth/2,self.mapHeight/2),#pos = (0,self.mapHeight/2),
														batch=self.level_batch,
														group=self.pbg,
														linear_interpolation=hiRes
														)
		self.parallax_sprite_2  = loaders.spriteloader('images/middle.png', 
														anchor=('center','center'),
														pos = (self.mapWidth/2,self.mapHeight/2),
														batch=self.level_batch,
														group=self.pbg2,
														linear_interpolation=hiRes
														)
		self.parallax_sprite_3  = loaders.spriteloader('images/clouds.png', 
														anchor=('center','center'),
														pos = (self.mapWidth/2,self.mapHeight/2),#pos = (0,self.mapHeight/2),
														batch=self.level_batch,
														group=self.pbg3,
														linear_interpolation=hiRes
														)
		self.parallax_sprite_4  = loaders.spriteloader('images/top.png', 
														anchor=('center','center'),
														pos = (self.mapWidth/2,self.mapHeight/2),
														batch=self.level_batch,
														group=self.pbg4,
														linear_interpolation=hiRes
														)
		self.level_sprite       = loaders.spriteloader('images/level.png', 
														anchor=('center','center'),
														pos = (self.mapWidth/2,self.mapHeight/2),
														batch=self.level_batch,
														group=self.lbg,
														linear_interpolation=hiRes
														)
		'''

		self.bg_tiled = BackgroundTiler('images/bg.png', scale=.5, tile_size = self.tile_size)
		self.bg_tiled.setup(self.level_batch, self.bg, (self.mapWidth,self.mapHeight))

		self.bottom_tiled = BackgroundTiler('images/bottom.png', scale=.5, tile_size = self.tile_size)
		self.bottom_tiled.setup(self.level_batch, self.pbg, (self.mapWidth,self.mapHeight))

		self.middle_tiled = BackgroundTiler('images/middle.png', scale=.5, tile_size = self.tile_size)
		self.middle_tiled.setup(self.level_batch, self.pbg2, (self.mapWidth,self.mapHeight))

		#self.top_tiled = BackgroundTiler('images/top.png', scale=.5, tile_size = self.tile_size)
		#self.top_tiled.setup(self.level_batch, self.pbg4, (self.mapWidth,self.mapHeight))

		self.level_tiled = BackgroundTiler('images/level.png', scale=.5, tile_size = self.tile_size)
		self.level_tiled.setup(self.level_batch, self.lbg, (self.mapWidth,self.mapHeight))

		pyglet.resource.path.pop(-1)
		pyglet.resource.reindex()

		self.level_name 		= pyglet.text.Label(text = self.mapName,
													font_name = 'Calibri', font_size = 8, bold = True,
													x = 1, y = screen_res[1]+2,
													anchor_x = 'left', anchor_y = 'top',
													color = (0,0,0,200),
													batch = self.ui_batch)
		self.level_author_name 	= pyglet.text.Label(text = ' by '+self.mapAuthor,
													font_name = 'Calibri', font_size = 8, bold = True,
													x = self.level_name.content_width+1, y = screen_res[1]+2,
													anchor_x = 'left', anchor_y = 'top',
													color = (0,0,0,120),
													batch = self.ui_batch)
		self.level_name.set_style('background_color', (255,255,255,80))
		self.level_author_name.set_style('background_color', (255,255,255,80))

		if self.playerType == 'Truck':
			self.player = playernew.Truck(self.space, 
										(self.start_Position), 
										self.level_batch, 
										self.debug_batch,
										self.ui_batch,
										self.lfg, 
										self.lfg2, 
										self.lfg3)
		if self.playerType == 'None' or editor_mode == True:
			self.player = None

		for line in self.powerups:
			line.setup_modifiers(self.player, self.space)
			line.setup_pyglet_batch(self.level_batch, self.ui_batch, 
									self.lfg, self.lfg2, lfg3, 
									self.screen_res, 
									ordered_group_bg=self.lbg)

		if not editor_mode:
			self.gt = gametime.GameTime()
			self.time_ui 	= loaders.spriteloader('time_ui.png', 
											anchor=(0,0),
											pos = (5,5),
											batch=self.ui_batch,
											group=self.lfg,
											linear_interpolation=True)
			self.time_label = pyglet.text.Label(text = '00:00:00',
											font_name = 'Calibri', font_size = 11, bold = True, italic = True,
											x = 50, y = 5,
											anchor_x = 'left', anchor_y = 'bottom',
											color = (255,255,255,255),
											batch = self.ui_batch,
											group = self.lfg3)

		self.powerup_queue = powerup.PowerUpQueue()
		self.active_powerups = []
		self.space_step_rate = 0.015

	def update(self, keys_held, target_pos, camera_pos, camera_scale, angle):

		self.level_tiled.pop(camera_pos, camera_scale)
		self.bg_tiled.pop(camera_pos, camera_scale)
		
		self.bottom_tiled.parallax_scroll((camera_pos[0]*.25) - (self.mapWidth/2)*.25, 
										 (camera_pos[1]*.25) - (self.mapHeight/2)*.25)
		self.bottom_tiled.pop(camera_pos, camera_scale)
		
		self.middle_tiled.parallax_scroll((camera_pos[0]*.125) - (self.mapWidth/2)*.125, 
										 (camera_pos[1]*.125) - (self.mapHeight/2)*.125)
		self.middle_tiled.pop(camera_pos, camera_scale)

		if not self.editor_mode:
			self.time_label.text = self.gt.tick()

		if self.player != None:
			self.player.update()
			self.player.controls(keys_held)

		for line in self.bridges:
			line.draw()
		for line in self.jellies:
			line.draw()
		for line in self.mobis:
			line.update(target_pos, keys_held)
		for line in self.boxes:
			line.draw()
		for line in self.collectables:
			index = self.collectables.index(line)
			line.update(target_pos, index*(line.image.width*.66))
		for line in self.triggers:
			line.update(target_pos, angle)

		for line in self.powerups:
			line.update(self.player)
			if line.do_action and not line.placed_in_queue:
				line.placed_in_queue = True
				self.active_powerups.append(line)
				# Set the step rate of the powerup
				# AKA the space's update rate
				if self.active_powerups[-1].pwr_type == 'SlowMo':
					self.space_step_rate = self.active_powerups[-1].space_step_rate

		for p in self.active_powerups:
			if not p.do_action:
				p.placed_in_queue = False
				self.active_powerups.remove(p)
				if p.pwr_type == 'SlowMo':
					self.space_step_rate = p.space_step_rate
			
		#print(self.active_powerups)

		self.powerup_queue.update(self.active_powerups)
		'''
		self.parallax_sprite_1.x = (camera_pos[0]*.25) 	 	- (self.mapWidth/2)*.25	+ self.mapWidth/2
		self.parallax_sprite_2.x = (camera_pos[0]*.125)  	- (self.mapWidth/2)*.125   + self.mapWidth/2
		'''
		#self.parallax_sprite_1.y = (camera_pos[1]*.1)   	- (self.mapHeight/2)*.1  	+ self.mapHeight/2
		#self.parallax_sprite_2.y = (camera_pos[1]*.05)  	- (self.mapHeight/2)*.05 	+ self.mapHeight/2

		##
		#self.parallax_sprite_1.x = (camera_pos[0]*-.125) 	+ (self.mapWidth/2)*.125	+ self.mapWidth/2
		#self.parallax_sprite_3.x = (camera_pos[0]*.125) 	- (self.mapWidth/2)*.125 	+ self.mapWidth/2
		#self.parallax_sprite_4.x = (camera_pos[0]*.5) 		- (self.mapWidth/2)*.5		+ self.mapWidth/2
		##
		#self.parallax_sprite_1.y = (camera_pos[1]*-.1) 	+ (self.mapHeight/2)*.1		+ self.mapHeight/2
		#self.parallax_sprite_3.y = (camera_pos[1]*.1) 		- (self.mapHeight/2)*.1 	+ self.mapHeight/2
		#self.parallax_sprite_4.y = (camera_pos[1]*.1) 		- (self.mapHeight/2)*.1		+ self.mapHeight/2