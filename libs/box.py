import pymunk
import pyglet

class CreatePymunkBox:
	def __init__(self, mass, size, friction, position, space):
		self.box_mass = mass
		self.box_size = size
		self.box_inertia = pymunk.moment_for_box(self.box_mass,self.box_size[0],self.box_size[1])
		self.box_body = pymunk.Body(self.box_mass, self.box_inertia)
		self.box_body.position = position
		self.box_shape = pymunk.Poly.create_box(self.box_body, self.box_size)
		self.box_shape.friction = friction

		self.space = space
		self.space.add(self.box_body, self.box_shape)

	def draw(self):
		self.box_verts = self.box_shape.get_points()
		self.vertlist = []
		for v in self.box_verts: # transforms a list of tuple coords (Vec2d(x,y),Vec2d(x,y), etc) 
			self.vertlist.append(v.x) # to a list that pyglet can draw to [x,y, x,y, etc]
			self.vertlist.append(v.y)
		pyglet.graphics.draw(4, pyglet.gl.GL_POLYGON,
							('v2f', (self.vertlist)),
							('c3B', (0,0,255,0,255,0,255,0,255,255,0,0))
							)