import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import math
import levelassembler

class Elevator:
    def __init__(self, space, position, size, target, padding, speed, image):
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
            self.left = (self.top_body.position[0] - size[0]//2 - padding_left, self.top_body.position[1] + padding_top + target)
            self.bottom = (self.top_body.position[0] - size[0]//2 - padding_left, self.top_body.position[1] - padding_bottom)
            self.right = (self.top_body.position[0] + size[0]//2 + padding_right, self.top_body.position[1] - padding_bottom)
            self.top = (self.top_body.position[0] + size[0]//2 + padding_right, self.top_body.position[1] + padding_top + target)
            self.bb = pymunk.BB(self.top_body.position[0] - size[0]//2 - padding_left,
                                self.top_body.position[1] - padding_bottom,
                                self.top_body.position[0] + size[0]//2 + padding_right,
                                self.top_body.position[1] + padding_top + target)
        if self.target < 0:
            self.left = (self.top_body.position[0] - size[0]//2 - padding_left, self.top_body.position[1] + padding_top)
            self.bottom = (self.top_body.position[0] - size[0]//2 - padding_left, self.top_body.position[1] - padding_bottom + target)
            self.right = (self.top_body.position[0] + size[0]//2 + padding_right, self.top_body.position[1] - padding_bottom + target)
            self.top = (self.top_body.position[0] + size[0]//2 + padding_right, self.top_body.position[1] + padding_top)
            self.bb = pymunk.BB(self.top_body.position[0] - size[0]//2 - padding_left,
                                self.top_body.position[1] - padding_bottom + target,
                                self.top_body.position[0] + size[0]//2 + padding_right,
                                self.top_body.position[1] + padding_top)
            self.speed *= -1
        
        alpha = 10
        self.color = (200,0,0,alpha)
        self.color2 = (0,200,0,alpha)
        self.color3 = (200,200,0,alpha)

        image = levelassembler.imageloader(image, 'placeholder.png', size)
        tex = image.get_texture()
        glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        self.sprite = pyglet.sprite.Sprite(image) # batch = level_batch, group = ordered_group)
        #self.sprite.image.width = size[0]
        #self.sprite.image.height = size[1]
        self.sprite.image.anchor_x = self.sprite.image.width//2
        self.sprite.image.anchor_y = self.sprite.image.height//2
        #self.sprite.scale = .5

    def setup_pyglet_batch(self, debug_batch, level_batch, ordered_group):
        self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
        self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
                                            ('v2f', (self.left[0],self.left[1],
                                                     self.bottom[0],self.bottom[1],
                                                     self.right[0],self.right[1],
                                                     self.top[0],self.top[1])),
                                            ('c4B', (0,0,0,0)*4))
        self.sprite.batch = level_batch
        self.sprite.group = ordered_group

    def update(self, player_pos, keys_held):

        if not self.bb.contains_vect(player_pos):
            self.bb_outline.colors = (self.color*4)
        if self.bb.contains_vect(player_pos): 
            self.bb_outline.colors = (self.color2*4)
        if self.target > 0:
            if self.top_body.position[1] >= self.position[1] + self.target - 2:
                self.bb_outline.colors = (self.color3*4)
        if self.target < 0:
            if self.top_body.position[1] <= self.position[1] + self.target + 2:
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
        if pyglet.window.key.SPACE in keys_held:
            if self.bb.contains_vect(player_pos): 
                if self.target > 0:
                    if self.top_body.position[1] < self.position[1] + self.target:
                        self.top_body.position[1] += self.speed
                if self.target < 0:
                    if self.top_body.position[1] > self.position[1] + self.target:
                        self.top_body.position[1] += self.speed
        else:
            if self.target > 0:
                if self.top_body.position[1] > self.position[1]:
                    self.top_body.position[1] -= self.speed
            if self.target < 0:
                if self.top_body.position[1] < self.position[1]:
                    self.top_body.position[1] -= self.speed
        if not self.bb.contains_vect(player_pos):
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
                 image):
        self.padding = padding
        padding_left = self.padding[0]
        padding_bottom = self.padding[1]
        padding_right = self.padding[2]
        padding_top = self.padding[3]
        self.ang_vel = abs(ang_vel) # Refrain from using negative angular velocities, as it may give unexpected results.
        self.start = start + 57
        self.end = end + 57
        self.size = size
        #self.force = force
        self.space = space
        mass = 3
        self.inertia = pymunk.moment_for_box(mass, size[0], size[1])
        self.body = pymunk.Body(mass, self.inertia)
        self.body.angle = math.radians(start)
        self.body.position = (position[0]-hinge_pos[0], position[1]-hinge_pos[1])
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

        self.left = (position[0] - padding_left, position[1] + padding_top)
        self.bottom = (position[0] - padding_left, position[1]- padding_bottom)
        self.right = (position[0] + padding_right, position[1]- padding_bottom)
        self.top = (position[0] + padding_right, position[1] + padding_top)

        self.bb = pymunk.BB(position[0] - padding_left, #- hinge_pos[0], # left
                            position[1] - padding_bottom, #  - hinge_pos[1], # bottom
                            position[0] + padding_right, # - hinge_pos[0], # right
                            position[1] + padding_top, ) # - hinge_pos[1]) # top
        alpha = 10
        self.color = (200,0,0,alpha)
        self.color2 = (0,200,0,alpha)
        self.color3 = (200,200,0,alpha)

        image = levelassembler.imageloader(image, 'placeholder.png', size)
        tex = image.get_texture()
        glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        self.sprite = pyglet.sprite.Sprite(image) # batch = level_batch, group = ordered_group)
        #self.sprite.image.width = size[0]
        #self.sprite.image.height = size[1]
        self.sprite.image.anchor_x = self.sprite.image.width//2
        self.sprite.image.anchor_y = self.sprite.image.height//2
        #self.sprite.scale = .5

    def setup_pyglet_batch(self, debug_batch, level_batch, ordered_group):
        self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
        self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
                                            ('v2f', (self.left[0],self.left[1],
                                                     self.bottom[0],self.bottom[1],
                                                     self.right[0],self.right[1],
                                                     self.top[0],self.top[1])),
                                            ('c4B', (0,0,0,0)*4))
        self.sprite.batch = level_batch
        self.sprite.group = ordered_group

    def update(self, player_pos, keys_held):

        self.bb_outline.colors = (self.color*4)
        if self.bb.contains_vect(player_pos): 
            self.bb_outline.colors = (self.color2*4)
        if self.end > 0.0001:
            if self.body.angle >= math.radians(self.end - 57 - 5):
                self.bb_outline.colors = (self.color3*4)
        if self.end < 0.0001:
            if self.body.angle <= math.radians(self.end - 57 + 5):
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

        if pyglet.window.key.SPACE in keys_held:
            if self.bb.contains_vect(player_pos):
                if self.end - 57 >= 0:
                    if self.hinge_body.angle < math.radians(self.end):
                        self.hinge_body.angle += self.ang_vel
                if self.end - 57 < 0:
                    if self.hinge_body.angle > math.radians(self.end):
                        self.hinge_body.angle -= self.ang_vel
        else:
            if self.end - 57 >= 0:
                if self.hinge_body.angle > math.radians(self.start):
                    self.hinge_body.angle -= self.ang_vel
            if self.end - 57 < 0:
                if self.hinge_body.angle < math.radians(self.start):
                    self.hinge_body.angle += self.ang_vel
        if not self.bb.contains_vect(player_pos):
            if self.end - 57 >= 0:
                if self.hinge_body.angle > math.radians(self.start):
                    self.hinge_body.angle -= self.ang_vel
            if self.end - 57 < 0:
                if self.hinge_body.angle < math.radians(self.start):
                    self.hinge_body.angle += self.ang_vel

class SpiralPivot:
    def __init__(self, space, position, hinge_pos, 
                 padding, 
                 ang_vel, start, end, 
                 image):
        self.padding = padding
        padding_left = self.padding[0]
        padding_bottom = self.padding[1]
        padding_right = self.padding[2]
        padding_top = self.padding[3]
        self.ang_vel = abs(ang_vel) # Refrain from using negative angular velocities, as it may give unexpected results.
        self.start = start + 57
        self.end = end + 57
        #size = 20,20
        #self.force = force
        self.space = space
        mass = 3
        #self.inertia = pymunk.moment_for_box(mass, size[0], size[1])
        
        '''
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.friction = 1
        self.shape.group = 2
        self.space.add(self.body, self.shape)
        '''
        self.body = pymunk.Body(pymunk.inf, pymunk.inf)
        self.body.angle = math.radians(start)
        self.shapelist = [
            pymunk.Segment(self.body, (333.9878888620935, 201.3931176121986), (324.543444417649, 201.3931176121986), 4),
            pymunk.Segment(self.body, (324.60529688755037, 201.4223178430688), (305.1608524431059, 204.14454006529104), 4),
            pymunk.Segment(self.body, (305.1608524431059, 204.14454006529104), (282.6052968875503, 215.8112067319577), 4),
            pymunk.Segment(self.body, (282.6052968875503, 215.8112067319577), (265.8830746653281, 235.25565117640218), 4),
            pymunk.Segment(self.body, (265.8830746653281, 235.25565117640218), (257.32751910977254, 264.42231784306887), 4),
            pymunk.Segment(self.body, (257.32751910977254, 264.42231784306887), (258.8830746653281, 289.7000956208467), 4),
            pymunk.Segment(self.body, (258.8830746653281, 289.7000956208467), (268.60529688755025, 311.0889845097356), 4),
            pymunk.Segment(self.body, (268.60529688755025, 311.0889845097356), (285.71640799866145, 327.4223178430689), 4),
            pymunk.Segment(self.body, (285.71640799866145, 327.4223178430689), (312.9386302208837, 338.70009562084675), 4),
            pymunk.Segment(self.body, (312.9386302208837, 338.70009562084675), (347.1608524431059, 339.0889845097356), 4),
            pymunk.Segment(self.body, (347.1608524431059, 339.0889845097356), (381.3830746653282, 331.31120673195784), 4),
            pymunk.Segment(self.body, (381.3830746653282, 331.31120673195784), (412.8830746653282, 312.64454006529115), 4),
            pymunk.Segment(self.body, (412.8830746653282, 312.64454006529115), (440.8830746653283, 284.64454006529115), 4),
            pymunk.Segment(self.body, (440.8830746653283, 284.64454006529115), (459.93863022088385, 251.58898450973552), 4),
            pymunk.Segment(self.body, (459.93863022088385, 251.58898450973552), (468.8830746653283, 219.31120673195772), 4),
            pymunk.Segment(self.body, (468.8830746653283, 219.31120673195772), (467.7164079986617, 180.42231784306878), 4),
            pymunk.Segment(self.body, (467.7164079986617, 180.42231784306878), (457.6052968875505, 146.9778733986243), 4),
            pymunk.Segment(self.body, (457.6052968875505, 146.9778733986243), (442.43863022088385, 119.75565117640204), 4),
            pymunk.Segment(self.body, (442.43863022088385, 119.75565117640204), (410.54974133199494, 89.03342895417978), 4),
            pymunk.Segment(self.body, (410.54974133199494, 89.03342895417978), (378.660852443106, 72.31120673195754), 4),
            pymunk.Segment(self.body, (378.660852443106, 72.31120673195754), (332.38307466532814, 64.14454006529087), 4)
            ]

        
        self.body.position = (self.shapelist[0].a)#(position[0]-hinge_pos[0], position[1]-hinge_pos[1])
        self.seg_list = []

        for shape in self.shapelist:
            s = shape
            s.a[0] -= self.body.position[0]
            s.a[1] -= self.body.position[1]
            s.b[0] -= self.body.position[0]
            s.b[1] -= self.body.position[1]
            s.friction = 1
            s.group = 2
            self.seg_list.append(s)
        self.space.add(self.body, self.shapelist)

        self.hinge_body = pymunk.Body()
        self.hinge_body.angle = math.radians(start) + math.radians(57)
        self.hinge_body.position = self.body.position[0] + hinge_pos[0], self.body.position[1] + hinge_pos[1]

        pivot = pymunk.constraint.PivotJoint(self.body, self.hinge_body, (hinge_pos), (0,0))
        self.space.add(pivot)

        gear = pymunk.constraint.GearJoint(self.body, self.hinge_body, 1.0, 1.0)
        self.space.add(gear)

        self.left = (position[0] - padding_left, position[1] + padding_top)
        self.bottom = (position[0] - padding_left, position[1]- padding_bottom)
        self.right = (position[0] + padding_right, position[1]- padding_bottom)
        self.top = (position[0] + padding_right, position[1] + padding_top)

        self.bb = pymunk.BB(position[0] - padding_left, #- hinge_pos[0], # left
                            position[1] - padding_bottom, #  - hinge_pos[1], # bottom
                            position[0] + padding_right, # - hinge_pos[0], # right
                            position[1] + padding_top, ) # - hinge_pos[1]) # top
        
        self.color = (200,0,0)
        self.color2 = (0,200,0)
        self.color3 = (200,200,0)
        
        image = levelassembler.imageloader(image, 'placeholder.png', (10,10))
        tex = image.get_texture()
        glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        self.sprite = pyglet.sprite.Sprite(image) # batch = level_batch, group = ordered_group)
        #self.sprite.image.width = size[0]
        #self.sprite.image.height = size[1]
        self.sprite.image.anchor_x = 82
        self.sprite.image.anchor_y = 140
        #self.sprite.scale = .5
        

    def setup_pyglet_batch(self, debug_batch, level_batch, ordered_group):
        '''
        self.point_list = []
        for point in self.seg_list:
            self.point_list.append(point.a[0])
            self.point_list.append(point.a[1])
            self.point_list.append(point.b[0])
            self.point_list.append(point.b[1])
        '''
        self.outline = debug_batch.add(2, pyglet.gl.GL_LINES, ordered_group, ('v2f'), ('c3B', (0,0,0)*2))
        self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
                                            ('v2f', (self.left[0],self.left[1],
                                                     self.bottom[0],self.bottom[1],
                                                     self.right[0],self.right[1],
                                                     self.top[0],self.top[1])),
                                            ('c3B', (0,0,0)*4))
        self.sprite.batch = level_batch
        self.sprite.group = ordered_group
        

    def update(self, player_pos, keys_held):

        self.point_list = []
        for point in self.seg_list:
            pv1 = point.a.rotated(self.body.angle) + self.body.position
            pv2 = point.b.rotated(self.body.angle) + self.body.position
            self.point_list.append(pv1[0])
            self.point_list.append(pv1[1])
            self.point_list.append(pv2[0])
            self.point_list.append(pv2[1])
            #self.point_list.append(point.a[0] + self.body.position[0])
            #self.point_list.append(point.a[1] + self.body.position[1])
            #self.point_list.append(point.b[0] + self.body.position[0])
            #self.point_list.append(point.b[1] + self.body.position[1])
        #print(self.point_list)
        self.outline.resize(len(self.point_list)//2)
        self.outline.vertices = self.point_list #('v2f', self.point_list)
        self.outline.colors = (0,0,0,100,180,250)*(len(self.point_list)//4)
        
        self.bb_outline.colors = (self.color*4)
        if self.bb.contains_vect(player_pos): 
            self.bb_outline.colors = (self.color2*4)
        if self.end > 0:
            if self.body.angle >= math.radians(self.end - 57 - 5):
                self.bb_outline.colors = (self.color3*4)
        if self.end < 0:
            if self.body.angle <= math.radians(self.end - 57 + 5):
                self.bb_outline.colors = (self.color3*4)
        #print(self.body.angle)
        #iterNum = 0
        #for bp in self.outlineList:
        '''
        self.pPoints = self.shape.get_points()
        self.p_list = []
        for point in self.pPoints:
            self.p_list.append(point.x)
            self.p_list.append(point.y)
        self.outline.vertices = self.p_list
        #self.fillList[iterNum].vertices = self.p_list
        
        #iterNum += 1
        '''

        self.sprite.set_position(self.body.position[0], self.body.position[1])
        self.sprite.rotation = math.degrees(-self.body.angle)
        

        if pyglet.window.key.SPACE in keys_held:
            if self.bb.contains_vect(player_pos):
                if self.end - 57 >= 0:
                    if self.hinge_body.angle < math.radians(self.end):
                        self.hinge_body.angle += self.ang_vel
                if self.end - 57 < 0:
                    if self.hinge_body.angle > math.radians(self.end):
                        self.hinge_body.angle -= self.ang_vel
        else:
            if self.end - 57 >= 0:
                if self.hinge_body.angle > math.radians(self.start):
                    self.hinge_body.angle -= self.ang_vel
            if self.end - 57 < 0:
                if self.hinge_body.angle < math.radians(self.start):
                    self.hinge_body.angle += self.ang_vel
        if not self.bb.contains_vect(player_pos):
            if self.end - 57 >= 0:
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