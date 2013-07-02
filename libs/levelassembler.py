import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import configparser
import zipfile
import bridge
import jelly
import mobi
import box
import time
import collectable
import trigger
import particle
import loaders

def imageloader(image_file, placeholder, size=None, stretch=None):
	try:
		i = pyglet.resource.image(image_file)
		#print(i)
		#i = i.get_region(0,0,i.width,i.height)
		if stretch == None: pass
		else:
			i.width = stretch[0]
			i.height = stretch[1]
	except:
		print('Missing "'+str(image_file)+'." Replacing with "'+str(placeholder)+'."')
		i = pyglet.resource.image(placeholder)
		i = i.get_region(0,0,i.width,i.height)
		i.width = size[0]
		i.height = size[1]
	return i
'''
def spriteloader(image_file, 
				placeholder = 'placeholder.png',
				anchor, 
				size, 
				batch = None, 
				group = None, 
				linear_intrpolation=False,):
	try:
		image = pyglet.resource.image(image_file)
	except:
		image = pyglet.resource.image(placeholder)
	sprite = pyglet.sprite.Sprite(image, batch = batch, group = group)

	if size != None:
		sprite.image.width = size[0]
		sprite.image.height = size[1]

	if anchor[0] == 'center':
		sprite.image.anchor_x = image.width//2
	if anchor[1] == 'center':
		sprite.image.anchor_y = image.height//2
	if anchor[0] == 'top':
		sprite.image.anchor_x = image.width
	if anchor[1] == 'right':
		sprite.image.anchor_y = image.height

	if linear_intrpolation:
		tex = self.parallaxImage.get_texture()
		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
	return sprite
'''
class Game_Level:
	def __init__(self, map_zip, space, screen_res, debug_batch, background_batch, level_batch, ui_batch, 
				ordered_group_bg, 
				ordered_group_pbg, 
				ordered_group_pbg2, 
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
		self.start_Position_X = int(self.mapConfig.get("MapConfig", "Player_Start_Position_X"))
		self.start_Position_Y = int(self.mapConfig.get("MapConfig", "Player_Start_Position_Y"))
		self.lowres = str(self.mapConfig.get("MapConfig", "LowRes"))
		print("Name: "+self.mapName)
		print("Map size: "+str(self.mapWidth)+", "+str(self.mapHeight))
		print("Starting Position: "+str(self.start_Position_X),str(self.start_Position_Y))
		print("LowRes: "+str(self.lowres))
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

		self.map_zip.close()

		self.space.add(self.map_segments)
		for line in self.map_segments:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
			self.stuff = self.debugBatch.add(2, pyglet.gl.GL_LINES, ordered_group_lfg,
										('v2f/static', (p1[0],p1[1],p2[0],p2[1])),
										('c3B/static', (125,10,160,200,20,60)))
		

		if self.lowres == 'True':
			self.level_sprite 		= loaders.spriteloader('levellow.png', 
															anchor=(25,25),
															batch=level_batch,
															group=ordered_group_lbg,
															linear_intrpolation=True)
			self.parallax_sprite_1 	= loaders.spriteloader('parallaxlow1.png', 
														  	anchor=('center','center'),
														  	batch=level_batch,
														  	group=ordered_group_pbg2,
														  	linear_intrpolation=True)
			self.parallax_sprite_1.y = self.mapHeight/2 
			self.parallax_sprite_2 	= loaders.spriteloader('parallaxlow2.png', 
														  	anchor=('center',50),
														  	batch=level_batch,
														  	group=ordered_group_pbg,
														  	linear_intrpolation=True)


		self.background = loaders.spriteloader('bg.png', 
											  	anchor=('center','center'),
											  	#size = (100,100),
											  	batch=level_batch,
											  	group=ordered_group_bg,
											  	linear_intrpolation=True)

		for line in self.collectables:
			line.setup_pyglet_batch(level_batch, ui_batch, ordered_group_lfg3)
		for line in self.boxes:
			line.setup_pyglet_batch(debug_batch, level_batch, ordered_group_lfg)
		for line in self.bridges:
			line.setup_pyglet_batch(debug_batch, level_batch, ordered_group_lfg)
		for line in self.mobis:
			line.setup_pyglet_batch(debug_batch, level_batch, ordered_group_lfg2)

		for line in self.triggers:
			line.setup_pyglet_batch(debug_batch, level_batch, ui_batch, ordered_group_lfg3, screen_res)

		#self.levelScore = 0

	def update(self, player_pos, angle, camera_offset, scale, keys_held):
		self.camera_offset = camera_offset
		self.scale = scale
		
		self.parallax_sprite_2.x = self.mapWidth/2 + (self.camera_offset[0]*.25) - self.mapWidth/8 #- self.mapWidth/4 

		self.background.scale = scale[0]/(self.screen_res[0]/2)
		self.background.x = self.camera_offset[0]
		self.background.y = self.camera_offset[1]
		
		self.parallax_sprite_1.x = self.mapWidth/2 + (self.camera_offset[0]*.5) - self.mapWidth/4 
		#self.parallax_sprite_1.y = self.mapHeight/2 +(self.camera_offset[1]*.5) - self.mapHeight/4

		for line in self.bridges:
			line.draw()
		for line in self.jellies:
			line.draw()
		for line in self.mobis:
			line.update(player_pos, keys_held)
		for line in self.boxes:
			line.draw()
		for line in self.collectables:
			index = self.collectables.index(line)
			line.update(player_pos, index*(line.image.width*.66))
		for line in self.triggers:
			line.update(player_pos, angle)
	def remove(self):
		for line in self.boxes:
			line.remove()
'''
	def mobi_activate(self, player_pos):
		for line in self.mobis:
			line.activate(player_pos)
	def mobi_deactivate(self, player_pos):
		for line in self.mobis:
			line.deactivate(player_pos)
'''