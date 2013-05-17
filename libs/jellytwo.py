from math import sin,cos
import pymunk
from pymunk import Vec2d
import pyglet
class Jelly:
    def __init__ (self, space, radius, position, bounciness, group, color):
        self.space = space
        self.radius = radius
        self.color = color
        self.group = group
        self.bounciness = bounciness
        self.angle = 0
        self.angle_to_add = .21

        self.mass               = .02
        self.center_radius      = radius
        self.position           = position
        
        self.inertia            = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body               = pymunk.Body(self.mass, self.inertia)
        self.body.position      = self.position
        self.shape              = pymunk.Circle(self.body, self.radius)
        self.shape.friction     = .2
        self.shape.group        = self.group
        self.space.add(self.body)
        
        self.list = []

        for i in range(30):
            self.part_mass          = .002
            self.part_radius        = 8
            
            self.position_x         = self.radius*cos(self.angle) + self.body.position[0]
            self.position_y         = self.radius*sin(self.angle) + self.body.position[1]

            self.new_position            = self.position_x, self.position_y
            self.part_inertia            = pymunk.moment_for_circle(self.part_mass, 0, self.part_radius)
            self.part_body               = pymunk.Body(self.part_mass, self.part_inertia)
            self.part_body.position      = self.new_position
            self.part_shape              = pymunk.Circle(self.part_body, self.part_radius)
            self.part_shape.friction     = .5
            self.part_shape.group        = self.group
            self.angle += self.angle_to_add

            self.space.add(self.part_body, self.part_shape)
            self.list.append(self.part_body)

            self.rest_ln = 0
            self.stiffness = self.bounciness # 10 for really bouncy, 1 for squishy as shit
            self.damp = .1
            self.spring = pymunk.constraint.DampedSpring(self.body, self.part_body, (self.position_x-self.body.position[0],self.position_y-self.body.position[1]), 
                                                        (0,0), self.rest_ln, self.stiffness, self.damp)
            #self.slide = pymunk.constraint.GrooveJoint(self.body, self.part_body, (0,0), (self.position_x-self.body.position[0],self.position_y-self.body.position[1]), (0,0))

            self.space.add(self.spring)


    def draw(self):
        self.point_list = []
        self.padding_angle = self.body.angle
        for self.part_body in self.list:
            ''' # actual position of the parts of the jelly
            self.point_list.append(self.part_body.position[0])
            self.point_list.append(self.part_body.position[1])
            '''
            # Adding padding with the width of the parts of the jelly
            self.padded_x = self.part_radius*cos(self.padding_angle) + self.part_body.position[0]
            self.padded_y = self.part_radius*sin(self.padding_angle) + self.part_body.position[1]
            self.point_list.append(self.padded_x)
            self.point_list.append(self.padded_y)
            self.padding_angle += self.angle_to_add
            self.part_body.angular_velocity *= 0.01

        self.point_list_length = len(self.point_list)//2

        pyglet.graphics.draw(self.point_list_length, pyglet.gl.GL_POLYGON,
                            ('v2f', self.point_list),
                            ('c4B', self.color*self.point_list_length)
                            )

        pyglet.graphics.draw(self.point_list_length, pyglet.gl.GL_LINE_LOOP,
                            ('v2f', self.point_list),
                            ('c4B', (0,0,0,140)*self.point_list_length)
                            )

        pyglet.graphics.draw(self.point_list_length, pyglet.gl.GL_POINTS,
                            ('v2f', self.point_list),
                            ('c3B', (255,255,255)*self.point_list_length)
                            )

class PolygonJelly:
    def __init__ (self, space, stiffness):
        self.space = space
        self.stiffness = stiffness

        self.list = []

        self.mass               = .02
        self.radius             = 5
        
        self.inertia            = pymunk.moment_for_circle(self.mass, 0, self.radius)

        self.body1               = pymunk.Body(self.mass, self.inertia)
        self.body1.position      = 300,310
        self.shape1              = pymunk.Circle(self.body1, self.radius)
        self.shape1.friction     = .2
        self.shape1.group        = 7

        self.space.add(self.body1, self.shape1)
        self.list.append(self.body1)

        self.body2               = pymunk.Body(self.mass, self.inertia)
        self.body2.position      = 270,270
        self.shape2              = pymunk.Circle(self.body2, self.radius)
        self.shape2.friction     = .2
        self.shape2.group        = 7

        self.space.add(self.body2, self.shape2)
        self.list.append(self.body2)

        self.body3               = pymunk.Body(self.mass, self.inertia)
        self.body3.position      = 330,270
        self.shape3              = pymunk.Circle(self.body3, self.radius)
        self.shape3.friction     = .2
        self.shape3.group        = 7

        self.space.add(self.body3, self.shape3)
        self.list.append(self.body3)

        self.list_item = 0

        for body in self.list[1:]:
            self.spring = pymunk.constraint.DampedSpring(body, self.list[self.list_item], (0,0), (0,0), 30, self.stiffness, .1)
            self.space.add(self.spring)
            self.list_item += 1

        self.spring = pymunk.constraint.DampedSpring(self.list[0], self.list[-1], (0,0), (0,0), 30, self.stiffness, .1)
        self.space.add(self.spring)
                

    def draw(self):
        self.point_list = []
        for body in self.list:
            self.point_list.append(body.position.x)
            self.point_list.append(body.position.y)

        self.point_list_length = len(self.point_list)//2

        pyglet.graphics.draw(self.point_list_length, pyglet.gl.GL_POLYGON,
                            ('v2f', self.point_list),
                            ('c4B', (124,124,250,140)*self.point_list_length)
                            )

        pyglet.graphics.draw(self.point_list_length, pyglet.gl.GL_LINE_LOOP,
                            ('v2f', self.point_list),
                            ('c4B', (0,0,0,140)*self.point_list_length)
                            )