import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import math
import levelassembler
import camera
from math import sin,cos

class Hint:
    def __init__(self, position, padding, image):
        self.position = position
        self.padding = padding
        padding_left = self.padding[0]
        padding_bottom = self.padding[1]
        padding_right = self.padding[2]
        padding_top = self.padding[3]
        #self.text = text
        
        self.bb = pymunk.BB(position[0] - padding_left,
                            position[1] - padding_bottom,
                            position[0] + padding_right,
                            position[1] + padding_top)

        self.left = (position[0] -  padding_left, position[1] + padding_top)
        self.bottom = (position[0]  - padding_left, position[1] - padding_bottom)
        self.right = (position[0] + padding_right, position[1] - padding_bottom)
        self.top = (position[0] + padding_right, position[1] + padding_top)
        
        alpha = 200
        self.color = (200,0,0,alpha)
        self.color2 = (0,200,0,alpha)
        self.color3 = (200,200,0,alpha)


        image = levelassembler.imageloader(image, 'placeholder.png', (10,10))
        tex = image.get_texture()
        glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        self.sprite = pyglet.sprite.Sprite(image) # batch = level_batch, group = ordered_group)
        #self.sprite.image.width = size[0]
        #self.sprite.image.height = size[1]
        self.sprite.image.anchor_x = 4
        self.sprite.image.anchor_y = 0
        self.sprite.opacity = 0
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

    def update(self, player_pos, angle):

        x = 23*cos(angle+math.radians(90)) + player_pos[0]
        y = 23*sin(angle+math.radians(90)) + player_pos[1]
        self.sprite.set_position(x,y)
        self.sprite.rotation = math.degrees(-angle)


        if not self.bb.contains_vect(player_pos):
            self.bb_outline.colors = (self.color*4)

            if self.sprite.opacity != 0:
                if self.sprite.opacity > 11:
                    self.sprite.opacity -= 10
                if self.sprite.opacity < 11:
                    self.sprite.opacity -= 1

        if self.bb.contains_vect(player_pos): 
            self.bb_outline.colors = (self.color2*4)

            if self.sprite.opacity != 255:
                if self.sprite.opacity < 241:
                    self.sprite.opacity += 10
                if self.sprite.opacity > 241:
                    self.sprite.opacity += 1
