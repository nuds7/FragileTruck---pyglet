import pyglet
#import pygame
import pymunk
from pymunk import Vec2d
import math
from math import sin,cos,atan2,pi    

        


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

        pyglet.graphics.draw(self.list_length, pyglet.gl.GL_LINE_STRIP,
                            ('v2f', (self.clist)),
                            ('c3B', (0,0,0)*self.list_length)
                            )

        

class Player:
    def __init__(self, space, body_position, map_size):
        self.space = space
        self.map_size = map_size
        
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
                        ((self.origin),(-52,2),(-56,-8),(50,-8)),
                        ((-56,-8),(-56,7),(-52,10),(-52,2)),
                        ]
        self.shape_list = []
        for part in self.parts:
            self.part = pymunk.Poly(self.car_body, part)
            self.part.friction = 0.5
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

        self.left_groove    = pymunk.constraint.GrooveJoint(self.car_body, self.left_wheel_b, (-self.wheel_base, -10), (-self.wheel_base, -self.lift), (0,0))
        self.right_groove   = pymunk.constraint.GrooveJoint(self.car_body, self.right_wheel_b, (self.wheel_base, -10), (self.wheel_base, -self.lift), (0,0))

        self.space.add(self.left_spring, self.right_spring, self.left_groove, self.right_groove)

        self.antenna_position       = (self.body_position[0] + 28, self.body_position[1] + 30)
        self.antenna_mass           = .001
        self.antenna_radius         = 1
        self.antenna_inertia        = pymunk.moment_for_circle(self.antenna_mass, 0, self.antenna_radius)
        self.antenna_body           = pymunk.Body(self.antenna_mass, self.antenna_inertia)
        self.antenna_body.position  = self.antenna_position
        self.antenna_poly           = pymunk.Circle(self.antenna_body, self.antenna_radius)
        self.antenna_poly.friction  = 0.5
        self.antenna_poly.group     = 1  # so that the wheels and the body do not collide with eachother

        self.antenna_spring         = pymunk.constraint.DampedSpring(self.car_body, self.antenna_body, (28,55), (0,0), 18, 4, .1)
        self.antenna_slide          = pymunk.constraint.SlideJoint(self.car_body, self.antenna_body, (28,0), (0,0), 25, 30)


        self.space.add(self.antenna_body, self.antenna_poly, self.antenna_spring, self.antenna_slide)


        self.player_image = pyglet.resource.image("truck2.png")
        self.player_image.anchor_x = self.player_image.width/2 + 1
        self.player_image.anchor_y = self.player_image.height/2
        self.player_sprite = pyglet.sprite.Sprite(self.player_image)
        self.player_sprite.scale = .5

        self.antenna_image = pyglet.resource.image("antenna.png")
        self.antenna_image.anchor_x = 4
        self.antenna_image.anchor_y = 3
        self.antenna_sprite = pyglet.sprite.Sprite(self.antenna_image)

        self.circle_angle_add = 0
        self.color_add = 0

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

        self.antenna_body.position = self.antenna_position
        self.antenna_body.velocity = (0,0)
        self.antenna_body.angular_velocity = 0
        self.antenna_body.angle = 0

    def draw(self, batch):
        self.batch = batch

        if self.car_body.position[1] < 0:
            self.car_body.position[1] = 5
        if self.car_body.position[1] > self.map_size[1]:
            self.car_body.position[1] = self.map_size[1] - self.body_size[1] - 30

        if self.left_wheel_b.position[1] < 0:
            self.left_wheel_b.position[1] = self.left_wheel_radius + 2
        if self.left_wheel_b.position[1] < 0:
            self.right_wheel_b.position[1] = self.right_wheel_radius + 2
        
        self.sprite_x = 5*cos(self.car_body.angle-5) + self.car_body.position[0]
        self.sprite_y = 5*sin(self.car_body.angle-5) + self.car_body.position[1]
        self.player_sprite.set_position(self.sprite_x, self.sprite_y)

        self.player_sprite.rotation =  math.degrees(-self.car_body.angle)
        self.player_sprite.draw()

        self.lcircle.update(self.left_wheel_radius, self.left_wheel_b.angle, self.left_wheel_b.position)
        self.rcircle.update(self.right_wheel_radius, self.right_wheel_b.angle, self.right_wheel_b.position)
        '''
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
                            ('v2f', (self.antenna_body.position)))
        '''
        self.antenna_pos_x = 28*cos(self.car_body.angle) + self.car_body.position[0]
        self.antenna_pos_y = 28*sin(self.car_body.angle) + self.car_body.position[1]
        self.deltaX = self.antenna_body.position[0] - self.antenna_pos_x
        self.deltaY = self.antenna_body.position[1] - self.antenna_pos_y
        self.antenna_deg = atan2(self.deltaY,self.deltaX) * (-180/pi) + 90
        self.new_antenna_pos_x = 30*cos(self.car_body.angle + .28) + self.car_body.position[0]
        self.new_antenna_pos_y = 30*sin(self.car_body.angle + .28) + self.car_body.position[1]
        self.antenna_sprite.set_position(self.new_antenna_pos_x, self.new_antenna_pos_y)
        self.antenna_sprite.rotation = self.antenna_deg

        self.antenna_sprite.draw()

        if self.car_body.is_sleeping: self.car_body.activate()

    def debug_draw(self):
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

        self.new_antenna_pos_x = 29*cos(self.car_body.angle + .28) + self.car_body.position[0]
        self.new_antenna_pos_y = 29*sin(self.car_body.angle + .28) + self.car_body.position[1]

        pyglet.graphics.draw(2, pyglet.gl.GL_LINE_LOOP,
                            ('v2f', (self.antenna_body.position[0],self.antenna_body.position[1],self.new_antenna_pos_x,self.new_antenna_pos_y)))

        if self.car_body.is_sleeping: self.car_body.activate()