import pyglet
from pyglet.gl import *
#import pygame
import pymunk
from pymunk import Vec2d
import math
from math import sin,cos,atan2,pi    
import levelassembler
import loaders

class Truck(object):
    def __init__(self,
                 space,
                 starting_pos,
                 level_batch,
                 debug_batch,
                 ui_batch,
                 lfg,
                 lfg2,
                 lfg3,):
        self.space = space
        self.starting_pos = starting_pos
        ## Chassis
        chassis_inertia = pymunk.moment_for_box(.9, 104, 18)
        self.chassis_body = pymunk.Body(.9,chassis_inertia)
        self.chassis_body.position = starting_pos
        self.chassis_body.group = 1
        space.add(self.chassis_body)
        origin = (0,0)
        self.parts =    [
                        ((origin),(-8,13),(10,14),(21,4)),
                        ((origin),(21,4),(47,2),(50,-14)),
                        ((origin),(50,-14),(-56,-13),(-14,-3)),
                        ((-56,-13),(-57,2),(-52,2),(-52,-3)),
                        ((-56,-13),(-52,-3),(-14,-3)),
                        ((origin),(-14,-3),(-8,13))
                        ]

        self.shape_list = []
        for part in self.parts:
            self.part = pymunk.Poly(self.chassis_body, part)
            self.part.friction = 0.3 #0.5
            self.part.group    = 1  # so that the wheels and the body do not collide with eachother
            self.space.add(self.part)
            self.shape_list.append(self.part)
        self.outlines = []
        for shape in self.shape_list:
            s_points = shape.get_points()
            if len(s_points) < 4:
                self.tri_outline = debug_batch.add_indexed(3, pyglet.gl.GL_LINES, None, [0,1,1,2,2,0], ('v2f'), ('c4B', (0,120,0,220)*3))
                self.outlines.append(self.tri_outline)
            elif len(s_points) == 4:
                self.quad_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, None, [0,1,1,2,2,3,3,0], ('v2f'), ('c4B', (0,120,0,220)*4))
                self.outlines.append(self.quad_outline)

        ## End Chassis
        ## Wheels
        wheel_mass = .3
        wheel_radius = 13
        wheel_inertia = pymunk.moment_for_circle(wheel_mass, 0, wheel_radius)
        wheel_friction = 1.8
        # L
        l_wheel_base  = 35
        l_wheel_pos                 = (starting_pos[0]-l_wheel_base+wheel_radius,starting_pos[1]-18-wheel_radius)
        self.l_wheel_body           = pymunk.Body(wheel_mass, wheel_inertia)
        self.l_wheel_body.position  = l_wheel_pos
        self.l_wheel_shape          = pymunk.Circle(self.l_wheel_body, wheel_radius)
        self.l_wheel_shape.friction = wheel_friction
        self.l_wheel_shape.group    = 1
        space.add(self.l_wheel_body,self.l_wheel_shape)
        # R
        r_wheel_base = 33
        r_wheel_pos                 = (starting_pos[0]+r_wheel_base-wheel_radius,starting_pos[1]-18-wheel_radius)
        self.r_wheel_body           = pymunk.Body(wheel_mass, wheel_inertia)
        self.r_wheel_body.position  = r_wheel_pos
        self.r_wheel_shape          = pymunk.Circle(self.r_wheel_body, wheel_radius)
        self.r_wheel_shape.friction = wheel_friction
        self.r_wheel_shape.group    = 1
        space.add(self.r_wheel_body,self.r_wheel_shape)
        ## End Wheels
        ## Constraints
        rest_ln     = 25  # 25
        lift        = 25  # 25
        stiff       = 110 # 100
        damp        = .4  # .4

        left_spring   = pymunk.constraint.DampedSpring(self.chassis_body, self.l_wheel_body, (-l_wheel_base, 0),  (0,0), rest_ln, stiff, damp)
        right_spring  = pymunk.constraint.DampedSpring(self.chassis_body, self.r_wheel_body, (r_wheel_base, 0),   (0,0), rest_ln, stiff, damp)

        left_groove    = pymunk.constraint.GrooveJoint(self.chassis_body, self.l_wheel_body, (-l_wheel_base, -5), (-l_wheel_base, -lift),   (0,0))
        right_groove   = pymunk.constraint.GrooveJoint(self.chassis_body, self.r_wheel_body, (r_wheel_base, -5),  (r_wheel_base, -lift),    (0,0))

        space.add(left_spring,left_groove,right_spring,right_groove)
        ##
        ## Sprites
        self.truck_sprite = loaders.spriteloader('truck.png', 
                                                 anchor=('center','center'),
                                                 anchor_offset=(7,0),
                                                 scale = .5,
                                                 batch=level_batch,
                                                 group=lfg2,
                                                 #linear_interpolation=True
                                                 )
        self.l_wheel_sprite = loaders.spriteloader('wheel.png', 
                                                  anchor=('center','center'),
                                                  scale = .5,
                                                  batch=level_batch,
                                                  group=lfg3,
                                                  #linear_interpolation=True
                                                  )
        self.r_wheel_sprite = loaders.spriteloader('wheel.png', 
                                                  anchor=('center','center'),
                                                  scale = .5,
                                                  batch=level_batch,
                                                  group=lfg3,
                                                  #linear_interpolation=True
                                                  )
        self.l_sus_sprite = loaders.spriteloader('suspension.png', 
                                                 anchor=('center',9),
                                                 scale = .5,
                                                 batch=level_batch,
                                                 group=lfg,
                                                 #linear_interpolation=True
                                                 )
        self.r_sus_sprite = loaders.spriteloader('suspension.png', 
                                                 anchor=('center',9),
                                                 scale = .5,
                                                 batch=level_batch,
                                                 group=lfg,
                                                 #linear_interpolation=True
                                                 )
        ##
        self.accel_amount       = 4
        self.player_max_ang_vel = 100
        self.mouseGrabbed       = False
        self.grabFirstClick     = True
    def update(self):
        iter_num = 0
        for shape in self.shape_list:
            s_points = shape.get_points()
            verts = []
            for point in s_points:
                verts.append(point.x)
                verts.append(point.y)
            if len(s_points) < 4:
                self.outlines[iter_num].vertices = verts
            elif len(s_points) == 4:
                self.outlines[iter_num].vertices = verts
            iter_num += 1

        self.l_wheel_sprite.set_position(self.l_wheel_body.position[0], self.l_wheel_body.position[1])
        self.l_wheel_sprite.rotation = math.degrees(-self.l_wheel_body.angle)
        self.r_wheel_sprite.set_position(self.r_wheel_body.position[0], self.r_wheel_body.position[1])
        self.r_wheel_sprite.rotation = math.degrees(-self.r_wheel_body.angle)

        #sprite_x = 5*cos(self.chassis_body.angle-5) + self.chassis_body.position[0]
        #sprite_y = 5*sin(self.chassis_body.angle-5) + self.chassis_body.position[1]

        self.truck_sprite.set_position(self.chassis_body.position[0],self.chassis_body.position[1])
        self.truck_sprite.rotation = math.degrees(-self.chassis_body.angle)
    def controls(self, keys_held):
        self.keys_held = keys_held
        if pyglet.window.key.LEFT in self.keys_held:
            self.chassis_body.angular_velocity += .65
        if pyglet.window.key.RIGHT in self.keys_held:
            self.chassis_body.angular_velocity -= .65
        if pyglet.window.key.LCTRL in self.keys_held:
            self.chassis_body.angular_velocity *= 0.49

        if (pyglet.window.key.DOWN in self.keys_held and \
                    abs(self.l_wheel_body.angular_velocity) < self.player_max_ang_vel):
            if pyglet.window.key.LSHIFT in self.keys_held: # Boost
                self.l_wheel_body.angular_velocity += 6
            else: # Regular
                self.l_wheel_body.angular_velocity += self.accel_amount

        if (pyglet.window.key.UP in self.keys_held and \
                    abs(self.l_wheel_body.angular_velocity) < self.player_max_ang_vel):
            if pyglet.window.key.LSHIFT in self.keys_held: # Boost
                self.l_wheel_body.angular_velocity -= 6
            else: # Regular
                self.l_wheel_body.angular_velocity -= self.accel_amount

        if not pyglet.window.key.UP in self.keys_held and \
                    not pyglet.window.key.DOWN in self.keys_held:
            self.l_wheel_body.angular_velocity *= .95 # fake friction for wheels
            self.r_wheel_body.angular_velocity *= .95

    def mouse_grab_press(self, mouse_pos):
        if self.grabFirstClick == True:
            self.mouseBody = pymunk.Body()
            self.grabFirstClick = False
        print(mouse_pos)
        self.mouseBody.position = mouse_pos
        self.mouseGrabSpring = pymunk.constraint.DampedSpring(self.mouseBody, self.chassis_body, (0,0), (0,0), 0, 20, 1)
        self.space.add(self.mouseGrabSpring)
        self.mouseGrabbed = True
    def mouse_grab_drag(self, mouse_coords):
        if self.mouseGrabbed == True:
            self.mouseBody.position = mouse_coords
    def mouse_grab_release(self):
        if self.mouseGrabbed == True:
            self.space.remove(self.mouseGrabSpring)
            self.mouseGrabbed = False
