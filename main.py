import os, sys
os.putenv('PYGLET_SHADOW_WINDOW', '0')
import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import math
from math import sin,cos,tan,degrees
lib_path = os.path.abspath('libs/')
sys.path.append(lib_path)
import camera
import player
import levelassembler
import box
import bridge
import particle
import box
import mobi
import collectable
import scene
#from scene import Level_Scene, Menu_Scene, Game_Scene
import loaders
from random import randrange,uniform
pyglet.resource.path = ['resources',
						'resources/images', 
						'resources/images/tips', 
						'resources/images/dkcopy',
						'resources/menu/images',
						'levels/previews',
						'resources/temp',
						'resources/temp/images', 
						'resources/temp/images/tips']
pyglet.resource.reindex()

class FirstWindow(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super(FirstWindow, self).__init__(*args, **kwargs)
		self.aspect = (self.width/self.height)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_LINE_SMOOTH)
		#self.set_vsync(True)
		pyglet.clock.set_fps_limit(1/60.0)
		pyglet.clock.schedule_interval(self.keyboard_input, 1/60.0)
		#pyglet.clock.schedule_interval(self.update, 1/120.0)

		self.map_zip = "resources/menu/MAIN_MENU.zip"
		self.manager = scene.SceneManager(self.map_zip, 
										(self.width,self.height))

		self.overlay_batch = pyglet.graphics.Batch()
		self.ver_label = pyglet.text.Label(text = 'FragileTruck v0.0.1',
											font_name = 'Calibri', font_size = 8, bold = True,
											x = self.width, y = self.height, 
											anchor_x = 'right', anchor_y = 'top',
											color = (255,255,255,120),
											batch = self.overlay_batch)
		self.ver_label.set_style('background_color', (0,0,0,80)) 

		self.keys_held = []
		
	def on_draw(self):
		self.clear()
		self.manager.scene.update(self.keys_held)
		self.overlay_batch.draw()

	def update(self, dt):
		pass
	def keyboard_input(self, dt):
		pass
	def on_key_press(self, symbol, modifiers):
		self.keys_held.append(symbol)
		self.manager.scene.on_key_press(symbol, modifiers)
	def on_key_release(self, symbol, modifiers):
		self.keys_held.pop(self.keys_held.index(symbol))
	def on_mouse_press(self, x, y, button, modifiers):
		worldMouse = self.manager.scene.world_pos(x,y)
		self.manager.scene.on_mouse_press(x, y, button, modifiers, worldMouse)
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		worldMouse = self.manager.scene.world_pos(x,y)
		self.manager.scene.on_mouse_drag(x, y, dx, dy, buttons, modifiers, worldMouse)
	def on_mouse_release(self, x, y, button, modifiers):
		worldMouse = self.manager.scene.world_pos(x,y)
		self.manager.scene.on_mouse_release(x, y, button, modifiers, worldMouse)
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		worldMouse = self.manager.scene.world_pos(x,y)
		self.manager.scene.on_mouse_scroll(x, y, scroll_x, scroll_y)
	def on_mouse_motion(self, x, y, dx, dy):
		worldMouse = self.manager.scene.world_pos(x,y)
		self.manager.scene.on_mouse_motion(x, y, dx, dy, worldMouse)
	
if __name__ == '__main__':
	window = FirstWindow(1280, 720, caption = 'FragileTruck', fullscreen= False) # 960, 540
	pyglet.app.run()