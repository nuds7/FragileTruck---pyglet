from math import sin,cos
import pymunk
import pyglet
class Jelly:
    def __init__ (self, space, radius, position, bounciness, group, color):
        self.space = space
        self.radius = radius
        self.color = color
        self.group = group
        self.bounciness = bounciness
        self.angle = 0
        self.angle_to_add = .45

        self.mass               = .05
        self.center_radius      = radius
        self.position           = position
        
        self.inertia            = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body               = pymunk.Body(self.mass, self.inertia)
        self.body.position      = self.position
        self.shape              = pymunk.Circle(self.body, self.radius)
        self.shape.friction     = .2
        self.shape.group        = self.group
        self.space.add(self.body, self.shape)
        
        self.list = []

        for i in range(14):
            self.part_mass          = .05
            self.part_radius        = 5
            
            self.position_x         = self.radius*cos(self.angle) + self.body.position[0]
            self.position_y         = self.radius*sin(self.angle) + self.body.position[1]

            self.new_position            = self.position_x, self.position_y
            self.part_inertia            = pymunk.moment_for_circle(self.part_mass, 0, self.part_radius)
            self.part_body               = pymunk.Body(self.part_mass, self.part_inertia)
            self.part_body.position      = self.new_position
            self.part_shape              = pymunk.Circle(self.part_body, self.part_radius)
            self.part_shape.friction     = 1
            self.part_shape.group        = self.group
            self.angle += self.angle_to_add

            self.space.add(self.part_body, self.part_shape)
            self.list.append(self.part_body)

            self.rest_ln = -1
            self.stiffness = self.bounciness # 10 for really bouncy, 1 for squishy as shit
            self.damp = .4
            self.spring = pymunk.constraint.DampedSpring(self.body, self.part_body, (self.position_x-self.body.position[0],self.position_y-self.body.position[1]), (0,0), self.rest_ln, self.stiffness, self.damp)
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

        