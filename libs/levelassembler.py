import pyglet
import pymunk
from pymunk import Vec2d
import configparser
import zipfile
import bridge
import jelly
import mobi
import box

class Game_Level:
	def __init__(self, map_zip, space, batch, ordered_group_pbg, ordered_group_bg, ordered_group_fg):
		self.batch = batch
		self.ordered_group_pbg = ordered_group_pbg
		self.ordered_group_bg = ordered_group_bg
		self.ordered_group_fg = ordered_group_fg
		################################ Map Config
		self.map_zip = zipfile.ZipFile(map_zip)
		self.map_config_file = self.map_zip.extract('map_config.cfg', path = 'temp')
		print(self.map_zip.namelist())

		# Read the map's config
		self.mapConfig = configparser.RawConfigParser()
		self.mapConfig.read(self.map_config_file)

		self.mapName = self.mapConfig.get("MapConfig", "Name")
		self.mapWidth = int(self.mapConfig.get("MapConfig","Width"))
		self.mapHeight = int(self.mapConfig.get("MapConfig","Height"))
		self.start_Position_X = int(self.mapConfig.get("MapConfig", "Player_Start_Position_X"))
		self.start_Position_Y = int(self.mapConfig.get("MapConfig", "Player_Start_Position_Y"))

		print("Name: "+self.mapName)
		print("Width: "+str(self.mapWidth))
		print("Height: "+str(self.mapHeight))
		print("Starting Position: "+str(self.start_Position_X),str(self.start_Position_Y))
		################################ End Map Config

		################################ Adding Static Lines
		self.map_file = self.map_zip.extract('map_layout.map', path = 'temp')
		self.map_file = open(self.map_file)

		self.space = space
		self.static_body = pymunk.Body()

		self.map_segment_verts = [] # creates a list to hold segments contained in map file
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
				print(line)
				line.friction = .5
				line.group = 2
				line.collision_type = 2
				self.map_segment_verts.append(line)
				continue
			if line.startswith("elevator"):
				print(line)
				line = eval(line)
				self.elevators.append(line)
				continue
			if line.startswith("bridge"):
				print(line)
				line = eval(line)
				self.bridges.append(line)
				continue
			if line.startswith("jelly"):
				print(line)
				line = eval(line)
				self.jellies.append(line)
				continue
			if line.startswith("mobi"):
				print(line)
				line = eval(line)
				self.mobis.append(line)
				continue
			if line.startswith("box.Boxes"):
				print(line)
				line = eval(line)
				self.boxes.append(line)
				continue

			if line.startswith("playerdetector"):
				print(line)
				line = eval(line)
				self.detectors.append(line)
				continue

		self.space.add(self.map_segment_verts)
		################################# End Adding Map Objects
		
		# Unzip map specific images.
		self.pbg = self.map_zip.extract('pbg.png', path = 'resources/temp')
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
		pyglet.resource.reindex()
		self.pbg = pyglet.resource.image("pbg.png")
		self.pbg_sprite = pyglet.sprite.Sprite(self.pbg, batch = batch, group = ordered_group_pbg)
		self.pbg_sprite.scale = .5

		self.bg = self.map_zip.extract('bg.png', path = 'resources/temp')
		pyglet.resource.reindex()
		self.bg = pyglet.resource.image("bg.png")
		self.bg_sprite = pyglet.sprite.Sprite(self.bg, batch = batch, group = ordered_group_bg)
		self.bg_sprite.scale = .5

		self.map_zip.close()

		for line in self.map_segment_verts:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
			self.stuff = self.batch.add(2, pyglet.gl.GL_LINES, ordered_group_fg,
										('v2f/static', (p1[0],p1[1],p2[0],p2[1])),
										('c3B/static', (125,10,160,0,255,0)))


	def update(self, player_pos, camera_offset):
		self.camera_offset = camera_offset
		self.pbg_sprite.x = self.camera_offset[0] * -.2 + 400
		self.pbg_sprite.y = self.camera_offset[1] * -.2 + 120
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
