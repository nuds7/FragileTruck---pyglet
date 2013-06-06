import pyglet
import pymunk
from pymunk import Vec2d
import math

class Elevator:
    def __init__(self, space, position, size, target, padding, speed, image, debug_batch, level_batch, ordered_group):
        self.speed = abs(speed)
        self.padding = padding
        padding_left = self.padding[0]
        padding_bottom = self.padding[1]
        padding_right = self.padding[2]
        padding_top = self.padding[3]
        self.target = target
        self.space = space
        self.position = position
        mass = 1
        self.body = pymunk.Body(mass, pymunk.inf)
        self.body.position = position
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.friction = 1
        self.shape.group = 2
        self.space.add(self.body, self.shape)

        self.top_body = pymunk.Body()
        self.top_body.position = self.body.position[0], self.body.position[1]

        joint = pymunk.constraint.PivotJoint(self.body, self.top_body, (0,0), (0,0))
        self.space.add(joint)

        if self.target > 0:
            left = (self.top_body.position[0] - size[0]//2 - padding_left, self.top_body.position[1] + padding_top + target)
            bottom = (self.top_body.position[0] - size[0]//2 - padding_left, self.top_body.position[1] - padding_bottom)
            right = (self.top_body.position[0] + size[0]//2 + padding_right, self.top_body.position[1] - padding_bottom)
            top = (self.top_body.position[0] + size[0]//2 + padding_right, self.top_body.position[1] + padding_top + target)
            self.bb = pymunk.BB(self.top_body.position[0] - size[0]//2 - padding_left,
                                self.top_body.position[1] - padding_bottom,
                                self.top_body.position[0] + size[0]//2 + padding_right,
                                self.top_body.position[1] + padding_top + target)
        if self.target < 0:
            left = (self.top_body.position[0] - size[0]//2 - padding_left, self.top_body.position[1] + padding_top)
            bottom = (self.top_body.position[0] - size[0]//2 - padding_left, self.top_body.position[1] - padding_bottom + target)
            right = (self.top_body.position[0] + size[0]//2 + padding_right, self.top_body.position[1] - padding_bottom + target)
            top = (self.top_body.position[0] + size[0]//2 + padding_right, self.top_body.position[1] + padding_top)
            self.bb = pymunk.BB(self.top_body.position[0] - size[0]//2 - padding_left,
                                self.top_body.position[1] - padding_bottom + target,
                                self.top_body.position[0] + size[0]//2 + padding_right,
                                self.top_body.position[1] + padding_top)
            self.speed *= -1

        self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
        self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
                                            ('v2f', (left[0],left[1],
                                                     bottom[0],bottom[1],
                                                     right[0],right[1],
                                                     top[0],top[1])),
                                            ('c3B', (0,0,0)*4))

        self.color = (200,0,0)
        self.color2 = (0,200,0)
        self.color3 = (200,200,0)

        #self.sprites = []
        elevatorImage = pyglet.resource.image(image)
        elevatorImage.anchor_x = elevatorImage.width/2
        elevatorImage.anchor_y = elevatorImage.height/2
        self.sprite = pyglet.sprite.Sprite(elevatorImage, batch = level_batch, group = ordered_group)
        self.sprite.scale = .5
        #self.sprites.append(sprite)

    def draw(self, player_pos):
        if not self.bb.contains_vect(player_pos):
            self.bb_outline.colors = (self.color*4)
        if self.bb.contains_vect(player_pos): 
            self.bb_outline.colors = (self.color2*4)
        #iterNum = 0
        #for bp in self.outlineList:
        self.pPoints = self.shape.get_points()
        self.p_list = []
        for point in self.pPoints:
            self.p_list.append(point.x)
            self.p_list.append(point.y)
        self.outline.vertices = self.p_list
        #self.fillList[iterNum].vertices = self.p_list
        #iterNum += 1

        self.sprite.set_position(self.body.position[0], self.body.position[1])
        self.sprite.rotation = math.degrees(-self.body.angle)

    def activate(self, player_pos):
        if self.bb.contains_vect(player_pos): 
            if self.target > 0:
                if self.top_body.position[1] < self.position[1] + self.target:
                    self.top_body.position[1] += self.speed
            if self.target < 0:
                if self.top_body.position[1] > self.position[1] + self.target:
                    self.top_body.position[1] += self.speed
    def deactivate(self, player_pos):
        if self.target > 0:
            if self.top_body.position[1] > self.position[1]:
                self.top_body.position[1] -= self.speed
        if self.target < 0:
            if self.top_body.position[1] < self.position[1]:
                self.top_body.position[1] -= self.speed

class ObjectPivot:
    def __init__(self, space, position, size, hinge_pos, 
                 padding, 
                 ang_vel, start, end, 
                 image, debug_batch, level_batch, ordered_group):
        self.padding = padding
        padding_left = self.padding[0]
        padding_bottom = self.padding[1]
        padding_right = self.padding[2]
        padding_top = self.padding[3]
        self.ang_vel = abs(ang_vel) # Refrain from using negative angular velocities, as it may give unexpected results.
        self.start = start + 57
        self.end = end + 57
        #self.force = force
        self.space = space
        mass = 3
        self.inertia = pymunk.moment_for_box(mass, size[0], size[1])
        self.body = pymunk.Body(mass, self.inertia)
        self.body.angle = math.radians(start) + math.radians(57)
        self.body.position = (position[0], position[1])
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.friction = 1
        self.shape.group = 2
        self.space.add(self.body, self.shape)

        self.hinge_body = pymunk.Body()
        self.hinge_body.angle = math.radians(start) + math.radians(57)
        self.hinge_body.position = self.body.position[0] + hinge_pos[0], self.body.position[1] + hinge_pos[1]

        pivot = pymunk.constraint.PivotJoint(self.body, self.hinge_body, (hinge_pos), (0,0))
        self.space.add(pivot)

        gear = pymunk.constraint.GearJoint(self.body, self.hinge_body, 1.0, 1.0)
        self.space.add(gear)

        left = (self.body.position[0] - size[0]//2 - padding_left, self.body.position[1] + padding_top)
        bottom = (self.body.position[0] - size[0]//2 - padding_left, self.body.position[1]- padding_bottom)
        right = (self.body.position[0] + size[0]//2 + padding_right, self.body.position[1]- padding_bottom)
        top = (self.body.position[0] + size[0]//2 + padding_right, self.body.position[1] + padding_top)

        self.bb = pymunk.BB(self.body.position[0] - size[0]//2 - padding_left,
                            self.body.position[1] - padding_bottom,
                            self.body.position[0] + size[0]//2 + padding_right,
                            self.body.position[1] + padding_top)

        self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
        self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
                                            ('v2f', (left[0],left[1],
                                                     bottom[0],bottom[1],
                                                     right[0],right[1],
                                                     top[0],top[1])),
                                            ('c3B', (0,0,0)*4))

        self.color = (200,0,0)
        self.color2 = (0,200,0)
        self.color3 = (200,200,0)

        objectPivotImage = pyglet.resource.image(image)
        objectPivotImage.anchor_x = objectPivotImage.width/2
        objectPivotImage.anchor_y = objectPivotImage.height/2
        self.sprite = pyglet.sprite.Sprite(objectPivotImage, batch = level_batch, group = ordered_group)
        self.sprite.scale = .5

    def draw(self, player_pos):

        self.bb_outline.colors = (self.color*4)
        if self.bb.contains_vect(player_pos): 
            self.bb_outline.colors = (self.color2*4)

        if self.body.position[1] >= self.hinge_body.position[1]:
            self.bb_outline.colors = (self.color3*4)
        #iterNum = 0
        #for bp in self.outlineList:
        self.pPoints = self.shape.get_points()
        self.p_list = []
        for point in self.pPoints:
            self.p_list.append(point.x)
            self.p_list.append(point.y)
        self.outline.vertices = self.p_list
        #self.fillList[iterNum].vertices = self.p_list
        #iterNum += 1

        self.sprite.set_position(self.body.position[0], self.body.position[1])
        self.sprite.rotation = math.degrees(-self.body.angle)

    def activate(self, player_pos):
        if self.bb.contains_vect(player_pos):
            if self.end - 57 > 0:
                if self.hinge_body.angle < math.radians(self.end):
                    self.hinge_body.angle += self.ang_vel
            if self.end - 57 < 0:
                if self.hinge_body.angle > math.radians(self.end):
                    self.hinge_body.angle -= self.ang_vel

    def deactivate(self, player_pos):
        if self.end - 57 > 0:
            if self.hinge_body.angle > math.radians(self.start):
                self.hinge_body.angle -= self.ang_vel
        if self.end - 57 < 0:
            if self.hinge_body.angle < math.radians(self.start):
                self.hinge_body.angle += self.ang_vel


class Flinger:
    def __init__(self, space, position, size, height, padding_left, padding_bottom, padding_right, padding_top, force, batch, ordered_group):
        self.force = force
        self.space = space
        mass = 5
        self.body = pymunk.Body(mass, pymunk.inf)
        self.body.position = (position[0], position[1])
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.friction = 1
        self.shape.group = 2
        self.space.add(self.body, self.shape)

        self.top_body = pymunk.Body()
        self.top_body.position = self.body.position[0], self.body.position[1] + height

        groove = pymunk.constraint.GrooveJoint(self.top_body, self.body, (0,0), (0,-height), (0,0))
        self.space.add(groove)

        left = (self.top_body.position[0] - size[0]//2 - padding_left, self.top_body.position[1] + padding_top)
        bottom = (self.body.position[0] - size[0]//2 - padding_left, self.body.position[1] - padding_bottom)
        right = (self.body.position[0] + size[0]//2 + padding_right, self.body.position[1] - padding_bottom)
        top = (self.top_body.position[0] + size[0]//2 + padding_right, self.top_body.position[1] + padding_top)

        self.bb = pymunk.BB(self.top_body.position[0] - size[0]//2 - padding_left,
                            self.body.position[1] - padding_bottom,
                            self.top_body.position[0] + size[0]//2 + padding_right,
                            self.top_body.position[1] + padding_top)

        self.outline = batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
        self.bb_outline = batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
                                            ('v2f', (left[0],left[1],
                                                     bottom[0],bottom[1],
                                                     right[0],right[1],
                                                     top[0],top[1])),
                                            ('c3B', (0,0,0)*4))

        self.color = (200,0,0)
        self.color2 = (0,200,0)
        self.color3 = (200,200,0)

    def draw(self, player_pos):

        self.bb_outline.colors = (self.color*4)
        if self.bb.contains_vect(player_pos): 
            self.bb_outline.colors = (self.color2*4)

        if self.body.position[1] >= self.top_body.position[1]:
            self.bb_outline.colors = (self.color3*4)
        #iterNum = 0
        #for bp in self.outlineList:
        self.pPoints = self.shape.get_points()
        self.p_list = []
        for point in self.pPoints:
            self.p_list.append(point.x)
            self.p_list.append(point.y)
        self.outline.vertices = self.p_list
        #self.fillList[iterNum].vertices = self.p_list
        #iterNum += 1

    def activate(self, player_pos):
        if self.bb.contains_vect(player_pos): 
            self.body.apply_impulse((0,self.force))
    def deactivate(self):
        pass