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

        for i in range(13):
            c = Circle(radius=self.radius, angle=self.angle, position=self.position, add=self.add)
            self.clist.append(c.x)
            self.clist.append(c.y)
            self.add += .5

        self.list_length = len(self.clist)//2
        if self.add > self.list_length/self.add:
            self.add = 0

        pyglet.graphics.draw(self.list_length, pyglet.gl.GL_LINE_STRIP,
                            ('v2f', (self.clist))
                            )

class Player:
    def __init__(self, space, body_position):
        self.space = space
        
        self.lcircle = Circle()
        self.rcircle = Circle()

        # body
        self.body_position      = body_position
        self.body_mass          = .9
        self.body_size          = (104,18) #(70,15)
        self.body_inertia       = pymunk.moment_for_box(self.body_mass, self.body_size[0], self.body_size[1])
        self.car_body           = pymunk.Body(self.body_mass, self.body_inertia)
        self.car_body.position  = self.body_position
        self.body_poly          = pymunk.Poly.create_box(self.car_body, self.body_size)
        self.body_poly.friction = 0.5
        self.body_poly.group    = 1  # so that the wheels and the body do not collide with eachother
        
        self.body2_position     = (self.body_position[0],self.body_position[1] + 20)
        self.body2_mass         = 1
        self.body2_size         = (15,35)
        self.body2_inertia      = pymunk.moment_for_box(self.body2_mass, self.body2_size[0], self.body2_size[1])
        self.body2_poly         = pymunk.Poly(self.car_body, ((-7,20),(7,20),(0,0)))
        self.body2_poly.friction= 0.5
        self.body2_poly.group   = 1  # so that the wheels and the body do not collide with eachother

        self.space.add(self.car_body, self.body_poly, self.body2_poly)

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

        ''' original setup
        self.left_spring   = pymunk.constraint.DampedSpring(self.car_body, self.left_wheel_b, (-self.body_size[0]//2, -10), (0,0), self.rest_ln, self.stiff, self.damp)
        self.right_spring  = pymunk.constraint.DampedSpring(self.car_body, self.right_wheel_b, (self.body_size[0]//2, -10), (0,0), self.rest_ln, self.stiff, self.damp)

        self.left_groove    = pymunk.constraint.GrooveJoint(self.car_body, self.left_wheel_b, (-self.body_size[0]//2, -20), (-self.body_size[0]//2, -30), (0,0))
        self.right_groove   = pymunk.constraint.GrooveJoint(self.car_body, self.right_wheel_b, (self.body_size[0]//2, -20), (self.body_size[0]//2, -30), (0,0))
        '''
        self.space.add(self.left_spring, self.right_spring, self.left_groove, self.right_groove)

        self.antenna_position       = (self.body_position[0] + 24, self.body_position[1] + 20)
        self.antenna_mass           = .005
        self.antenna_radius         = 1
        self.antenna_inertia        = pymunk.moment_for_circle(self.antenna_mass, 0, self.antenna_radius)
        self.antenna_body           = pymunk.Body(self.antenna_mass, self.antenna_inertia)
        self.antenna_body.position  = self.antenna_position
        self.antenna_poly           = pymunk.Circle(self.antenna_body, self.antenna_radius)
        self.antenna_poly.friction  = 0.5
        self.antenna_poly.group     = 1  # so that the wheels and the body do not collide with eachother

        self.antenna_spring         = pymunk.constraint.DampedSpring(self.car_body, self.antenna_body, (24,-10), (0,0), 40, 50, .5)
        self.antenna_slide          = pymunk.constraint.SlideJoint(self.car_body, self.antenna_body, (24,0), (0,0), 20, 25)


        self.space.add(self.antenna_body, self.antenna_poly, self.antenna_spring, self.antenna_slide)


        self.player_image = pyglet.resource.image("truck.png")
        self.player_image.anchor_x = self.player_image.width/2 + 1
        self.player_image.anchor_y = self.player_image.height/2
        self.player_sprite = pyglet.sprite.Sprite(self.player_image)
        #self.player_sprite.scale = .47

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

    def pyglet_draw(self, batch):
        self.batch = batch
        
        self.sprite_x = 5*cos(self.car_body.angle-5) + self.car_body.position[0]
        self.sprite_y = 5*sin(self.car_body.angle-5) + self.car_body.position[1]
        self.player_sprite.set_position(self.sprite_x, self.sprite_y)
        self.player_sprite.rotation =  math.degrees(-self.car_body.angle)
        self.player_sprite.draw()
        
        self.box_verts = self.body_poly.get_points()
        self.vertlist = []
        
        for v in self.box_verts: # transforms a list of tuple coords (Vec2d(x,y),Vec2d(x,y), etc) 
            self.vertlist.append(v.x) # to a list that pyglet can draw to [x,y, x,y, etc]
            self.vertlist.append(v.y)
         # vehicle bb
        '''
        pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP,
                            ('v2f', (self.vertlist)),
                            )
        '''
        

        self.lcircle.update(self.left_wheel_radius, self.left_wheel_b.angle, self.left_wheel_b.position)
        self.rcircle.update(self.right_wheel_radius, self.right_wheel_b.angle, self.right_wheel_b.position)

        '''
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
                            ('v2f', (self.antenna_body.position)))
        '''
        self.antenna_pos_x = 24*cos(self.car_body.angle) + self.car_body.position[0]
        self.antenna_pos_y = 24*sin(self.car_body.angle) + self.car_body.position[1]
        self.deltaX = self.antenna_body.position[0] - self.antenna_pos_x
        self.deltaY = self.antenna_body.position[1] - self.antenna_pos_y
        self.antenna_deg = atan2(self.deltaY,self.deltaX) * (-180/pi) + 90
        self.new_antenna_pos_x = 28*cos(self.car_body.angle + .24) + self.car_body.position[0]
        self.new_antenna_pos_y = 28*sin(self.car_body.angle + .24) + self.car_body.position[1]
        self.antenna_sprite.set_position(self.new_antenna_pos_x, self.new_antenna_pos_y)
        self.antenna_sprite.rotation = self.antenna_deg

        self.antenna_sprite.draw()