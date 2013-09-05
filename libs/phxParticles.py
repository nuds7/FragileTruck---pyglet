import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import math
from math import sin,cos
from numpy.random import uniform,randint,choice
import PiTweener
import loaders

class PhysParticle(object):
	def __init__(self, 
				 pos,
				 age,
				 img_path, 
				 batch,
				 group,
				 start_impulse=(0,0),
				 *args, **kwargs):

		self.age = age
		self.batch = batch

		self.start_impulse = Vec2d(start_impulse)

		self.sprite = loaders.spriteloader(img_path,
                                           pos = pos,
                                           anchor = ('center', 'center'),
                                           batch = batch, 
                                           group = group,
                                           linear_interpolation = True)
		self.sprite.visible 	= False

		self.mass 				= .00001
		self.radius 			= self.sprite.image.width/2
		inertia 				= pymunk.moment_for_circle(self.mass, 0, self.radius)
		self.body 				= pymunk.Body(self.mass, pymunk.inf)
		self.body.position 		= Vec2d(pos)
		self.shape 				= pymunk.Circle(self.body, self.radius)
		self.shape.elasticity 	= .5
		self.shape.friction 	= .1
		self.shape.group 		= 1
		
		self.body.apply_impulse(self.start_impulse)
		self.tweener = PiTweener.Tweener()
		self.tweener.add_tween(self,
                               age = 0,
                               tween_time = age,
                               tween_type = self.tweener.LINEAR,)
		self.tween = False
		self.removed = False

	def update(self):
		if self.tween:
			self.tweener.update()
		self.sprite.set_position(self.body.position[0],
								 self.body.position[1])

class Spurt(object):
	def __init__(self,
				 space,
				 age,
				 amount,
				 pos, 
				 start_impulse_seed,
				 img,
				 batch=None,
				 group=None):
		self.space = space
		self.particles = []
		for i in range(amount):
			rand_impulse = (uniform(start_impulse_seed[0][0],start_impulse_seed[0][1]),
							uniform(start_impulse_seed[1][0],start_impulse_seed[1][1]))

			particle = PhysParticle(pos,
									age,
									img,
									batch,
									group, 
									start_impulse = rand_impulse)
			particle.start_impulse = rand_impulse
			self.particles.append(particle)

		self.spawn = False
		self.spawned = False

	def update(self):
		if self.spawn and not self.spawned:
			self.spawned = True
			for p in self.particles:
				p.sprite.visible = True
				self.space.add(p.body,p.shape)
		if self.spawn:
			for p in self.particles:
				p.tween = True
				p.update()
				if p.age == 0 and not p.removed:
					p.removed = True
					self.space.remove(p.body, p.shape)
					#p.sprite.delete()
				