from math import sin,cos
import pymunk
import pyglet
from pyglet.gl import *

class Jelly:
    def __init__ (self, space, position, radius, bounciness, shape_group, color, batch, order_group):
        self.space = space
        self.radius = radius
        #self.color = color
        #self.group = group
        self.bounciness = bounciness
        #self.map_size = map_size
        self.angle = 0
        self.angle_to_add = .21

        self.mass               = 0.02
        self.center_radius      = 3
        self.position           = position
        
        self.inertia            = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body               = pymunk.Body(self.mass, self.inertia)
        self.body.position      = self.position
        self.shape              = pymunk.Circle(self.body, self.radius)
        self.shape.friction     = .2
        self.shape.group        = shape_group
        self.space.add(self.body, self.shape)
        
        self.list = []

        for i in range(30):
            self.part_mass          = .002
            self.part_radius        = 8
            
            self.position_x         = self.radius*cos(self.angle) + self.body.position[0]
            self.position_y         = self.radius*sin(self.angle) + self.body.position[1]

            self.new_position            = self.position_x, self.position_y
            self.part_inertia            = pymunk.moment_for_circle(self.part_mass, 0, self.part_radius)
            self.part_body               = pymunk.Body(self.part_mass, pymunk.inf)
            self.part_body.position      = self.new_position
            self.part_shape              = pymunk.Circle(self.part_body, self.part_radius)
            self.part_shape.friction     = .6
            self.part_shape.group        = shape_group
            self.angle += self.angle_to_add

            self.space.add(self.part_body, self.part_shape)
            self.list.append(self.part_body)

            self.rest_ln = self.radius
            self.stiffness = self.bounciness # 10 for really bouncy, 1 for squishy as shit
            self.damp = .006
            self.spring = pymunk.constraint.DampedSpring(self.body, self.part_body, (0,0), (0,0), self.rest_ln, self.stiffness, self.damp)
            self.slide = pymunk.constraint.GrooveJoint(self.body, self.part_body, (0,0), (self.position_x-self.body.position[0],self.position_y-self.body.position[1]), (0,0))

            self.space.add(self.spring, self.slide)
        
        self.jelly_fill = batch.add_indexed(31, pyglet.gl.GL_TRIANGLES, None,
                                        [0,1,2,
                                        0,2,3,
                                        0,3,4,
                                        0,4,5,
                                        0,5,6,
                                        0,6,7,
                                        0,7,8,
                                        0,8,9,
                                        0,9,10,
                                        0,10,11,
                                        0,11,12,
                                        0,12,13,
                                        0,13,14,
                                        0,14,15,
                                        0,15,16,
                                        0,16,17,
                                        0,17,18,
                                        0,18,19,
                                        0,19,20,
                                        0,20,21,
                                        0,21,22,
                                        0,22,23,
                                        0,23,24,
                                        0,24,25,
                                        0,25,26,
                                        0,26,27,
                                        0,27,28,
                                        0,28,29,
                                        0,29,30],
                                        ('v2f'),('c4B', (color)*31))
        
        self.jelly_outline = batch.add_indexed(30, pyglet.gl.GL_LINES, order_group, 
                                        [0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,
                                        8,9,9,10,10,11,11,12,12,13,13,14,
                                        14,15,15,16,16,17,17,18,18,19,19,
                                        20,20,21,21,22,22,23,23,24,24,25,
                                        25,26,26,27,27,28,28,29,29,0],
                                        ('v2f'), ('c4B',(0,0,0,200)*30),)


    def draw(self):
        # Change the outline color if the body is sleeping
        self.outline_color = (0,0,0)
        if self.part_body.is_sleeping: 
            self.outline_color = (255,0,0)
        else:
            self.point_list = []
            self.padding_angle = self.body.angle
            for self.part_body in self.list:
                '''# actual position of the parts of the jelly
                self.point_list.append(self.part_body.position[0])
                self.point_list.append(self.part_body.position[1])
                '''
                # Adding padding with the width of the parts of the jelly
                
                self.padded_x = self.part_radius*cos(self.padding_angle) + self.part_body.position[0]
                self.padded_y = self.part_radius*sin(self.padding_angle) + self.part_body.position[1]
                self.point_list.append(self.padded_x)
                self.point_list.append(self.padded_y)
                self.padding_angle += self.angle_to_add
                
                '''
                if self.part_body.position[1] < 0:
                    self.part_body.position[1] = self.part_radius + self.part_radius
                if self.part_body.position[0] < 0:
                    self.part_body.position[0] = self.part_radius + self.part_radius

                if self.part_body.position[1] > self.map_size[1]:
                    self.part_body.position[1] = self.map_size[1] - self.part_radius
                if self.part_body.position[0] > self.map_size[0]:
                    self.part_body.position[0] = self.map_size[0] - self.part_radius
                '''
        # Outline
        self.jelly_outline.vertices = self.point_list
        self.point_list.insert(0,self.body.position[1])
        self.point_list.insert(0,self.body.position[0])
        self.jelly_fill.vertices = self.point_list


