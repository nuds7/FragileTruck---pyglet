import pyglet
from pyglet.gl import *
import zipfile
#import pymunk
#from pymunk import Vec2d

class Audio(object):
	def __init__(self):
		pass
	def load(self, audio_file):
		self.audio_file = audio_file
		self.sound = pyglet.media.load(audio_file)
		# Hack that loads the sound, 
		# plays it at zero volume, then 
		# loads it again so there is no
		# in-game lag when the sound is 
		# first played.
		self.sound.play().volume = 0
		self.sound = pyglet.media.load(audio_file)
		return self.sound
	def play(self):
		self.sound.play()
		## Play the sound, then reset the player
		self.sound = pyglet.media.load(self.audio_file)

def spriteloader(image_file, 
				placeholder = 'placeholder.png',
				anchor 					= None, 
				anchor_offset			= None,
				resize					= False,
				size  					= None, 
				scale 					= 1,
				pos   					= (0,0),
				batch 					= None, 
				group 					= None, 
				linear_interpolation	= False,):
	try:
		#print(image_file)
		image = pyglet.resource.image(image_file)
		missing = False
	except:
		#print('Missing "'+str(image_file)+'." Replacing with "'+str(placeholder)+'."')
		image = pyglet.resource.image(placeholder)
		missing = True

	image = image.get_region(0,0,image.width,image.height)
	sprite = pyglet.sprite.Sprite(image, batch = batch, group = group)

	if resize or missing:
		if size != None:
			sprite.image.width, sprite.image.height = size

	if isinstance(anchor[0], int):
		sprite.image.anchor_x = anchor[0]
	if isinstance(anchor[1], int):
		sprite.image.anchor_y = anchor[1]
	if anchor[0] == 'center':
		sprite.image.anchor_x = image.width//2
	if anchor[1] == 'center':
		sprite.image.anchor_y = image.height//2
	if anchor[0] == 'right':
		sprite.image.anchor_x = image.width
	if anchor[1] == 'top':
		sprite.image.anchor_y = image.height
	if anchor_offset != None:
		sprite.image.anchor_x = sprite.image.anchor_x + anchor_offset[0]
		sprite.image.anchor_y = sprite.image.anchor_y + anchor_offset[1]

	sprite.scale = scale
	sprite.x,sprite.y = pos

	if linear_interpolation:
		tex = image.get_texture()
		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
	else:
		tex = image.get_texture()
		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	
	return sprite

def image_sprite_loader(image_file, 
						placeholder = 'placeholder.png',
						anchor 					= None, 
						anchor_offset			= None,
						resize					= False,
						size  					= None, 
						scale 					= 1,
						pos   					= (0,0),
						batch 					= None, 
						group 					= None, 
						linear_interpolation	= False,):
	'''
	try:
		#print(image_file)
		image = pyglet.resource.image(image_file)
		missing = False
	except:
		#print('Missing "'+str(image_file)+'." Replacing with "'+str(placeholder)+'."')
		image = pyglet.resource.image(placeholder)
		missing = True
	'''
	missing = False
	#image = image.get_region(0,0,image.width,image.height)
	sprite = pyglet.sprite.Sprite(image_file, batch = batch, group = group)

	if resize or missing:
		if size != None:
			sprite.image.width, sprite.image.height = size

	if isinstance(anchor[0], int):
		sprite.image.anchor_x = anchor[0]
	if isinstance(anchor[1], int):
		sprite.image.anchor_y = anchor[1]
	if anchor[0] == 'center':
		sprite.image.anchor_x = sprite.image.width//2
	if anchor[1] == 'center':
		sprite.image.anchor_y = sprite.image.height//2
	if anchor[0] == 'right':
		sprite.image.anchor_x = sprite.image.width
	if anchor[1] == 'top':
		sprite.image.anchor_y = sprite.image.height
	if anchor_offset != None:
		sprite.image.anchor_x = sprite.image.anchor_x + anchor_offset[0]
		sprite.image.anchor_y = sprite.image.anchor_y + anchor_offset[1]

	sprite.scale = scale
	sprite.x,sprite.y = pos
	
	if linear_interpolation:
		tex = sprite.image.get_texture()
		glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

	return sprite