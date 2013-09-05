import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import math
import levelassembler
import camera
from math import sin,cos
import particles2D
import loaders
import PiTweener

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

        '''
        image = levelassembler.imageloader(image, 'placeholder.png', (10,10))
        tex = image.get_texture()
        glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        self.sprite = pyglet.sprite.Sprite(image) # batch = level_batch, group = ordered_group)
        #self.sprite.image.width = size[0]
        #self.sprite.image.height = size[1]
        self.sprite.image.anchor_x = 4
        self.sprite.image.anchor_y = 0
        
        self.sprite.scale = .75
        '''
        self.sprite = loaders.spriteloader(image,
                                          anchor= (4,0),
                                          scale = .75,
                                          linear_interpolation = True)
        self.sprite.opacity = 0
        self.stage1 = True
        self.stage2 = False
        self.stage3 = False
        self.stage4 = False
        self.stage5 = False
        self.stage6 = False

        self.fangle = 0
        self.weighted_angle = 0

    def setup_pyglet_batch(self, debug_batch, level_batch,  ui_batch, ordered_group, screen_res):
        self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
        self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
                                            ('v2f', (self.left[0],self.left[1],
                                                     self.bottom[0],self.bottom[1],
                                                     self.right[0],self.right[1],
                                                     self.top[0],self.top[1])),
                                            ('c4B', (0,0,0,0)*4))

        self.sprite.batch = level_batch
        self.sprite.group = ordered_group

        self.fangle = 0
        self.sangle = 1.5
        self.flipped = False

    def update(self, player_pos, angle):

        x = 23*cos(angle+math.radians(90)) + player_pos[0]
        y = 23*sin(angle+math.radians(90)) + player_pos[1]
        self.sprite.set_position(x,y)
        self.weighted_angle = ((self.weighted_angle*(5-1))+angle) / 5
        self.sprite.rotation = math.degrees(-self.weighted_angle)

        if not self.bb.contains_vect(player_pos):
            self.bb_outline.colors = (self.color*4)

            if self.sprite.opacity != 0 or self.sprite.opacity >= 1:
                if self.sprite.opacity > 41:
                    self.sprite.opacity -= 30
                if self.sprite.opacity < 41:
                    self.sprite.opacity -= 10
                if self.sprite.opacity < 5:
                    self.sprite.opacity = 0

                if self.sprite.opacity > 10:
                    self.sprite.scale -= 0.02
                self.sangle = 1.5
                self.fangle = ((self.fangle*(20-1))+1.5) / 20
                self.sprite.rotation = math.degrees(self.fangle-self.weighted_angle)
            self.stage1 = True
            self.stage2 = False
            self.stage3 = False
            self.stage4 = False

        if self.bb.contains_vect(player_pos): 
            self.fangle = 0
            self.sangle = ((self.sangle*(5-1))+0) / 5
            self.sprite.rotation = math.degrees(self.sangle-self.weighted_angle)

            self.bb_outline.colors = (self.color2*4)
            if self.stage1:
                if self.sprite.opacity > 1:
                    self.sprite.scale += 0.04
                if self.sprite.scale > 1:
                    self.stage1 = False
                    self.stage2 = True
            if self.stage2:
                if self.sprite.scale > 1:
                    self.sprite.scale += 0.04
                if self.sprite.scale > 1.25:
                    self.stage2 = False
                    self.stage3 = True
            if self.stage3:
                if self.sprite.scale != 1:
                    if self.sprite.scale > 1:
                        self.sprite.scale -= 0.04
                    if self.sprite.scale < 1:
                        self.sprite.scale += 0.04
                    if self.sprite.scale == 1 or self.sprite.scale >= 1.0001:
                        self.stage3 = False
                        self.stage4 = True
            if self.stage4:
                if self.sprite.scale >= .88:
                    self.sprite.scale -= 0.03
                if self.sprite.scale < .88:
                    self.stage4 = False
                    self.stage5 = True
            if self.stage5:
                if self.sprite.scale != 1:
                    if self.sprite.scale > 1:
                        self.sprite.scale -= 0.02
                    if self.sprite.scale < 1:
                        self.sprite.scale += 0.02
                    if self.sprite.scale == 1 or self.sprite.scale >= 1.0001:
                        self.stage5 = False
                        self.stage6 = True
            if self.stage6:
                self.sprite.scale = 1
                self.stage6 = False
            #print(self.sprite.scale)

            if self.sprite.opacity != 255:
                if self.sprite.opacity < 234:
                    self.sprite.opacity += 15
                if self.sprite.opacity > 250:
                    self.sprite.opacity = 255

class Finish:
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
        
        self.sprite = loaders.spriteloader(image,
                                           anchor               = ('center', 'center'),
                                           #anchor_offset        = (0,-50)
                                           #scale                = 2,
                                           #linear_interpolation = True,
                                           )
        self.sprite.opacity = 0

        self.particle_emit = False

        self.fangle = 0
        self.weighted_angle = 0
        self.tweener = PiTweener.Tweener()

        self.finish_sound = loaders.Audio()
        self.finish_sound.load('resources/sounds/yay.ogg')

    def setup_pyglet_batch(self, debug_batch, level_batch, ui_batch, ordered_group, screen_res):
        self.outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], ('v2f'), ('c3B', (0,0,0)*4))
        self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, ordered_group, [0,1,1,2,2,3,3,0], 
                                            ('v2f', (self.left[0],self.left[1],
                                                     self.bottom[0],self.bottom[1],
                                                     self.right[0],self.right[1],
                                                     self.top[0],self.top[1])),
                                            ('c4B', (0,0,0,0)*4))

        self.screen_res = screen_res
        print(self.screen_res)
        self.sprite.set_position(screen_res[0]//2,screen_res[1]//2)
        self.sprite.batch = ui_batch
        self.sprite.group = ordered_group
        
        self.sprite_scale = .8
        self.sprite_opacity = 0
        self.added_tween = False


        self.fade_sprite_out = False
        self.wait_a_sec = 30

        self.emitter = particles2D.Emitter(pos = (screen_res[0]//2,-50))
        particle_img = pyglet.resource.image('confetti.png')
        self.factory = particles2D.finish_confetti(5,
                                                   ((-2,3),(5,7)),
                                                   particle_img,
                                                   batch=ui_batch,
                                                   group=ordered_group)

        self.emitter_spurt = particles2D.Spurt(self.emitter)

    def update(self, player_pos, angle):
        self.emitter_spurt.update()

        if not self.bb.contains_vect(player_pos):
            self.bb_outline.colors = (self.color*4)

        self.tweener.update()

        if self.bb.contains_vect(player_pos):
            self.particle_emit = True
            self.bb_outline.colors = (self.color2*4)
            if not self.added_tween:
                self.emitter_spurt.add_factory(self.factory, .001)

                self.finish_sound.play()
                
                self.added_tween = True
                self.tweener.add_tween(self,
                                       sprite_scale          = 1,
                                       sprite_opacity        = 255,
                                       tween_time            = 1,
                                       tween_type            = self.tweener.OUT_CUBIC,
                                       on_complete_function  = self.fade_out)

        if self.fade_sprite_out:
            if self.wait_a_sec > -1:
                self.wait_a_sec -= 1
            if self.wait_a_sec == 0:
                self.tweener.add_tween(self,
                                       sprite_scale          = 1.25,
                                       sprite_opacity        = 0,
                                       tween_time            = .5,
                                       tween_type            = self.tweener.OUT_CUBIC,)

        self.sprite.scale = self.sprite_scale
        self.sprite.opacity = self.sprite_opacity

    def fade_out(self):
        self.fade_sprite_out = True
