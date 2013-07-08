import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import random
from random import randrange,uniform
import levelassembler 
import loaders

class SimpleParticle:
	def __init__(self, pos, grav, vel, rot, life, image, batch, ordered_group=None, rainbow_mode = False, random_scale = False):
		self.pos = Vec2d(pos)
		self.vel = Vec2d(vel)
		self.grav = Vec2d(grav)
		self.rot = rot
		self.life = life + randrange(0,30)
		self.sprite = loaders.spriteloader(image,
										   pos = pos,
										   anchor = ('center', 'center'),
										   batch = batch, 
										   group = ordered_group,
										   linear_interpolation = True)
		if rainbow_mode:
			self.sprite.color = (randrange(0,255),
								 randrange(0,255),
								 randrange(0,255),)
		if random_scale:
			self.sprite.scale = uniform(.5, 2)
			#print(self.sprite.scale)

class SimpleEmitter:
	def __init__(self, image, batch, 
				stretch = None, 
				max_active = None, 
				ordered_group = None, 
				rainbow_mode = False, 
				random_scale = False, 
				fade_out = False):
		self.image = image
		self.batch = batch
		self.ordered_group = ordered_group
		self.particles = []
		self.max_active = max_active
		self.rainbow_mode = rainbow_mode
		self.random_scale = random_scale
		self.fade_out = fade_out
	def emit(self, amount, pos, grav, vel, rot, life):
		for i in range(amount):
			n_vel = [vel[0],vel[1]]
			if isinstance(vel[0], tuple):
				n_vel[0] = uniform(vel[0][0],vel[0][1])
			if isinstance(vel[1], tuple):
				n_vel[1] = uniform(vel[1][0],vel[1][1])
			n_rot = rot
			if isinstance(rot, tuple):
				n_rot = uniform(rot[0],rot[1])

			if self.max_active == None:
				p = SimpleParticle(pos, 
								   grav, 
								   n_vel, 
								   n_rot, 
								   life, 
								   self.image, 
								   self.batch, 
								   ordered_group = self.ordered_group,
								   rainbow_mode = self.rainbow_mode,
								   random_scale = self.random_scale)
				self.particles.append(p)
			elif len(self.particles) < self.max_active:
				p = SimpleParticle(pos, 
								   grav, 
								   n_vel, 
								   n_rot, 
								   life, 
								   self.image, 
								   self.batch, 
								   ordered_group = self.ordered_group,
								   rainbow_mode = self.rainbow_mode,
								   random_scale = self.random_scale)
				self.particles.append(p)
	def update(self):
		for p in self.particles:
			p.pos = p.pos + p.vel
			p.vel += p.grav
			p.life -= 1
			p.sprite.x = p.pos[0]
			p.sprite.y = p.pos[1]
			p.sprite.rotation += p.rot
			if self.fade_out:
				if p.life <= 13:
					p.sprite.opacity -= 19

		self.particles = [p for p in self.particles if p.life>0]

class Particle:
	def __init__ (self, space, color, batch, order_group):
		self.color = color
		
		self.space = space
		self.radius = 0.5
		self.mass = 0.001

		self.particle_body_list = []
		self.particle_shape_list = []
		self.particle_pos_list = []
		self.collidingBool = False

		self.list_size = 1
		self.particle_line_list = batch.add(1, pyglet.gl.GL_LINES, order_group,
                            ('v2f'),
                            ('c3B'),)

	def colliding(self, space, arb): # for 
		self.collidingBool = True
		for c in arb.contacts:
			#print("touching at:", c.position)
			#self.initial_velocity = initial_velocity
			self.position = c.position
		return True

	def collided(self, space, arb):
		self.collidingBool = False
		return True

	def add(self, initial_velocity, spawn_amount):
		
		for i in range(spawn_amount):
			self.body = pymunk.Body(self.mass, pymunk.inf)
			self.body.position = self.position[0]+randrange(-2,2),self.position[1]+randrange(-2,2)
			self.body.velocity = Vec2d(initial_velocity)#Vec2d(self.initial_velocity)
			self.shape = pymunk.Circle(self.body, self.radius)
			self.shape.group = 1
			self.shape.friction = 1
			self.shape.elasticity = 1.0
			
			self.space.add(self.body, self.shape)
			self.particle_body_list.append(self.body)
			self.particle_shape_list.append(self.shape)

	def draw(self):
		self.particle_pos_list = []
		if len(self.particle_body_list)//2 > 1:
			for body in self.particle_body_list:
				self.particle_pos_list.append(body.position[0])
				self.particle_pos_list.append(body.position[1])
				self.particle_pos_list.append(body.position[0]+body.velocity[0]/20)
				self.particle_pos_list.append(body.position[1]+body.velocity[1]/20)

		self.particle_line_list.resize(len(self.particle_pos_list)//2)
		self.particle_line_list.vertices = self.particle_pos_list
		self.particle_line_list.colors = (self.color*self.particle_line_list.count)

		'''
		if len(self.particle_pos_list)//2 > 1:
			self.particle_line_list.delete()
		self.particle_line_list = self.batch.add(len(self.particle_pos_list)//2, pyglet.gl.GL_LINES, None,
                            ('v2f', self.particle_pos_list),
                            ('c3B', self.color*(len(self.particle_pos_list)//2)),
                            )
		'''

		#goopy looking stuff
		'''
		if len(self.particle_pos_list)//2 > 1:
			self.particle_point_list.delete()
		self.particle_point_list = self.batch.add(len(self.particle_pos_list)//2, pyglet.gl.GL_POINTS, None,
                            ('v2f', self.particle_pos_list),
                            ('c3B', self.color*(len(self.particle_pos_list)//2)),
                            )
		'''

	
	def cleanup(self, max_particles):
		if len(self.particle_body_list) > max_particles:
				self.space.remove(self.particle_body_list[0])
				self.space.remove(self.particle_shape_list[0])
				self.particle_body_list.pop(0)
				self.particle_shape_list.pop(0)
	
	'''
	def delete(self):
		self.particle_line_list.delete()
	def add(self, position, amount, initial_velocity):

		self.initial_velocity = initial_velocity
		if len(self.particle_body_list) > 60:
			self.space.remove(self.particle_body_list[0])
			self.space.remove(self.particle_shape_list[0])
			self.particle_body_list.pop(0)
			self.particle_shape_list.pop(0)
		
		for i in range(amount):
			self.body = pymunk.Body(self.mass, pymunk.inf)
			self.body.position = position[0]+randrange(-2,2),position[1]+randrange(-2,2)
			self.body.velocity = Vec2d(self.initial_velocity)
			self.shape = pymunk.Circle(self.body, self.radius)
			self.shape.group = 1
			self.shape.friction = 1
			
			self.space.add(self.body, self.shape)
			self.particle_body_list.append(self.body)
			self.particle_shape_list.append(self.shape)

'''