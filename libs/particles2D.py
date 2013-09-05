import pyglet
from pyglet.gl import *
#import random
#from random import uniform,randrange,choice
from numpy.random import uniform,randint,choice
import loaders
from pymunk import Vec2d
import PiTweener
import itertools

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

def sprite_color_overlay(color):
    def _sprite_color_overlay(particle):
        particle.sprite.color = color
    return _sprite_color_overlay

class FadeToColor(object):
    def __init__(self, color):
        self.r,self.g,self.b = 255,255,255
        self.tweener = PiTweener.Tweener()
        self.tweener.add_tween(self,
                               r = color[0],
                               g = color[1],
                               b = color[2],
                               tween_time = uniform(.25,.5),
                               tween_type = self.tweener.LINEAR,)

def sprite_color_overlay_flash(color):
    fader = FadeToColor(color)
    def _sprite_color_overlay_flash(particle):
        fader.tweener.update()
        particle.sprite.color = fader.r,fader.g,fader.b
    return _sprite_color_overlay_flash


def age(amount):
    def _age(particle):
        particle.alive += amount
    return _age

class AgeDecay(object):
    def __init__(self, age, fade=False):
        self.tweenable = 1
        self.opacity = 255
        self.tweener = PiTweener.Tweener()
        if not fade:
            self.tweener.add_tween(self,
                                   tweenable = 0,
                                   tween_time = age,
                                   tween_type = self.tweener.LINEAR,)
        else:
            self.tweener.add_tween(self,
                                   tweenable = 0,
                                   tween_time = age,
                                   tween_type = self.tweener.OUT_CUBIC,
                                   on_complete_function = self.fade)
    def fade(self):
        self.tweener.add_tween(self,
                               opacity = 0,
                               tween_time = .25,
                               tween_type = self.tweener.LINEAR)

def age_kill(age):
    age_decay = AgeDecay(age)
    def _age_kill(particle):
        age_decay.tweener.update()
        if age_decay.tweenable == 0:
            particle.kill()
    return _age_kill

def age_fade_kill(age):
    age_decay = AgeDecay(age, fade=True)
    def _age_fade_kill(particle):
        age_decay.tweener.update()
        particle.sprite.opacity = age_decay.opacity
        if particle.sprite.opacity == 0:
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
        particle.x += randint(int(-d),int(d))
    return _fan_out
def wind(direction, strength):
    def _wind(particle):
        if randint(0,100) < strength:
            particle.x += direction
    return _wind

def fan(modifier):
    def _fan(particle):
        d = particle.alive / modifier
        d += 1
        particle.x += randint(-d, d)
    return _fan


def spark_machine(age,img,batch,group):
    def create():
        for _ in range(choice([0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4])):
            behavior = (
                        omni_spread(uniform(0.4,-0.4),
                                    uniform(0.2,-0.2)),
                        age_fade_kill(age+uniform(0,.5)),
                        #scale(uniform(2,5)),
                        #fade_kill_at(260,160),
                        rotate(uniform(0.2,-0.2)),
                        scale(uniform(2,5))
                        )
            p = Particle(age,img,batch,group,*behavior)
            yield p
    while True:
        yield create()

def powerup(age, i_vel, img, color_overlay=(0,0,0), batch=None, group=None):
    def create():
        for _ in range(20):
            behavior = (gravity(0,-.08),
                        #sprite_color_overlay_flash(color_overlay),
                        age_fade_kill(age))
            p = Particle(age,img,batch,group,*behavior)
            p.sprite.color = color_overlay
            p.sprite.scale = uniform(.5,1)
            p.vel = (uniform(i_vel[0][0],i_vel[0][1]),
                     uniform(i_vel[1][0],i_vel[1][1]))
            yield p
    while True:
        yield create()



def finish_confetti(age,
                    i_vel,
                    img,
                    batch=None,
                    group=None):
    behavior = (fan(3),
                gravity(0,-0.05),
                age_kill(age+randint(0,2)),)
    def create():
        for _ in range(50):
            p = Particle(age,img,batch,group,*behavior)
            p.sprite.rotation = randint(-90,90)
            p.sprite.scale = randint(3,4)
            p.vel = (uniform(i_vel[0][0],i_vel[0][1]),
                     uniform(i_vel[1][0],i_vel[1][1]))
            yield p
    while True:
        yield create()

class Spurt(object):
    def __init__(self, emitter):
        self.emitter = emitter
        self.tweener = PiTweener.Tweener()
        self.tweenable = 1
    def update(self):
        self.emitter.update()
        self.tweener.update()
    def add_factory(self, factory, duration):
        self.factory = factory
        self.emitter.add_factory(self.factory, pre_fill = 0)
        self.tweener.add_tween(self,
                               tweenable = 0,
                               tween_time = duration,
                               tween_type = self.tweener.LINEAR,
                               on_complete_function = self.remove_factory)
    def remove_factory(self):
        self.emitter.factories.remove(self.factory)


class Particle():
    def __init__(self,age,img,batch=None,group=None,*strategies,age_offset=(0,100)):
        self.x,self.y = 0,0
        self.vel = Vec2d(0,0)
        self.sprite = loaders.image_sprite_loader(img,
                                                  pos = (self.x,self.y),
                                                  anchor = ('center', 'center'),
                                                  batch = batch, 
                                                  group = group,
                                                  linear_interpolation = True)
        self.age = age + randint(age_offset[0],age_offset[1])
        self.alive = age 
        self.strategies = strategies
    def set_scale(self, scale):
        self.sprite.scale = scale
    def kill(self):
        self.alive = -1
    def move(self):
        for s in self.strategies:
            s(self)
        if self.alive > 0:
            return self

class Emitter(object):
    def __init__(self, pos=(0,0), max_num = (1500), *args, **kwargs):
        self.particles = []
        self.pos = pos
        self.factories = []
        self.max_num = max_num

    def add_factory(self,factory,pre_fill=300):
        self.factories.append(factory)
        tmp = []
        for _ in range(pre_fill):
            n = next(factory)
            tmp.extend(n)
            for p in tmp:
                p.move()
        self.particles.extend(tmp)

    def move(self, p):
        p.sprite.x, p.sprite.y = self.pos[0]+p.x,self.pos[1]+p.y
        return p

    def update(self):
        #if self.emit:
        #    for f in self.factories:
        #        if len(self.particles) < self.max_num:
        #            self.particles.extend(next(f))
        #    for p in self.particles[:]:
        #        p.move()
        #        if p.alive == -1:
        #            self.particles.remove(p)
        tmp = itertools.chain(self.particles, *map(next, self.factories)) 
        tmp2 = filter(Particle.move, tmp) # side effect!
        self.particles = list(tmp2)

        for p in self.particles:
            p.sprite.x,p.sprite.y = self.pos[0]+p.x,self.pos[1]+p.y