class Jelly_Two:
    def __init__ (self, space, position, radius, bounciness, shape_group, color, batch, order_group):
        self.space = space
        self.radius = radius
        #self.color = color
        #self.group = group
        self.bounciness = bounciness
        #self.map_size = map_size
        self.angle = 0
        self.angle_to_add = .21

        self.mass               = 0.02
        self.center_radius      = 3
        self.position           = position
        
        self.inertia            = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body               = pymunk.Body(self.mass, self.inertia)
        self.body.position      = self.position
        self.shape              = pymunk.Circle(self.body, self.radius)
        self.shape.friction     = .2
        self.shape.group        = shape_group
        self.space.add(self.body)
        
        self.list = []

        for i in range(30):
            self.part_mass          = .002
            self.part_radius        = 8
            
            self.position_x         = self.radius*cos(self.angle) + self.body.position[0]
            self.position_y         = self.radius*sin(self.angle) + self.body.position[1]

            self.new_position            = self.position_x, self.position_y
            self.part_inertia            = pymunk.moment_for_circle(self.part_mass, 0, self.part_radius)
            self.part_body               = pymunk.Body(self.part_mass, pymunk.inf)
            self.part_body.position      = self.new_position
            self.part_shape              = pymunk.Circle(self.part_body, self.part_radius)
            self.part_shape.friction     = .6
            self.part_shape.group        = shape_group
            self.angle += self.angle_to_add

            self.space.add(self.part_body, self.part_shape)
            self.list.append(self.part_body)

            self.rest_ln = 0
            self.stiffness = self.bounciness # 10 for really bouncy, 1 for squishy as shit
            self.damp = .05
            self.spring = pymunk.constraint.DampedSpring(self.body, self.part_body, 
                                                        (self.position_x-self.body.position[0],self.position_y-self.body.position[1]), 
                                                        (0,0), self.rest_ln, self.stiffness, self.damp)
            #self.slide = pymunk.constraint.GrooveJoint(self.body, self.part_body, (0,0), (self.position_x-self.body.position[0],self.position_y-self.body.position[1]), (0,0))

            self.space.add(self.spring)
        
        self.jelly_fill = batch.add_indexed(31, pyglet.gl.GL_TRIANGLES, None,
                                        [0,1,2,
                                        0,2,3,
                                        0,3,4,
                                        0,4,5,
                                        0,5,6,
                                        0,6,7,
                                        0,7,8,
                                        0,8,9,
                                        0,9,10,
                                        0,10,11,
                                        0,11,12,
                                        0,12,13,
                                        0,13,14,
                                        0,14,15,
                                        0,15,16,
                                        0,16,17,
                                        0,17,18,
                                        0,18,19,
                                        0,19,20,
                                        0,20,21,
                                        0,21,22,
                                        0,22,23,
                                        0,23,24,
                                        0,24,25,
                                        0,25,26,
                                        0,26,27,
                                        0,27,28,
                                        0,28,29,
                                        0,29,30],
                                        ('v2f'),('c4B', (color)*31))
        
        self.jelly_outline = batch.add_indexed(30, pyglet.gl.GL_LINES, order_group, 
                                        [0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,
                                        8,9,9,10,10,11,11,12,12,13,13,14,
                                        14,15,15,16,16,17,17,18,18,19,19,
                                        20,20,21,21,22,22,23,23,24,24,25,
                                        25,26,26,27,27,28,28,29,29,0],
                                        ('v2f'), ('c4B',(0,0,0,200)*30),)


    def draw(self):
        # Change the outline color if the body is sleeping
        self.outline_color = (0,0,0)
        if self.part_body.is_sleeping: 
            self.outline_color = (255,0,0)
        else:
            self.point_list = []
            self.padding_angle = self.body.angle
            for self.part_body in self.list:
                '''# actual position of the parts of the jelly
                self.point_list.append(self.part_body.position[0])
                self.point_list.append(self.part_body.position[1])
                '''
                # Adding padding with the width of the parts of the jelly
                
                self.padded_x = self.part_radius*cos(self.padding_angle) + self.part_body.position[0]
                self.padded_y = self.part_radius*sin(self.padding_angle) + self.part_body.position[1]
                self.point_list.append(self.padded_x)
                self.point_list.append(self.padded_y)
                self.padding_angle += self.angle_to_add
                
                '''
                if self.part_body.position[1] < 0:
                    self.part_body.position[1] = self.part_radius + self.part_radius
                if self.part_body.position[0] < 0:
                    self.part_body.position[0] = self.part_radius + self.part_radius

                if self.part_body.position[1] > self.map_size[1]:
                    self.part_body.position[1] = self.map_size[1] - self.part_radius
                if self.part_body.position[0] > self.map_size[0]:
                    self.part_body.position[0] = self.map_size[0] - self.part_radius
                '''
        # Outline
        self.jelly_outline.vertices = self.point_list
        self.point_list.insert(0,self.body.position[1])
        self.point_list.insert(0,self.body.position[0])
        self.jelly_fill.vertices = self.point_list


