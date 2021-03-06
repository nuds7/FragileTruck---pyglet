import pyglet
from pyglet.gl import *
#import pygame
import pymunk
from pymunk import Vec2d
import math
from math import sin,cos,atan2,pi    
import levelassembler
import loaders

class Circle:
    def __init__ (self, radius=0, angle=0, position=(0,0), add=0):
        self.add = add
        self.radius = radius
        self.angle = angle
        self.position = position
        self.x = self.radius*cos(self.angle + self.add) + self.position[0]
        self.y = self.radius*sin(self.angle + self.add) + self.position[1]
        
    def update (self, radius, angle, position):

        self.radius = radius
        self.angle = angle
        self.position = position
        self.clist = [self.position[0],self.position[1]]
        #self.clist = []

        for i in range(13):
            c = Circle(radius=self.radius, angle=self.angle, position=self.position, add=self.add)
            self.clist.append(c.x)
            self.clist.append(c.y)
            self.add += .475

        self.list_length = len(self.clist)//2
        if self.add > self.list_length/self.add:
            self.add = 0

        pyglet.graphics.draw(self.list_length, pyglet.gl.GL_POLYGON,
                            ('v2f', (self.clist)),
                            ('c4B', (0,0,0,100)*self.list_length)
                            )

        pyglet.graphics.draw(self.list_length, pyglet.gl.GL_LINE_LOOP,
                            ('v2f', (self.clist)),
                            ('c3B', (0,0,0)*self.list_length)
                            )

