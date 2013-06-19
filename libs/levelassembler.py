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

def imageloader(image_file, placeholder, size):
	try:
		i = pyglet.resource.image(image_file)
		#i = i.get_region(0,0,i.width,i.height)
		#i.width = size[0]
		#i.height = size[1]
	except:
		print('Missing "'+str(image_file)+'." Replacing with "'+str(placeholder)+'."')
		i = pyglet.resource.image(placeholder)
		i = i.get_region(0,0,i.width,i.height)
		i.width = size[0]
		i.height = size[1]
	return i

class Game_Level:
	def __init__(self, map_zip, space, debug_batch, level_batch, ui_batch, 
				ordered_group_pbg, ordered_group_level, ordered_group_fg, ordered_group_fg3):
		self.debugBatch = debug_batch
		self.levelBatch = level_batch
		self.ordered_group_pbg = ordered_group_pbg
		self.ordered_group_level = ordered_group_level
		self.ordered_group_fg = ordered_group_fg
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
			if line.startswith("playerdetector"):
				#print(line)
				line = eval(line)
				self.detectors.append(line)
				continue

		self.space.add(self.map_segments)
		for line in self.map_segments:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
			self.stuff = self.debugBatch.add(2, pyglet.gl.GL_LINES, ordered_group_fg,
										('v2f/static', (p1[0],p1[1],p2[0],p2[1])),
										('c3B/static', (125,10,160,200,20,60)))
		#glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		if self.lowres == 'True':
			# adding 100px of padding to the parallax image.
			self.parallaxImage = imageloader('parallaxlow.png', 'placeholder.png', #empty is a 1x1 alpha png special testing case. change to placeholder.png 
											(self.mapWidth+100,self.mapHeight+100)) #.25
			self.parallaxImage_sprite = pyglet.sprite.Sprite(self.parallaxImage, batch = level_batch, group = ordered_group_pbg)
			self.parallaxImage_sprite.image.anchor_x = self.parallaxImage.width//2
			self.parallaxImage_sprite.image.anchor_y = self.parallaxImage.height//2

			self.levelImage = imageloader('levellow.png', 'placeholder.png', (4,4))
			self.levelImage_sprite = pyglet.sprite.Sprite(self.levelImage, batch = level_batch, group = ordered_group_level)
			self.levelImage_sprite.x = -25
			self.levelImage_sprite.y = -25
			leveltex = self.levelImage.get_texture()
			glTexParameteri(leveltex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		elif self.lowres == 'False':
			#glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			self.parallaxImage = imageloader('parallax.png', 'placeholder.png', (self.mapWidth, self.mapHeight))
			self.parallaxImage.width = self.parallaxImage.width//2
			self.parallaxImage.height = self.parallaxImage.height//2
			self.parallaxImage_sprite = pyglet.sprite.Sprite(self.parallaxImage, batch = level_batch, group = ordered_group_pbg)

			self.levelImage = imageloader('level.png', 'placeholder.png', (self.mapWidth, self.mapHeight))
			self.levelImage.width = self.levelImage.width//2
			self.levelImage.height = self.levelImage.height//2
			self.levelImage_sprite = pyglet.sprite.Sprite(self.levelImage, batch = level_batch, group = ordered_group_level)
			self.levelImage_sprite.x = -25
			self.levelImage_sprite.y = -25
		else:
			print("Error with boolean 'LowRes.' '"+str(self.lowres)+"' is not a correct value. LowRes must equal either 'True' or 'False.'")
	
			#leveltex = self.levelImage.get_texture()
			#glTexParameteri(leveltex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			#self.levelImage_sprite.scale = .5

		self.map_zip.close()

		for line in self.collectables:
			line.setup_pyglet_batch(level_batch, ui_batch, ordered_group_fg3)
		for line in self.boxes:
			line.setup_pyglet_batch(debug_batch, level_batch, ordered_group_fg)
		for line in self.mobis:
			line.setup_pyglet_batch(debug_batch, level_batch, ordered_group_fg)

		#self.levelScore = 0

	def update(self, player_pos, camera_offset, scale, keys_held):
		self.camera_offset = camera_offset
		self.scale = scale
		# iterating 50% of the camera movement, subtracting the initial 50% of the camera movement,
		# adding the image's width, and subtracting 1/2 of the padding
		self.parallaxImage_sprite.x = (self.camera_offset[0]*.5) - self.mapWidth//4 + self.parallaxImage.width//2 - 50
		self.parallaxImage_sprite.y = (self.camera_offset[1]*.5) - self.mapHeight//4 + self.parallaxImage.height//2 - 50
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