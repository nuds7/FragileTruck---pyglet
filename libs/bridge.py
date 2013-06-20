import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import math
from math import sin,cos
import levelassembler

class Bridge:
	def __init__(self, space, starting_position, segment_size, amount, slack, image):

		self.starting_position = starting_position
		self.segment_size = segment_size
		self.space = space

		self.segment_mass = .5
		self.segment_list = []
		self.body_list = []
		self.add = 0
		for i in range(amount):
			self.segment_inertia      		= pymunk.moment_for_box(self.segment_mass, self.segment_size[0], self.segment_size[1])
			self.segment_body              	= pymunk.Body(self.segment_mass, self.segment_inertia)
			self.segment_body.position     	= self.starting_position[0]+self.add,self.starting_position[1]
			self.segment_shape             	= pymunk.Poly.create_box(self.segment_body, self.segment_size)
			self.segment_shape.friction    	= .8
			self.segment_shape.group       	= 2

			self.space.add(self.segment_body, self.segment_shape)
			self.body_list.append(self.segment_body)
			self.segment_list.append(self.segment_shape)


			self.add += self.segment_size[0]

		# Here I create two bodies that attach to each end of the bridge
		self.start_constraint = pymunk.Body()
		self.start_constraint.position = self.starting_position[0]-self.segment_size[0]//2,self.starting_position[1]

		self.end_constraint = pymunk.Body()
		self.end_constraint.position = self.starting_position[0]+self.add-self.segment_size[0]//2 - slack,self.starting_position[1]

		self.rest_ln = 0
		self.stiffness = 100
		self.damp = 8
		
		self.startPivot = pymunk.constraint.PivotJoint(self.start_constraint, self.body_list[0], (0,0), (self.segment_size[0]//-2,0))
		self.endPivot = pymunk.constraint.PivotJoint(self.end_constraint, self.body_list[-1], (0,0), (self.segment_size[0]//2,0))
		
		self.space.add(self.startPivot,self.endPivot)
		

		self.target_connect = 0
		# Pin Joint
		for seg in self.body_list[1:]:
			self.bridgeJoint = pymunk.constraint.PivotJoint(self.body_list[self.target_connect], seg, 
															(self.segment_size[0]//2,0), (self.segment_size[0]//-2,0))
			self.space.add(self.bridgeJoint)
			self.target_connect += 1
		'''
		## Primitives
		self.bridgeOutlineList = []
		for thing in self.body_list:
			self.bridgeOutlineDraw = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
			self.bridgeOutlineList.append(self.bridgeOutlineDraw)

		self.bridgeFillList = []
		for thing in self.body_list:
			self.bridgeFillDraw = debug_batch.add_indexed(4, pyglet.gl.GL_TRIANGLES, ordered_group, [0,1,2,2,3,0], ('v2f'), ('c4B', (0,0,0,50)*4))
			self.bridgeFillList.append(self.bridgeFillDraw)
		
		
		self.bridgeAnchors = debug_batch.add(2, pyglet.gl.GL_POINTS, ordered_group, ('v2f', (self.start_constraint.position[0],self.start_constraint.position[1],
																	self.end_constraint.position[0],self.end_constraint.position[1])),
																	('c3B', (0,255,0)*2))
		'''
		
		glPointSize(4)

		self.sprites = []
		
		image = levelassembler.imageloader(image, 'placeholder.png', (self.segment_size))
		image.anchor_x = image.width/2
		image.anchor_y = image.height/2
		for i in range(amount):
			sprite = pyglet.sprite.Sprite(image)
			#sprite.scale = .5
			self.sprites.append(sprite)
	def setup_pyglet_batch(self, debug_batch, level_batch, ordered_group):
		## Primitives
		self.bridgeOutlineList = []
		for thing in self.body_list:
			self.bridgeOutlineDraw = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
			self.bridgeOutlineList.append(self.bridgeOutlineDraw)

		self.bridgeFillList = []
		for thing in self.body_list:
			self.bridgeFillDraw = debug_batch.add_indexed(4, pyglet.gl.GL_TRIANGLES, ordered_group, [0,1,2,2,3,0], ('v2f'), ('c4B', (0,0,0,50)*4))
			self.bridgeFillList.append(self.bridgeFillDraw)

		self.bridgeAnchors = debug_batch.add(2, pyglet.gl.GL_POINTS, ordered_group, ('v2f', (self.start_constraint.position[0],self.start_constraint.position[1],
																	self.end_constraint.position[0],self.end_constraint.position[1])),
																	('c3B', (0,255,0)*2))
		for sprite in self.sprites:
			sprite.batch = level_batch
			sprite.group = ordered_group

	def draw(self):
		# Change the outline color if the body is sleeping
		self.outline_color = (200,200,200)
		#if self.segment_body.is_sleeping: self.outline_color = (250,0,0)

		for bod in self.body_list[1:-2]:
			#bod.apply_impulse((0,1))
			bod.angular_velocity *= 0.8
			bod.velocity[1] *= 0.9
		
		iterNum = 0
		for bp in self.bridgeOutlineList:
			self.pPoints = self.segment_list[iterNum].get_points()
			self.p_list = []
			for point in self.pPoints:
				self.p_list.append(point.x)
				self.p_list.append(point.y)
			bp.vertices = self.p_list
			self.bridgeFillList[iterNum].vertices = self.p_list
			iterNum += 1
		
		iterNum = 0
		for s in self.sprites:
			s.set_position(self.body_list[iterNum].position[0], self.body_list[iterNum].position[1])
			s.rotation = math.degrees(-self.body_list[iterNum].angle)
			iterNum += 1