import pymunk
import pyglet
import math

class Boxes:
	def __init__(self, space, mass, size, friction, position, amount, add, image, debug_batch, level_batch, ordered_group):
		add_new_x = 0
		add_new_y = 0
		self.space = space
		inertia = pymunk.moment_for_box(mass, size[0],size[1])

		self.shape_list = []
		self.body_list = []

		for i in range(amount):
			body = pymunk.Body(mass, inertia)
			body.position = (position[0]+add_new_x, position[1]+add_new_y)
			shape = pymunk.Poly.create_box(body, size)
			shape.friction = friction

			space.add(body, shape)
			self.shape_list.append(shape)
			self.body_list.append(body)
			add_new_x += add[0]
			add_new_y += add[1]

		self.outlineList = []
		for thing in self.shape_list:
			self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
			self.outlineList.append(self.outline)

		self.fillList = []
		for thing in self.shape_list:
			self.fill = debug_batch.add_indexed(4, pyglet.gl.GL_TRIANGLES, ordered_group, [0,1,2,2,3,0], ('v2f'), ('c4B', (200,200,200,100)*4))
			self.fillList.append(self.fill)

		self.sprites = []
		crateImage = pyglet.resource.image(image)
		crateImage.anchor_x = crateImage.width/2
		crateImage.anchor_y = crateImage.height/2
		for i in range(amount):
			sprite = pyglet.sprite.Sprite(crateImage, batch = level_batch, group = ordered_group)
			sprite.scale = .5
			self.sprites.append(sprite)

	def draw(self):
		iterNum = 0
		for bp in self.outlineList:
			self.pPoints = self.shape_list[iterNum].get_points()
			self.p_list = []
			for point in self.pPoints:
				self.p_list.append(point.x)
				self.p_list.append(point.y)
			bp.vertices = self.p_list
			self.fillList[iterNum].vertices = self.p_list
			iterNum += 1
		iterNum = 0
		for s in self.sprites:
			s.set_position(self.body_list[iterNum].position[0], self.body_list[iterNum].position[1])
			s.rotation = math.degrees(-self.body_list[iterNum].angle)
			iterNum += 1
	def remove(self):
		self.space.remove(self.body_list)
		self.space.remove(self.shape_list)

		for bp in self.outlineList:
			bp.delete()
		for bp in self.fillList:
			bp.delete()
		self.sprites = []
		print('Level cleared of all boxes!')