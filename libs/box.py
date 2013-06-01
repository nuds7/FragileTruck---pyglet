import pymunk
import pyglet

class Boxes:
	def __init__(self, space, mass, size, friction, position, amount, add_x, add_y, batch, ordered_group):
		add_new_x = 0
		add_new_y = 0
		inertia = pymunk.moment_for_box(mass, size[0],size[1])

		self.shape_list = []

		for i in range(amount):
			body = pymunk.Body(mass, inertia)
			body.position = (position[0]+add_new_x, position[1]+add_new_y)
			shape = pymunk.Poly.create_box(body, size)
			shape.friction = friction

			space.add(body, shape)
			self.shape_list.append(shape)
			add_new_x += add_x
			add_new_y += add_y

		self.outlineList = []
		for thing in self.shape_list:
			self.outline = batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
			self.outlineList.append(self.outline)

		self.fillList = []
		for thing in self.shape_list:
			self.fill = batch.add_indexed(4, pyglet.gl.GL_TRIANGLES, ordered_group, [0,1,2,2,3,0], ('v2f'), ('c4B', (200,200,200,200)*4))
			self.fillList.append(self.fill)

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