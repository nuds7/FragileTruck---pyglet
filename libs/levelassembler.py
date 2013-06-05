import pyglet
import pymunk
from pymunk import Vec2d
import configparser
import zipfile
import bridge
import jelly
import mobi
import box

def map_image_loader(map_zip, location, placeholder):
	location = location
	try:
		map_zip.extract(location, path = 'resources/temp')
	except:
		print('Failed to load %r' % location)
		location = placeholder
	return location



class Game_Level:
	def __init__(self, map_zip, space, debug_batch, level_batch, ordered_group_pbg, ordered_group_level, ordered_group_fg):
		self.debugBatch = debug_batch
		self.levelBatch = level_batch
		self.ordered_group_pbg = ordered_group_pbg
		self.ordered_group_level = ordered_group_level
		self.ordered_group_fg = ordered_group_fg
		################################ Map Config
		self.map_zip = zipfile.ZipFile(map_zip)
		self.map_config_file = self.map_zip.extract('map_config.cfg', path = 'temp')
		#print(self.map_zip.namelist())

		# Read the map's config
		self.mapConfig = configparser.RawConfigParser()
		self.mapConfig.read(self.map_config_file)
		self.mapName = self.mapConfig.get("MapConfig", "Name")
		self.mapWidth = int(self.mapConfig.get("MapConfig","Width"))
		self.mapHeight = int(self.mapConfig.get("MapConfig","Height"))
		self.start_Position_X = int(self.mapConfig.get("MapConfig", "Player_Start_Position_X"))
		self.start_Position_Y = int(self.mapConfig.get("MapConfig", "Player_Start_Position_Y"))
		print("Name: "+self.mapName)
		print("Map size: "+str(self.mapWidth)+", "+str(self.mapHeight))
		print("Starting Position: "+str(self.start_Position_X),str(self.start_Position_Y))
		# Unzip failsafe placeholder image.
		self.placeholderImage = 'images/placeholder.png'
		self.map_zip.extract(self.placeholderImage, path = 'resources/temp')
		pyglet.resource.reindex()

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

		##
		self.levelImage = map_image_loader(self.map_zip, str(self.mapConfig.get("Images", "LevelImage")), self.placeholderImage)
		##
		self.parallaxImage = map_image_loader(self.map_zip, str(self.mapConfig.get("Images", "ParallaxImage")), self.placeholderImage)
		##
		self.bridgeImage = map_image_loader(self.map_zip, str(self.mapConfig.get("Images", "BridgeImage")), self.placeholderImage)
		##
		self.crateImage = map_image_loader(self.map_zip, str(self.mapConfig.get("Images", "CrateImage")), self.placeholderImage)
		##
		self.elevatorImage = map_image_loader(self.map_zip, str(self.mapConfig.get("Images", "ElevatorImage")), self.placeholderImage)

		pyglet.resource.reindex()
		##


		################################ End Map Config

		################################ Adding Static Lines
		self.map_file = self.map_zip.extract('map_layout.map', path = 'temp')
		self.map_file = open(self.map_file)

		self.space = space
		static_body = pymunk.Body()
		dirt_body = pymunk.Body()

		self.map_segments = [] # creates a list to hold segments contained in map file
		self.elevators = []
		self.bridges = []
		self.jellies = []
		self.mobis = []
		self.boxes = []
		self.detectors = []
		self.space = space

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

		self.parallaxImage = pyglet.resource.image(self.parallaxImage)
		self.parallaxImage_sprite = pyglet.sprite.Sprite(self.parallaxImage, batch = level_batch, group = ordered_group_pbg)
		self.parallaxImage_sprite.scale = .5

		self.levelImage = pyglet.resource.image(self.levelImage)
		self.levelImage_sprite = pyglet.sprite.Sprite(self.levelImage, batch = level_batch, group = ordered_group_level)
		self.levelImage_sprite.x = -25
		self.levelImage_sprite.y = -25
		self.levelImage_sprite.scale = .5

		self.map_zip.close()


	def update(self, player_pos, camera_offset):
		self.camera_offset = camera_offset
		self.parallaxImage_sprite.x = self.camera_offset[0] * -.2 + 400
		self.parallaxImage_sprite.y = self.camera_offset[1] * -.2 + 120
		for line in self.bridges:
			line.draw()
		for line in self.jellies:
			line.draw()
		for line in self.mobis:
			line.draw(player_pos)
		for line in self.boxes:
			line.draw()
	def mobi_activate(self, player_pos):
		for line in self.mobis:
			line.activate(player_pos)
	def mobi_deactivate(self, player_pos):
		for line in self.mobis:
			line.deactivate(player_pos)
	def remove(self):
		for line in self.boxes:
			line.remove()