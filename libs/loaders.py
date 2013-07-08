import pyglet
from pyglet.gl import *
#import pymunk
#from pymunk import Vec2d

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
	if anchor[0] == 'top':
		sprite.image.anchor_x = image.width
	if anchor[1] == 'right':
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

	return sprite