class JellyTypeTwo:
    def __init__ (self, space, radius, position, bounciness, group, color, map_size, batch, order_group):
        self.space = space
        self.radius = radius
        self.color = color
        self.group = group
        self.bounciness = bounciness
        self.map_size = map_size
        self.angle = 0
        self.angle_to_add = .21

        self.mass               = 0.02
        self.center_radius      = 3
        self.position           = position
        
        self.inertia            = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body               = pymunk.Body(self.mass, self.inertia)
        self.body.position      = self.position
        self.shape              = pymunk.Circle(self.body, self.radius)
        self.shape.friction     = .2
        self.shape.group        = self.group
        self.space.add(self.body, self.shape)
        
        self.list = []

        for i in range(30):
            self.part_mass          = .002
            self.part_radius        = 8
            
            self.position_x         = self.radius*cos(self.angle) + self.body.position[0]
            self.position_y         = self.radius*sin(self.angle) + self.body.position[1]

            self.new_position            = self.position_x, self.position_y
            self.part_inertia            = pymunk.moment_for_circle(self.part_mass, 0, self.part_radius)
            self.part_body               = pymunk.Body(self.part_mass, pymunk.inf)
            self.part_body.position      = self.new_position
            self.part_shape              = pymunk.Circle(self.part_body, self.part_radius)
            self.part_shape.friction     = .6
            self.part_shape.group        = self.group
            self.angle += self.angle_to_add

            self.space.add(self.part_body, self.part_shape)
            self.list.append(self.part_body)

            self.rest_ln = 0
            self.stiffness = 10 # 10 for really bouncy, 1 for squishy as shit
            self.damp = .2
            self.spring = pymunk.constraint.DampedSpring(self.body, self.part_body, 
                                                        (self.position_x-self.body.position[0],self.position_y-self.body.position[1]), (0,0), 
                                                        self.rest_ln, self.stiffness, self.damp)
            #self.slide = pymunk.constraint.GrooveJoint(self.body, self.part_body, (0,0), (self.position_x-self.body.position[0],self.position_y-self.body.position[1]), (0,0))

            self.space.add(self.spring, self.slide)
        
        self.jelly_fill = batch.add_indexed(31, pyglet.gl.GL_TRIANGLES, order_group,
                                        [0,1,2,
                                        0,2,3,
                                        0,3,4,
                                        0,6,5,
                                        0,5,6],
                                        ('v2f'),('c4B'))
        
        self.jelly_outline = batch.add_indexed(30, pyglet.gl.GL_LINES, order_group, 
                                        [0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,
                                        8,9,9,10,10,11,11,12,12,13,13,14,
                                        14,15,15,16,16,17,17,18,18,19,19,
                                        20,20,21,21,22,22,23,23,24,24,25,
                                        25,26,26,27,27,28,28,29,29,0],
                                        ('v2f'), ('c3B',(0,0,0)*30),)


    def draw(self):
        # Change the outline color if the body is sleeping
        self.point_list = []
        self.padding_angle = self.body.angle
        for self.part_body in self.list:
            '''# actual position of the parts of the jelly
            self.point_list.append(self.part_body.position[0])
            self.point_list.append(self.part_body.position[1])
            '''
            # Adding padding with the width of the parts of the jelly
            self.padded_x = self.part_radius*cos(self.padding_angle) + self.part_body.position[0]
            self.padded_y = self.part_radius*sin(self.padding_angle) + self.part_body.position[1]
            self.point_list.append(self.padded_x)
            self.point_list.append(self.padded_y)
            self.padding_angle += self.angle_to_add
            
            if self.part_body.position[1] < 0:
                self.part_body.position[1] = self.part_radius + self.part_radius
            if self.part_body.position[0] < 0:
                self.part_body.position[0] = self.part_radius + self.part_radius
            if self.part_body.position[1] > self.map_size[1]:
                self.part_body.position[1] = self.map_size[1] - self.part_radius - 10
            if self.part_body.position[0] > self.map_size[0]:
                    self.part_body.position[0] = self.map_size[0] - self.part_radius
        # Outline
        self.jelly_outline.vertices = self.point_list
        #self.jelly_outline.colors = (self.outline_color*self.jelly_outline.count)