class Truck:
    def __init__(self, space, body_position, level_batch, debug_batch, ordered_group_lfg, ordered_group_lfg2, ordered_group_lfg3):
        self.space = space
        #self.map_size = map_size

        self.lcircle = Circle()
        self.rcircle = Circle()

        # body
        self.body_position      = body_position
        self.body_mass          = .9
        self.body_size          = (104,18) #(70,15)
        self.body_inertia       = pymunk.moment_for_box(self.body_mass, self.body_size[0], self.body_size[1])
        self.car_body           = pymunk.Body(self.body_mass, self.body_inertia)
        self.car_body.position  = self.body_position
        #self.body_poly          = pymunk.Poly.create_box(self.car_body, self.body_size)
        self.space.add(self.car_body)
        self.origin = (-9,2)
        self.parts =    [((self.origin),(50,-8),(49,7),(24,8)),
                        ((self.origin),(24,8),(10,20),(-7,20)),
                        ((self.origin),(-51,2),(-55,-8),(50,-8)),
                        ((-55,-8),(-55,6),(-51,10),(-51,2)),
                        ]
        self.shape_list = []
        for part in self.parts:
            self.part = pymunk.Poly(self.car_body, part)
            self.part.friction = 0.3 #0.5
            self.part.group    = 1  # so that the wheels and the body do not collide with eachother
            self.space.add(self.part)
            self.shape_list.append(self.part)

        # left wheel
        self.left_wheel_mass            = .3
        self.left_wheel_radius          = 13
        self.left_wheel_position_x      = self.body_position[0]-(self.body_size[0]//2) + self.left_wheel_radius
        self.left_wheel_position_y      = self.body_position[1] - self.body_size[1]
        self.left_wheel_position        = self.left_wheel_position_x, self.left_wheel_position_y
        
        self.inertiaL                   = pymunk.moment_for_circle(self.left_wheel_mass, 0, self.left_wheel_radius)
        self.left_wheel_b               = pymunk.Body(self.left_wheel_mass, self.inertiaL)
        self.left_wheel_b.position      = self.left_wheel_position
        self.left_wheel_shape           = pymunk.Circle(self.left_wheel_b, self.left_wheel_radius)
        self.left_wheel_shape.friction  = 1.8
        self.left_wheel_shape.group     = 1  # so that the wheels and the body do not collide with eachother
        self.left_wheel_shape.collision_type = 1
        
        self.space.add(self.left_wheel_b, self.left_wheel_shape)

        # right wheel
        self.right_wheel_mass           = .3
        self.right_wheel_radius         = 13
        self.right_wheel_position_x     = self.body_position[0]+(self.body_size[0]//2) - self.right_wheel_radius
        self.right_wheel_position_y     = self.body_position[1] - self.body_size[1]
        self.right_wheel_position       = self.right_wheel_position_x, self.right_wheel_position_y
        
        self.inertiaR                   = pymunk.moment_for_circle(self.right_wheel_mass, 0, self.right_wheel_radius)
        self.right_wheel_b              = pymunk.Body(self.right_wheel_mass, self.inertiaR)
        self.right_wheel_b.position     = self.right_wheel_position
        self.right_wheel_shape          = pymunk.Circle(self.right_wheel_b, self.right_wheel_radius)
        self.right_wheel_shape.friction = 1.8
        self.right_wheel_shape.group    = 1  # so that the wheels and the body do not collide with eachother
        
        self.space.add(self.right_wheel_b, self.right_wheel_shape)

        # Springs and Other Constraints
        self.rest_ln        = 25 # 20
        self.lift           = 25
        self.stiff          = 100 # 90
        self.damp           = .4 # .8
        self.wheel_base     = 34
        
        self.left_spring   = pymunk.constraint.DampedSpring(self.car_body, self.left_wheel_b, (-self.wheel_base, 0), (0,0), self.rest_ln, self.stiff, self.damp)
        self.right_spring  = pymunk.constraint.DampedSpring(self.car_body, self.right_wheel_b, (self.wheel_base, 0), (0,0), self.rest_ln, self.stiff, self.damp)

        self.left_groove    = pymunk.constraint.GrooveJoint(self.car_body, self.left_wheel_b, (-self.wheel_base, -5), (-self.wheel_base, -self.lift), (0,0))
        self.right_groove   = pymunk.constraint.GrooveJoint(self.car_body, self.right_wheel_b, (self.wheel_base, -5), (self.wheel_base, -self.lift), (0,0))

        self.space.add(self.left_spring, self.right_spring, self.left_groove, self.right_groove)


        self.player_sprite = loaders.spriteloader('truck.png', 
                                                  anchor=('center','center'),
                                                  anchor_offset=(7,-1),
                                                  scale = .5,
                                                  batch=level_batch,
                                                  group=ordered_group_lfg2,
                                                  linear_interpolation=True)

        self.wheel_sprite_l = loaders.spriteloader('wheel.png', 
                                                  anchor=('center','center'),
                                                  #anchor_offset=(7,-1),
                                                  scale = .5,
                                                  batch=level_batch,
                                                  group=ordered_group_lfg3,
                                                  linear_interpolation=True)

        self.wheel_sprite_r = loaders.spriteloader('wheel.png', 
                                                  anchor=('center','center'),
                                                  #anchor_offset=(7,-1),
                                                  scale = .5,
                                                  batch=level_batch,
                                                  group=ordered_group_lfg3,
                                                  linear_interpolation=True)


        self.suspension_sprite_l = loaders.spriteloader('suspension.png', 
                                                  anchor=('center',9),
                                                  #anchor_offset=(7,-1),
                                                  scale = .5,
                                                  batch=level_batch,
                                                  group=ordered_group_lfg,
                                                  linear_interpolation=True)

        self.suspension_sprite_r = loaders.spriteloader('suspension.png', 
                                                  anchor=('center',9),
                                                  #anchor_offset=(7,-1),
                                                  scale = .5,
                                                  batch=level_batch,
                                                  group=ordered_group_lfg,
                                                  linear_interpolation=True)

        self.band_debug = debug_batch.add(2, pyglet.gl.GL_LINES, ordered_group_lfg3,
                                          ('v2f'),
                                          ('c3B', (255,125,255)*2))


        self.mouseGrabbed = False
        self.grabFirstClick = True
        self.player_max_ang_vel = 100

    def force(self, body_to_impulse, impulse):
        self.impulse            = Vec2d(impulse)
        self.body_to_impulse    = body_to_impulse
        self.body_to_impulse.apply_impulse(self.impulse)

    def reset(self):
        self.car_body.position          = self.body_position
        self.car_body.velocity          = (0,0)
        self.car_body.angular_velocity  = 0
        self.car_body.angle             = 0

        self.left_wheel_b.position          = self.left_wheel_position
        self.left_wheel_b.velocity          = (0,0)
        self.left_wheel_b.angular_velocity  = 0
        self.left_wheel_b.angle             = 0

        self.right_wheel_b.position         = self.right_wheel_position
        self.right_wheel_b.velocity         = (0,0)
        self.right_wheel_b.angular_velocity = 0
        self.right_wheel_b.angle            = 0

    def mouse_grab_press(self, mouse_pos):
        if self.grabFirstClick == True:
            self.mouseBody = pymunk.Body()
            self.grabFirstClick = False
        print(mouse_pos)
        self.mouseBody.position = mouse_pos
        self.mouseGrabSpring = pymunk.constraint.DampedSpring(self.mouseBody, self.car_body, (0,0), (0,0), 0, 20, 1)
        self.space.add(self.mouseGrabSpring)
        self.mouseGrabbed = True
    def mouse_grab_drag(self, mouse_coords):
        if self.mouseGrabbed == True:
            self.mouseBody.position = mouse_coords
    def mouse_grab_release(self):
        if self.mouseGrabbed == True:
            self.space.remove(self.mouseGrabSpring)
            self.mouseGrabbed = False
    def update(self):
        if self.mouseGrabbed == True:
            self.band_debug.vertices = (self.mouseBody.position[0], self.mouseBody.position[1],self.car_body.position[0], self.car_body.position[1])
        else:
            self.band_debug.vertices = (0,0,0,0)
        
        self.sprite_x = 5*cos(self.car_body.angle-5) + self.car_body.position[0]
        self.sprite_y = 5*sin(self.car_body.angle-5) + self.car_body.position[1]
        self.player_sprite.set_position(self.sprite_x, self.sprite_y)

        self.player_sprite.rotation =  math.degrees(-self.car_body.angle)

        self.wheel_sprite_l.set_position(self.left_wheel_b.position[0], self.left_wheel_b.position[1])
        self.wheel_sprite_l.rotation = math.degrees(-self.left_wheel_b.angle)
        self.wheel_sprite_r.set_position(self.right_wheel_b.position[0], self.right_wheel_b.position[1])
        self.wheel_sprite_r.rotation = math.degrees(-self.right_wheel_b.angle)

        deltaYL = self.left_wheel_b.position[1] - self.car_body.position[1]
        deltaXL = self.left_wheel_b.position[0] - self.car_body.position[0]
        deltaYR = self.right_wheel_b.position[1] - self.car_body.position[1]
        deltaXR = self.right_wheel_b.position[0] - self.car_body.position[0]

        self.suspension_sprite_l.set_position(self.left_wheel_b.position[0], self.left_wheel_b.position[1])
        self.suspension_sprite_l.rotation = math.degrees(atan2(deltaYL,deltaXL)) *-1 - 90 #100 

        self.suspension_sprite_r.set_position(self.right_wheel_b.position[0], self.right_wheel_b.position[1])
        self.suspension_sprite_r.rotation = math.degrees(atan2(deltaYR,deltaXR)) *-1 - 90 #80


    def debug_draw(self):
        if self.mouseGrabbed == True:
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                ('v2f', ( self.mouseBody.position[0], self.mouseBody.position[1],self.car_body.position[0], self.car_body.position[1])),
                                ('c3B', (255,195,105)*2))
        for part in self.shape_list:
            self.box_verts = part.get_points()
            self.triangle_list = []
            for v in self.box_verts: # transforms a list of tuple coords (Vec2d(x,y),Vec2d(x,y), etc) 
                self.triangle_list.append(v.x) # to a list that pyglet can draw to [x,y, x,y, etc]
                self.triangle_list.append(v.y)
             # vehicle bb
            pyglet.graphics.draw(len(self.triangle_list)//2, pyglet.gl.GL_POLYGON,
                                ('v2f', self.triangle_list),
                                ('c4B', (250,20,20,100)*(len(self.triangle_list)//2))
                                )
            
            pyglet.graphics.draw(len(self.triangle_list)//2, pyglet.gl.GL_LINE_LOOP,
                                ('v2f', self.triangle_list),
                                ('c4B', (200,200,200,180)*(len(self.triangle_list)//2))
                                )

        self.lcircle.update(self.left_wheel_radius, self.left_wheel_b.angle, self.left_wheel_b.position)
        self.rcircle.update(self.right_wheel_radius, self.right_wheel_b.angle, self.right_wheel_b.position)
    
        #if self.car_body.is_sleeping: self.car_body.activate()

    def controls(self, keys_held):
        self.keys_held = keys_held
        if pyglet.window.key.LEFT in self.keys_held:
            self.car_body.angular_velocity += .65
        if pyglet.window.key.RIGHT in self.keys_held:
            self.car_body.angular_velocity -= .65

        if (pyglet.window.key.DOWN in self.keys_held and \
                    abs(self.left_wheel_b.angular_velocity) < self.player_max_ang_vel):
            if pyglet.window.key.LSHIFT in self.keys_held: # Boost
                self.left_wheel_b.angular_velocity += 6
            else: # Regular
                self.left_wheel_b.angular_velocity += 4
        if (pyglet.window.key.UP in self.keys_held and \
                    abs(self.left_wheel_b.angular_velocity) < self.player_max_ang_vel):
            if pyglet.window.key.LSHIFT in self.keys_held: # Boost
                self.left_wheel_b.angular_velocity -= 6
            else: # Regular
                self.left_wheel_b.angular_velocity -= 4

        if not pyglet.window.key.UP in self.keys_held and \
                    not pyglet.window.key.DOWN in self.keys_held:
            self.left_wheel_b.angular_velocity       *= .95 # fake friction for wheel 
            self.right_wheel_b.angular_velocity      *= .95

        if pyglet.window.key.LCTRL in self.keys_held:
            self.car_body.angular_velocity           *= 0.49      