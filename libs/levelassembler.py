import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import configparser
import zipfile
import player
import bridge
import jelly
import mobi
import box
from box import Boxes
import time
import collectable
import trigger
import particle
import loaders
import camera
import os,sys
from random import randrange,uniform
from menu import Button
import math
from math import sin,cos

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
		self.map_zip = zipfile.ZipFile(map_zip)
		self.map_zip.extractall('resources/temp')
		pyglet.resource.reindex()
		self.map_zip.close()
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
		################################ End Map Config

		################################ 
		self.map_file = open('resources/temp/map_layout.map')
		static_body = pymunk.Body()
		dirt_body = pymunk.Body()

		self.map_segments = [] # creates a list to hold segments contained in map file
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
		self.space.add(self.map_segments)
		for line in self.map_segments:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
			self.stuff = self.debug_batch.add(2, pyglet.gl.GL_LINES, self.lfg,
										('v2f/static', (p1[0],p1[1],p2[0],p2[1])),
										('c3B/static', (125,10,160,200,20,60)))

		levels = [l for l in os.listdir('levels/') if l.endswith('.zip')]
		#print(levels)
		self.level_boxes = []
		iter_num = 0
		for level in levels:
			level_box = Boxes(self.space, ((self.mapWidth//2)+uniform(-5,5),self.mapHeight+200+uniform(-5,5)), 
									(128,128), 0.01, .5, 1, (0,0), 
									level.replace('.zip', '.png'), 
									menu_box = True,
									placeholder = 'preview_placeholder.png', 
									scale = 1,
									point_query = True,
									name = level)
			self.level_boxes.append(level_box)
			iter_num += 1

		for line in self.buttons:
			line.setup_pyglet_batch(self.debug_batch, self.level_batch, self.lfg, self.lfg2, self.lfg3)
		for box in self.level_boxes:
			box.setup_pyglet_batch(self.debug_batch, self.level_batch, self.lfg, ordered_group2 = self.lfg2)

		self.background = loaders.spriteloader('menu_bg.png', 
											  	anchor=(4,4),
											  	#size = (100,100),
											  	batch=self.level_batch,
											  	group=self.bg,
											  	linear_interpolation=True)
		self.emitter_L = particle.SimpleEmitter('menu_streamer.png', self.level_batch,  
                                                #stretch = (80,8), 
                                                ordered_group = self.lbg,
                                                #rainbow_mode = True, 
                                                max_active = 80,
                                                random_scale = True,
                                                fade_out = True)

		self.level_selected = ''
		self.cameraPosX = self.cameraStartX
		self.cameraPosY = self.cameraStartY

	def update(self):
		for box in self.level_boxes:
			box.draw()
		for button in self.buttons:
			if button.do_action and button.action == 'exit':
				pyglet.app.exit()
		self.emitter_L.emit(1, (300,360), 
                                (0,0), [(-1,1),(-1,1)], (-2,2), 180)
		self.emitter_L.update()

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

		self.space = space
		self.screen_res = screen_res
		self.map_zip = zipfile.ZipFile(map_zip)
		self.map_zip.extractall('resources/temp')
		pyglet.resource.reindex()
		self.map_zip.close()
		# Read the map's config
		self.mapConfig          = configparser.RawConfigParser()
		self.mapConfig.read('resources/temp/map_config.cfg')
		self.mapName            = self.mapConfig.get("MapConfig", "Name")
		self.mapAuthor          = self.mapConfig.get("MapConfig", "Author")
		self.mapWidth           = int(self.mapConfig.get("MapConfig","Width"))
		self.mapHeight          = int(self.mapConfig.get("MapConfig","Height"))
		self.playerType         = str(self.mapConfig.get("MapConfig", "Player_Type"))
		self.start_Position_X   = int(self.mapConfig.get("MapConfig", "Player_Start_Position_X"))
		self.start_Position_Y   = int(self.mapConfig.get("MapConfig", "Player_Start_Position_Y"))
		self.start_Position     = self.start_Position_X,self.start_Position_Y
		self.lowres             = str(self.mapConfig.get("MapConfig", "LowRes"))
		print("Name: "+self.mapName+"by "+self.mapAuthor)
		print("Map size: "+str(self.mapWidth)+", "+str(self.mapHeight))
		print("Player Type: "+self.playerType)
		print("Starting Position: "+str(self.start_Position_X),str(self.start_Position_Y))
		print("LowRes: "+str(self.lowres))
		################################ End Map Config
		self.map_file = open('resources/temp/map_layout.map')
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
		self.space.add(self.map_segments)
		for line in self.map_segments:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
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

		if self.lowres == 'True':
			self.background 		= loaders.spriteloader('bg.png', 
															anchor=('center','center'),
															pos = (self.mapWidth/2,self.mapHeight/2),
															batch=self.level_batch,
															group=self.bg,
															linear_interpolation=True)
			self.parallax_sprite_1  = loaders.spriteloader('bottom.png', 
															anchor=('center','center'),
															pos = (0,self.mapHeight/2),
															batch=self.level_batch,
															group=self.pbg,
															linear_interpolation=True)
			self.parallax_sprite_2  = loaders.spriteloader('middle.png', 
															anchor=('center','center'),
															pos = (self.mapWidth/2,self.mapHeight/2),
															batch=self.level_batch,
															group=self.pbg2,
															linear_interpolation=True)
			self.parallax_sprite_3  = loaders.spriteloader('clouds.png', 
															anchor=('center','center'),
															pos = (0,self.mapHeight/2),
															batch=self.level_batch,
															group=self.pbg3,
															linear_interpolation=True)
			self.parallax_sprite_4  = loaders.spriteloader('top.png', 
															anchor=('center','center'),
															pos = (0,self.mapHeight/2),
															batch=self.level_batch,
															group=self.pbg4,
															linear_interpolation=True)
			self.level_sprite       = loaders.spriteloader('level.png', 
															anchor=('center','center'),
															pos = (self.mapWidth/2,self.mapHeight/2),
															batch=self.level_batch,
															group=self.lbg,
															linear_interpolation=True)

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
			self.player = player.Truck(self.space, 
										self.start_Position, 
										self.level_batch, 
										self.lfg, 
										self.lfg2, 
										self.lfg3)
		if self.playerType == 'None' or editor_mode == True:
			self.player = None

	def update(self, keys_held, target_pos, camera_pos, angle):
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

		self.parallax_sprite_1.x = (camera_pos[0]*-.125) 	+ (self.mapWidth/2)*.125	+ self.mapWidth/2
		self.parallax_sprite_3.x = (camera_pos[0]*.125) 	- (self.mapWidth/2)*.125 	+ self.mapWidth/2
		self.parallax_sprite_4.x = (camera_pos[0]*.5) 		- (self.mapWidth/2)*.5		+ self.mapWidth/2

		self.parallax_sprite_1.y = (camera_pos[1]*-.1) 		+ (self.mapHeight/2)*.1		+ self.mapHeight/2
		self.parallax_sprite_3.y = (camera_pos[1]*.1) 		- (self.mapHeight/2)*.1 	+ self.mapHeight/2
		self.parallax_sprite_4.y = (camera_pos[1]*.1) 		- (self.mapHeight/2)*.1		+ self.mapHeight/2