from math import sin,cos,sqrt
import pymunk
from pymunk import Vec2d
import pyglet

class PolygonJelly:
    def __init__ (self, space, points, stiffness):
        self.space = space
        self.stiffness = stiffness

        self.points = points
        self.list = []

        self.mass               = .02
        self.radius             = 5
        self.inertia            = pymunk.moment_for_circle(self.mass, 0, self.radius)

        for point in self.points:
            #print(point)
            self.body               = pymunk.Body(self.mass, self.inertia)
            self.body.position      = point
            self.shape              = pymunk.Circle(self.body, self.radius)
            self.shape.friction     = .2
            self.shape.group        = 7

            self.space.add(self.body, self.shape)
            self.list.append(self.body)

        list_item = 0
        for body in self.list[1:]:
            #print(body.position)
            distance = sqrt((self.list[list_item].position[0]-body.position[0])**2 + (body.position[1]-self.list[list_item].position[1])**2)
            print(distance)
            self.spring = pymunk.constraint.DampedSpring(body, self.list[list_item], (0,0), (0,0), distance, self.stiffness, .1)
            self.space.add(self.spring)
            list_item += 1

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