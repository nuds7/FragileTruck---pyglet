from math import sin,cos,sqrt
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

class JellyThree:
    def __init__ (self, space, radius, position, stiffness):
        self.space = space
        self.stiffness = stiffness
        self.angle = 0
        self.angle_to_add = .21
        self.radius = radius
        self.position = position

        self.list = []

        self.mass               = .02
        self.shape_radius       = 5
        self.inertia            = pymunk.moment_for_circle(self.mass, 0, self.radius)

        for i in range(30):
            self.position_x         = self.radius*cos(self.angle) + self.position[0]
            self.position_y         = self.radius*sin(self.angle) + self.position[1]
            self.new_position       = self.position_x, self.position_y

            self.body               = pymunk.Body(self.mass, self.inertia)
            self.body.position      = self.new_position
            self.shape              = pymunk.Circle(self.body, self.shape_radius)
            self.shape.friction     = .5
            self.shape.group        = 8
            self.angle += self.angle_to_add

            self.space.add(self.body, self.shape)
            self.list.append(self.body)
        
        list_item = 0
        for body in self.list[1:]:
            #print(body.position)
            distance = sqrt((self.list[list_item].position[0]-body.position[0])**2 + (body.position[1]-self.list[list_item].position[1])**2)
            print(distance)
            self.slide = pymunk.constraint.SlideJoint(body, self.list[list_item], (0,0), (0,0), 3, distance)
            self.space.add(self.slide)
            list_item += 1

        '''
        list_item_tri = 0
        if len(self.list) > 3:
            for body in self.list[2:]:
                print(body.position)
                print(self.list[list_item_tri].position)
                distance = sqrt( (self.list[list_item_tri].position[0]-body.position[0])**2 + (self.list[list_item_tri].position[1]-body.position[1])**2 )
                print(distance)
                self.spring = pymunk.constraint.DampedSpring(body, self.list[list_item_tri], (0,0), (0,0), distance, self.stiffness, .1)
                self.space.add(self.spring)
                list_item_tri += 1
        '''

        list_item_opposite = int(len(self.list)*-.5)
        if len(self.list) > 3:
            for body in self.list:
                #print(body.position)
                #print(self.list[list_item_opposite].position)
                distance = sqrt( (self.list[list_item_opposite].position[0]-body.position[0])**2 + (self.list[list_item_opposite].position[1]-body.position[1])**2 )
                print(distance)
                self.spring = pymunk.constraint.DampedSpring(body, self.list[list_item_opposite], (0,0), (0,0), distance, self.stiffness, .1)
                self.space.add(self.spring)
                print(list_item_opposite)
                
                if list_item_opposite >= -29 and list_item_opposite <= -15:
                    list_item_opposite -= 1
                if list_item_opposite >= 0:
                    list_item_opposite += 1
                if list_item_opposite == -len(self.list):
                    list_item_opposite = 0

        list_item_opposite = int(len(self.list)*-.5) + 1
        if len(self.list) > 3:
            for body in self.list:
                #print(body.position)
                #print(self.list[list_item_opposite].position)
                distance = sqrt( (self.list[list_item_opposite].position[0]-body.position[0])**2 + (self.list[list_item_opposite].position[1]-body.position[1])**2 )
                print(distance)
                self.spring = pymunk.constraint.DampedSpring(body, self.list[list_item_opposite], (0,0), (0,0), distance, self.stiffness, .1)
                self.space.add(self.spring)
                print(list_item_opposite)
                
                if list_item_opposite >= -29 and list_item_opposite <= -16:
                    list_item_opposite -= 1
                if list_item_opposite >= 0:
                    list_item_opposite += 1
                if list_item_opposite == -len(self.list):
                    list_item_opposite = 0

        list_item_opposite = int(len(self.list)*-.5) - 1
        if len(self.list) > 3:
            for body in self.list:
                #print(body.position)
                #print(self.list[list_item_opposite].position)
                distance = sqrt( (self.list[list_item_opposite].position[0]-body.position[0])**2 + (self.list[list_item_opposite].position[1]-body.position[1])**2 )
                print(distance)
                self.spring = pymunk.constraint.DampedSpring(body, self.list[list_item_opposite], (0,0), (0,0), distance, self.stiffness, .1)
                self.space.add(self.spring)
                print(list_item_opposite)
                
                if list_item_opposite >= -29 and list_item_opposite <= -14:
                    list_item_opposite -= 1
                if list_item_opposite >= 0:
                    list_item_opposite += 1
                if list_item_opposite == -len(self.list):
                    list_item_opposite = 0

        distance = sqrt((self.list[-1].position[0]-self.list[0].position[0])**2 + (self.list[-1].position[1]-self.list[0].position[1])**2)
        self.spring = pymunk.constraint.DampedSpring(self.list[0], self.list[-1], (0,0), (0,0), distance, self.stiffness, .1)
        self.space.add(self.spring)

        distance = sqrt((self.list[-2].position[0]-self.list[0].position[0])**2 + (self.list[-2].position[1]-self.list[0].position[1])**2)
        self.spring = pymunk.constraint.DampedSpring(self.list[0], self.list[-2], (0,0), (0,0), distance, self.stiffness, .1)
        self.space.add(self.spring)

    def draw(self):
        self.point_list = []
        list_item = 1
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