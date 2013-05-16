#import pygame
import pyglet
import pymunk
from pymunk import Vec2d
#from pymunk.pygame_util import draw_space, draw_segment
import configparser
import zipfile
#import elevator
#import playerdetector
#import chromaimage
'''
originalMoveImg = pygame.image.load('assets/images/tipmove.png')
moveImg = chromaimage.ChromaSurface(originalMoveImg)

originalSpaceImg = pygame.image.load('assets/images/tipspace.png')
spaceImg = chromaimage.ChromaSurface(originalSpaceImg)
'''
class Game_Level:
	def __init__(self, map_zip, space):
		self.bg = pyglet.resource.image("bg.png")
		self.bg2 = pyglet.resource.image("bg2.png")
		self.bg_sprite = pyglet.sprite.Sprite(self.bg)
		self.bg2_sprite = pyglet.sprite.Sprite(self.bg2)
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
		self.detectors = []
		self.space = space

		for line in self.map_file:
			line = line.strip() # refer to http://programarcadegames.com/index.php?chapter=searching
			#print(line)

			if line == "": continue # skip blank lines
			if line.startswith("#"): continue # skip comments

			# Add static segments and objects first
			if line.startswith("pymunk.Segment"):
				line = eval(line) # converts string to an object ('segment' -> <segment>)
				print(line)
				line.friction = .8
				line.group = 2
				self.map_segment_verts.append(line)
				continue
			if line.startswith("elevator"):
				print(line)
				line = eval(line)
				self.elevators.append(line)
				continue
			if line.startswith("playerdetector"):
				print(line)
				line = eval(line)
				self.detectors.append(line)
				continue

		self.space.add(self.map_segment_verts)
		################################# End Adding Static Lines

		self.map_zip.close()


	def DebugDraw(self, surface, color, color2):
		self.surface = surface
		self.color = color
		self.color2 = color2

		for line in self.map_segment_verts:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
			pygame.draw.line(self.surface, self.color, p1, p2, 2)
		for line in self.elevators:
			self.body_rect = line.shape.get_points()
			pygame.draw.line(self.surface, self.color, line.elevator_top.position, line.position)
			pygame.draw.line(self.surface, self.color2, line.elevator_top.position, line.body.position)
			pygame.draw.lines(self.surface, self.color, True, self.body_rect, 1)
			pygame.draw.circle(self.surface, self.color, (int(line.elevator_top.position[0]),int(line.elevator_top.position[1])), int(4))
		
		for line in self.elevators:
			if line.detected:
				pygame.draw.rect(self.surface, self.color2, line.detection_rect, 2)
			else:
				pygame.draw.rect(self.surface, self.color, line.detection_rect, 1)

		for line in self.detectors:
			if line.detected:
				pygame.draw.rect(self.surface, self.color2, line.detection_rect, 2)
			else: 
				pygame.draw.rect(self.surface, self.color, line.detection_rect, 1)
			pygame.draw.rect(self.surface, self.color, line.player_position_rect, 7)
	def pyglet_draw(self, batch):
		self.batch = batch
		self.bg_sprite.batch = self.batch
		self.bg2_sprite.batch = self.batch
		self.bg_sprite.x = 0
		self.bg_sprite.y = 0

		for line in self.map_segment_verts:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
			self.stuff = self.batch.add(2, pyglet.gl.GL_LINES, None,
							('v2f', (p1[0],p1[1],p2[0],p2[1])),
							('c3B', (0,0,255,0,255,0))
							)
	def update(self, camera_offset):
		self.camera_offset = camera_offset
		self.bg2_sprite.x = self.camera_offset[0] * .1 - 200
		self.bg2_sprite.y = self.camera_offset[1] * .1 - 50


'''
	def pyglet_draw(self, batch):
		for line in self.map_segment_verts:
			p1 = line.a # start of seg
			p2 = line.b # end of seg
			pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
							('v2f', (p1[0],p1[1],p2[0],p2[1])),
							('c3B', (0,0,255,0,255,0))
							)

	def Update(self, player_position, surface):
		self.surface = surface
		self.player_position = player_position
		for line in self.detectors:
			line.update(self.player_position, self.surface)
'''