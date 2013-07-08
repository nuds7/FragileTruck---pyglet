import pymunk
from pymunk import Vec2d
import pyglet
from pyglet.gl import *
import math
import loaders

def imageloader(image_file, placeholder):
	try:
		image = pyglet.resource.image(image_file)
	except:
		print('Missing "'+str(image_file)+'." Replacing with "'+str(placeholder)+'."')
		image = pyglet.resource.image(placeholder)
	return image

class Boxes:
	def __init__(self, space, position, size, mass, friction, 
				amount, add, image, 
				menu_box = False,
				placeholder = 'placeholder.png', 
				scale = .5, 
				point_query = False, 
				name = 'None'):
		add_new_x = 0
		add_new_y = 0
		self.space = space
		inertia = pymunk.moment_for_box(mass, size[0],size[1])
		self.shape_list = []
		self.body_list = []

		for i in range(amount):
			self.body = pymunk.Body(mass, inertia)
			self.body.position = (position[0]+add_new_x, position[1]+add_new_y)
			shape = pymunk.Poly.create_box(self.body, size)
			shape.friction = friction
			space.add(self.body, shape)
			self.shape_list.append(shape)
			self.body_list.append(self.body)
			add_new_x += add[0]
			add_new_y += add[1]

		self.sprites = []
		for i in range(amount):
			sprite = loaders.spriteloader(image,
										   placeholder = placeholder,
										   #size = size,
										   scale = scale,
										   anchor = ('center','center'),
										   linear_interpolation = True)
			self.sprites.append(sprite)
		self.point_query = point_query
		self.mouse_pos = [0,0]
		self.mouse_buttons = 0
		self.name = name
		self.map_file = name
		self.contains = False
		self.clicked = False
		self.menu_box = menu_box

		self.grabFirstClick = True
		self.mouseGrabbed = False

	def setup_pyglet_batch(self, debug_batch, level_batch, ordered_group, ordered_group2=None):

		self.outlineList = []
		for thing in self.shape_list:
			self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, None, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
			self.outlineList.append(self.outline)

		self.fillList = []
		for thing in self.shape_list:
			if not self.menu_box:
				self.fill = debug_batch.add_indexed(4, pyglet.gl.GL_TRIANGLES, None, [0,1,2,2,3,0], ('v2f'), ('c4B', (200,200,200,100)*4))
			else: 
				self.fill = level_batch.add_indexed(4, pyglet.gl.GL_TRIANGLES, ordered_group2, [0,1,2,2,3,0], ('v2f'), ('c4B', (200,200,200,100)*4))
			self.fillList.append(self.fill)
		'''
		for thing in self.outlineList:
			thing.batch = debug_batch
		'''
		for thing in self.fillList:
			#thing.batch = debug_batch
			thing.group = ordered_group2
		
		for sprite in self.sprites:
			sprite.batch = level_batch
			sprite.group = ordered_group

	def draw(self):
		
		iterNum = 0
		for s in self.sprites:
			s.set_position(self.body_list[iterNum].position[0], self.body_list[iterNum].position[1])
			s.rotation = math.degrees(-self.body_list[iterNum].angle)
			iterNum += 1
		if self.point_query:
			for shape in self.shape_list:
				if shape.point_query(self.mouse_pos):
					self.contains = True
					if self.mouse_buttons == 1:
						if not self.clicked:
							self.clicked = True
							self.map_file = self.name
							print('Clicked: '+str(self.clicked), self.map_file)
				else: 
					self.clicked = False
					self.contains = False
		iterNum = 0
		for bp in self.outlineList:
			self.pPoints = self.shape_list[iterNum].get_points()
			self.p_list = []
			for point in self.pPoints:
				self.p_list.append(point.x)
				self.p_list.append(point.y)
			bp.vertices = self.p_list
			self.fillList[iterNum].vertices = self.p_list
			if self.contains:
				self.fillList[iterNum].colors = (0,200,0,50)*4
				if self.mouse_buttons == 1:
					self.fillList[iterNum].colors = (50,100,30,70)*4
			if not self.contains:
				self.fillList[iterNum].colors = (200,200,200,0)*4
			iterNum += 1
			
		self.mouse_buttons = 0
	def mouse_grab_press(self, mouse_pos):
		if self.contains == True:
			if self.grabFirstClick == True:
				self.mouseBody = pymunk.Body()
				self.grabFirstClick = False
			self.mouseBody.position = mouse_pos
			sx = (mouse_pos[0] - self.body.position[0])
			sy = (mouse_pos[1] - self.body.position[1])
			spring_pos = Vec2d(sx,sy).rotated(-self.body.angle)
			self.mouseGrabSpring = pymunk.constraint.DampedSpring(self.mouseBody, self.body, (0,0), (spring_pos), 0, .5, .01)
			self.space.add(self.mouseGrabSpring)
			self.mouseGrabbed = True
	def mouse_grab_drag(self, mouse_coords):
		if self.mouseGrabbed == True:
			self.mouseBody.position = mouse_coords
	def mouse_grab_release(self):
		if self.mouseGrabbed == True:
			self.space.remove(self.mouseGrabSpring)
			self.mouseGrabbed = False

	def remove(self):
		self.space.remove(self.body_list)
		self.space.remove(self.shape_list)
		for bp in self.outlineList:
			bp.delete()
		for bp in self.fillList:
			bp.delete()
		self.sprites = []
		print('Level cleared of all boxes!')