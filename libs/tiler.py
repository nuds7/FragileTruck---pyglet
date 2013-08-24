import os, sys
import pyglet
from pyglet.gl import *
from math import sqrt

class BackgroundTiler(object):
	def __init__(self, image, scale=1, tile_size = 256):
		self.scale = scale
		self.tile_size = tile_size
		try:
			img = pyglet.resource.image(image)
		except:
			tile_size = 64
			img = pyglet.resource.image('placeholder.png')
			
		tex = img.get_texture()
		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

		self.width = img.width
		self.height = img.height
		
		w_tile = self.width//tile_size
		h_tile = self.height//tile_size

		tiles = []
		self.tile_positions = []
		i_num = 0
		for h in range(h_tile):
			for w in range(w_tile):
				self.tile_positions.append(
										  (
										  (tile_size*(w)*scale), ## visible seams +w, +h
										  (tile_size*(h)*scale)
										  )
										  )
				#print(self.tile_positions)
				tiles.append(img.get_region(tile_size*(w),tile_size*(h),tile_size,tile_size))

		#print(tiles)
		print('Number of tiles:', str(len(tiles)))

		self.sprite_tiles = []
		for t in tiles:
			sprite = pyglet.sprite.Sprite(t)
			self.sprite_tiles.append(sprite)

		
	def setup(self, batch, group, map_size):
		self.map_size = map_size
		i_num = 0
		for s in self.sprite_tiles:
			s.batch = batch
			s.group = group
			s.scale = self.scale
			s.x = self.tile_positions[i_num][0] + map_size[0]//2 - self.width//4
			s.y = self.tile_positions[i_num][1] + map_size[1]//2 - self.height//4
			i_num += 1

	def parallax_scroll(self, x, y):
		i_num = 0
		for s in self.sprite_tiles:
			s.x = self.tile_positions[i_num][0] + self.map_size[0]//2 - self.width//4 + x + 4
			s.y = self.tile_positions[i_num][1] + self.map_size[1]//2 - self.height//4 + y
			i_num += 1

	def pop(self, camera_pos, camera_scale):
		for s in self.sprite_tiles:
			distance = abs(sqrt((s.x-camera_pos[0]+self.tile_size//4)**2+(s.y-camera_pos[1]+self.tile_size//4)**2))
			if distance > camera_scale*2 + 150: # +150
				s.visible = False
			else:
				s.visible = True
