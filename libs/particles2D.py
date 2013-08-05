import pyglet
from pyglet.gl import *
import random
from random import uniform,randrange,choice
import loaders
from pymunk import Vec2d
import pytweener

## http://stackoverflow.com/questions/14885349/how-to-implement-a-particle-engine
## Performance? http://docs.cython.org/src/userguide/tutorial.html
## or PyPy

def omni_spread(speed_x,speed_y):
    def _omni_spread(particle):
        particle.x += speed_x
        particle.y += speed_y
    return _omni_spread
def init_vel(x,y):
    def _init_vel(particle):
        particle.x += particle.vel[0]
        particle.y += particle.vel[1]
        particle.vel += Vec2d(x,y)
    return _init_vel
def gravity(strength_x,strength_y):
    def _gravity(particle):
        particle.x += particle.vel[0]
        particle.y += particle.vel[1]
        particle.vel += Vec2d(strength_x,strength_y)
    return _gravity

def scale(scale):
    def _scale(particle):
        particle.sprite.scale = scale
    return _scale

def rotate(speed):
    def _rotate(particle):
        particle.sprite.rotation += speed
    return _rotate

def age(amount):
    def _age(particle):
        particle.alive += amount
    return _age
def age_kill():
    def _age_kill(particle):
        particle.alive -= 1
        if particle.alive < 0:
            particle.kill()
    return _age_kill
def age_fade_kill():
    def _age_fade_kill(particle):
        particle.alive -= 1
        if particle.alive < 13:
            particle.sprite.opacity -= 15
        if particle.alive < 0:
            particle.kill()
    return _age_fade_kill

def age_scale_fade_kill(rate):
    def _age_scale_fade_kill(particle):
        particle.alive -= 1
        if particle.alive < 13:
            particle.sprite.opacity -= 15
            particle.sprite.scale += rate
        if particle.alive < 0:
            particle.kill()
    return _age_scale_fade_kill

def kill_at(max_x,max_y):
    def _kill_at(particle):
        if particle.x < -max_x or particle.x > max_x or particle.y < -max_y or particle.y > max_y:
            particle.kill()
    return _kill_at
def fade_kill_at(max_x,max_y):
    def _kill_at(particle):
        if particle.x < -max_x or particle.x > max_x or particle.y < -max_y or particle.y > max_y:
            particle.sprite.opacity -= 15
            if particle.sprite.opacity < 20:
                particle.kill()
    return _kill_at


def ascending(speed):
    def _ascending(particle):
        particle.y += speed
    return _ascending
def fan_out(modifier):
    def _fan_out(particle):
        d = particle.alive / modifier
        d += 1
        particle.x += random.randrange(int(-d),int(d))
    return _fan_out
def wind(direction, strength):
    def _wind(particle):
        if random.randint(0,100) < strength:
            particle.x += direction
    return _wind


def spark_machine(age,img,batch,group):
    def create():
        for _ in range(random.choice([0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4])):
            behavior = (
                        omni_spread(uniform(0.4,-0.4),uniform(0.2,-0.2)),
                        age_fade_kill(),
                        #scale(uniform(2,5)),
                        #fade_kill_at(260,160),
                        rotate(uniform(0.2,-0.2)),
                        scale(uniform(2,5))
                        )
            p = Particle(age,img,batch,group,*behavior)
            yield p
    while True:
        yield create()
def confetti_machine(age,i_vel,img,batch,group):
    def create():
        for _ in range(random.choice([0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4])):
            behavior = (
                        gravity(0,-0.1),
                        #age_kill(),
                        age_fade_kill(),
                        scale(uniform(.5,1)),
                        #rotate(uniform(1,-1))
                        )
            p = Particle(age,img,batch,group,*behavior)
            p.vel = (uniform(i_vel[0][0],i_vel[0][1]),
                     uniform(i_vel[1][0],i_vel[1][1]))
            #p.sprite.color = (randrange(0,255),
            #                  randrange(0,255),
            #                  randrange(0,255),)
            yield p
    while True:
        yield create()


class Particle():
    def __init__(self,age,img,batch=None,group=None,*strategies,age_offset=(0,100)):
        self.x,self.y = 0,0
        self.vel = Vec2d(0,0)
        self.sprite = loaders.image_sprite_loader(img,
                                                  pos = (self.x,self.y),
                                                  anchor = ('center', 'center'),
                                                  batch = batch, 
                                                  group = group,
                                                  linear_interpolation = True
                                                  )
        self.age = age + random.randrange(age_offset[0],age_offset[1])
        self.alive = age 
        self.strategies = strategies
    def set_scale(self, scale):
        self.sprite.scale = scale
    def kill(self):
        self.alive = -1
    def move(self):
        for s in self.strategies:
            s(self)

class Emitter(object):
    def __init__(self, pos=(0,0), max_num = (1500), *args, **kwargs):
        self.particles = []
        self.pos = pos
        self.factories = []
        self.max_num = max_num
        self.emit = True
    def add_factory(self,factory,pre_fill=300):
        self.factories.append(factory)
        tmp = []
        for _ in range(pre_fill):
            n = next(factory)
            tmp.extend(n)
            for p in tmp:
                p.move()
        self.particles.extend(tmp)
    def update(self):
        if self.emit:
            for f in self.factories:
                if len(self.particles) < self.max_num:
                    self.particles.extend(next(f))
            for p in self.particles[:]:
                p.move()
                if p.alive == -1:
                    self.particles.remove(p)
    def draw(self):
        if self.emit:
            for p in self.particles:
                p.sprite.x,p.sprite.y = self.pos[0]+p.x,self.pos[1]+p.y