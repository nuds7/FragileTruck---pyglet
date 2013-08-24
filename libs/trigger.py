import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import math
import levelassembler
import camera
from math import sin,cos
import particle
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

        self.emitters = []
        img = pyglet.resource.image('confetti.png')
        left_emitter    = particles2D.Emitter(pos=(0,0), 
                                              max_num = 50)
        left_emitter.add_factory(particles2D.confetti_machine(60,
                                                              ((1,6),(3,8)),
                                                              img,
                                                              batch=ui_batch,
                                                              group=None),
                                                              pre_fill = 0)
        right_emitter   = particles2D.Emitter(pos=(screen_res[0],0), 
                                              max_num = 50)
        right_emitter.add_factory(particles2D.confetti_machine(60,
                                                              ((-1,-6),(3,8)),
                                                              img,
                                                              batch=ui_batch,
                                                              group=None),
                                                              pre_fill = 0)
        self.emitters.append(left_emitter)
        self.emitters.append(right_emitter)

        self.sprite_scale = .5
        self.sprite_opacity = 0
        self.added_tween = False
    def update(self, player_pos, angle):
        if self.particle_emit:
            for e in self.emitters: 
                e.update()
                e.draw()
        #x = 23*cos(angle+math.radians(90)) + player_pos[0]
        #y = 23*sin(angle+math.radians(90)) + player_pos[1]

        #self.weighted_angle = ((self.weighted_angle*(5-1))+angle) / 5
        
        #self.sprite.rotation = math.degrees(-self.weighted_angle)

        #self.emitter_L.update()
        #self.emitter_R.update()

        if not self.bb.contains_vect(player_pos):
            self.bb_outline.colors = (self.color*4)

        self.tweener.update()

        if self.bb.contains_vect(player_pos):
            self.particle_emit = True
            #self.fangle = 0
            self.bb_outline.colors = (self.color2*4)
            #self.sprite.rotation = math.degrees(0)
            if not self.added_tween:
                self.added_tweens = True
                self.tweener.add_tween(self,
                                       sprite_scale          = 1,
                                       sprite_opacity        = 255,
                                       tween_time            = 1,
                                       tween_type            = self.tweener.OUT_CUBIC,
                                       #on_update_function   =
                                       #on_complete_function =
                                       )

        self.sprite.scale = self.sprite_scale
        self.sprite.opacity = self.sprite_opacity

        

            #print(self.sprite.scale)


#level_res = ['levels/'+l for l in os.listdir('levels/') if l.endswith('.zip')]