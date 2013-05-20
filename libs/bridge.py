import pyglet
import pymunk
from math import sin,cos

class Bridge:
	def __init__(self, space, starting_position, segment_size, amount):

		self.starting_position = starting_position
		self.segment_size = segment_size
		self.space = space

		self.segment_mass = .1
		self.segment_list = []
		self.body_list = []
		self.add = 0

		for i in range(amount):
			self.segment_inertia      			= pymunk.moment_for_box(self.segment_mass, self.segment_size[0], self.segment_size[1])
			self.segment_body               	= pymunk.Body(self.segment_mass, 100)
			self.segment_body.position      	= self.starting_position[0]+self.add,self.starting_position[1]
			self.segment_shape              	= pymunk.Poly.create_box(self.segment_body, self.segment_size)
			self.segment_shape.friction     	= .5
			self.segment_shape.group        	= 2

			self.space.add(self.segment_body, self.segment_shape)
			self.body_list.append(self.segment_body)
			self.segment_list.append(self.segment_shape)

			self.add += self.segment_size[0]

		# Here I create two bodies that attach to each end of the bridge
		self.start_constraint = pymunk.Body()
		self.start_constraint.position = self.starting_position[0]-self.segment_size[0]//2,self.starting_position[1]

		self.end_constraint = pymunk.Body()
		self.end_constraint.position = self.starting_position[0]+self.add-self.segment_size[0]+self.segment_size[0]//2,self.starting_position[1]

		self.rest_ln = 0
		self.stiffness = 200
		self.damp = 8
		
		self.startspring = pymunk.constraint.DampedSpring(self.start_constraint, self.body_list[0], (0,0), (self.segment_size[0]//-2,0), self.rest_ln, self.stiffness, self.damp)
		self.endspring = pymunk.constraint.DampedSpring(self.end_constraint, self.body_list[-1], (0,0), (self.segment_size[0]//2,0), self.rest_ln, self.stiffness, self.damp)

		self.space.add(self.startspring,self.endspring)
		

		self.target_connect = 0
		# Spring
		''' 
		for seg in self.body_list[1:]:
			self.springjoint = pymunk.constraint.DampedSpring(self.body_list[self.target_connect], seg, 
															(self.segment_size[0]//2 - 6,0), (self.segment_size[0]//-2 + 6,0), 
															self.rest_ln, self.stiffness, self.damp)
			self.space.add(self.spring)
			self.target_connect += 1
		'''
		# Pin Joint
		for seg in self.body_list[1:]:
			self.pinjoint = pymunk.constraint.PinJoint(self.body_list[self.target_connect], seg, 
															(self.segment_size[0]//2 - 4,0), (self.segment_size[0]//-2 + 4,0))
			self.space.add(self.pinjoint)
			self.target_connect += 1
			
	def draw(self):
		# Change the outline color if the body is sleeping
		self.outline_color = (200,200,200)
		if self.segment_body.is_sleeping: self.outline_color = (250,0,0)
		for seg in self.segment_list:
			self.seg_verts = seg.get_points()
			self.seg_list = []
			for v in self.seg_verts: # transforms a list of tuple coords (Vec2d(x,y),Vec2d(x,y), etc) 
				self.seg_list.append(v.x) # to a list that pyglet can draw to [x,y, x,y, etc]
				self.seg_list.append(v.y)
			
			pyglet.graphics.draw(len(self.seg_list)//2, pyglet.gl.GL_POLYGON,
								('v2f', self.seg_list),
								('c4B', (50,50,50,180)*(len(self.seg_list)//2))
								)
			pyglet.graphics.draw(len(self.seg_list)//2, pyglet.gl.GL_LINE_LOOP,
								('v2f', self.seg_list),
								('c3B', (self.outline_color)*(len(self.seg_list)//2))
								)
			
			
			