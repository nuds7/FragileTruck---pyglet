import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import sys, os
import math
from math import sin,cos,tan,degrees
lib_path = os.path.abspath('libs/')
sys.path.append(lib_path)
levels_path = os.path.abspath('levels/')
sys.path.append(levels_path)
import camera
import player
import levelassembler
import box
import jelly
import jellypolygon
import bridge
import particle
import box
import mobi
import levelbuilder
from datetime import datetime
from random import randrange,uniform
pyglet.resource.path = ['resources','resources/images','resources/temp','resources/temp/images']
pyglet.resource.reindex()

class FirstWindow(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super(FirstWindow, self).__init__(*args, **kwargs) #set size
		self.aspect = (self.width/self.height)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_LINE_SMOOTH)
		#self.set_vsync(False)
		glPointSize(4)
		glLineWidth(2)

		self.debug_batch = pyglet.graphics.Batch()
		self.level_batch = pyglet.graphics.Batch()
		self.ui_batch = pyglet.graphics.Batch()

		self.levelForeground3 	= pyglet.graphics.OrderedGroup(4)
		self.levelForeground2 	= pyglet.graphics.OrderedGroup(3)
		self.levelForeground 	= pyglet.graphics.OrderedGroup(2)
		self.levelBackground 	= pyglet.graphics.OrderedGroup(1)
		self.parallaxBackground = pyglet.graphics.OrderedGroup(0)
		#self.fps_display = pyglet.clock.ClockDisplay()
		self.space = pymunk.Space()
		self.space.enable_contact_graph = True
		self.space.gravity = (0,-800)
		#self.space.sleep_time_threshold = .05

		self.lvllist = [] # list of levels
		for lvl in os.listdir("levels"):
			self.lvllist.append(lvl)
		self.lvl_iter_num = 0
		print('Levels: '+str(self.lvllist))

		selected_map = 'dkcopy'
		self.map_zip = "levels/"+str(selected_map)+".zip"

		self.level = levelassembler.Game_Level(self.map_zip, self.space, self.debug_batch, self.level_batch, self.ui_batch,
											self.parallaxBackground, self.levelBackground, self.levelForeground, self.levelForeground3)

		self.alpha_label = pyglet.text.Label(text = 'FragileTruck v0.0.1',
											font_name = 'Calibri', font_size = 8, bold = True,
											x = self.width, y = 0, 
											anchor_x = 'right', anchor_y = 'bottom',
											color = (0,0,0,120),
											batch = self.ui_batch)
		self.fps_label = pyglet.text.Label(text = '',
											font_name = 'Calibri', font_size = 8, bold = True,
											x = self.width, y = 8, 
											anchor_x = 'right', anchor_y = 'bottom',
											color = (0,0,0,200),
											batch = self.ui_batch)

		self.camera = camera.Camera((self.width,self.height), (self.level.mapWidth,self.level.mapHeight), (0,0))
		
		#self.space.add_collision_handler(1,2,None,self.vehicle_particles.colliding, None, self.vehicle_particles.collided)

		pyglet.clock.schedule_interval(self.keyboard_input, 1/60.0) #schedule a function to move 60x per second (0.01==60x/s, 0.05==20x/s)
		pyglet.clock.schedule_interval(self.update, 1/120.0) #updates pymunk stuff

		self.scroll_zoom = 0
		self.keys_held = [] # maintain a list of keys held
		self.debug = False

		self.cameraPosX = self.level.mapWidth//2
		self.cameraPosY = self.level.mapHeight//2

		self.builder = levelbuilder.LevelBuilder(self.debug_batch, self.levelForeground3, self.levelForeground2, self.levelForeground)
		self.mode = 'None'
		self.count = 0
		self.drag_info = (0,0)

		self.mode_label = pyglet.text.Label(text = self.mode,
											font_name = 'Calibri', font_size = 8, bold = True,
											x = 1, y = 0, 
											anchor_x = 'left', anchor_y = 'bottom',
											color = (0,0,0,255),
											batch = self.ui_batch)
		self.pos_label = pyglet.text.Label(text = '',
											font_name = 'Calibri', font_size = 8, bold = True,
											x = 1, y = self.height-11, 
											anchor_x = 'left', anchor_y = 'bottom',
											color = (0,0,0,200),
											batch = self.ui_batch)

	def on_draw(self):
		self.level.update((self.camera.newPositionX,self.camera.newPositionY), 
						  (self.camera.newPositionX,self.camera.newPositionY),
						  (self.camera.newWeightedScale*self.aspect,self.camera.newWeightedScale), 
						  self.keys_held)
		self.space.step(0.005)

		self.camera.update((self.cameraPosX,self.cameraPosY), 
							(self.scroll_zoom + self.height//4), 
							0, [5,5], 10)
		self.clear()
		glClearColor(20,80,20,0)

		self.level_batch.draw()
		self.debug_batch.draw()
		self.camera.hud_mode() # draw hud after this
		self.fps_label.text = 'FPS: ' + str(int(pyglet.clock.get_fps()))
		self.ui_batch.draw()

		self.builder.update()
		if self.mode == "Segment":
			self.count = len(self.builder.segments_to_add)/2
			self.mode_label.text = "Mode: "+self.mode.upper()+" | Ammount: "+str(self.count)+" | Position: "+str(self.drag_info)
		if self.mode == "Collectable":
			self.count = len(self.builder.collectables_to_add)
			self.mode_label.text = "Mode: "+self.mode.upper()+" | Ammount: "+str(self.count)
		if self.mode == "None":
			self.mode_label.text = 'No editing mode selected. Press 1-2 to select a mode. Ctrl+Z to undo the last action in that mode. Ctrl+S to save.'

	def update(self, dt):
		pass

	def on_key_press(self, symbol, modifiers):
		self.keys_held.append(symbol)
		if symbol == pyglet.window.key.D:
			if self.debug == False: 
				self.debug = True
			else: self.debug = False
		if symbol == pyglet.window.key.R:
			self.scroll_zoom = 0
		if symbol == pyglet.window.key.T:
			self.scroll_zoom = self.height//4


		if symbol == pyglet.window.key._1:
			self.mode = 'Segment'
		if symbol == pyglet.window.key._2:
			self.mode = 'Collectable'
		if symbol == pyglet.window.key._0:
			self.mode = 'None'

		self.builder.write_to_file(symbol, modifiers)
		self.builder.undo(symbol, modifiers, self.mode)
		# Changing maps.
		# Can be adapted for the regular game, I just need to take in account
		# the player and its starting position.
		if symbol == pyglet.window.key.UP: 
			# clean out batches
			self.debug_batch = pyglet.graphics.Batch()
			self.level_batch = pyglet.graphics.Batch()
			self.ui_batch = pyglet.graphics.Batch()
	
			self.levelForeground3 	= pyglet.graphics.OrderedGroup(4)
			self.levelForeground2 	= pyglet.graphics.OrderedGroup(3)
			self.levelForeground 	= pyglet.graphics.OrderedGroup(2)
			self.levelBackground 	= pyglet.graphics.OrderedGroup(1)
			self.parallaxBackground = pyglet.graphics.OrderedGroup(0)
			# remove all bodies, shapes, and constraints
			for c in self.space.constraints:
				self.space.remove(c)
			for s in self.space.shapes:
				self.space.remove(s)
			for b in self.space.bodies:
				self.space.remove(b)

			# set new level
			print(self.lvl_iter_num)
			print(len(self.lvllist))
			if self.lvl_iter_num < len(self.lvllist)+1:
				self.lvl_iter_num += 1
			if self.lvl_iter_num > len(self.lvllist)-1:
				self.lvl_iter_num = 0
			print('Loading level... '+str(self.lvllist[self.lvl_iter_num]))
			self.level = levelassembler.Game_Level('levels/'+self.lvllist[self.lvl_iter_num], self.space, self.debug_batch, self.level_batch, self.ui_batch,
											      self.parallaxBackground, self.levelBackground, self.levelForeground, self.levelForeground3)
			# reset camera
			self.camera = camera.Camera((self.width,self.height), (self.level.mapWidth,self.level.mapHeight), (0,0))
			self.cameraPosX = self.level.mapWidth//2
			self.cameraPosY = self.level.mapHeight//2
			self.scroll_zoom = self.level.mapHeight//2 - self.height//4

	def on_key_release(self, symbol, modifiers):
		self.keys_held.pop(self.keys_held.index(symbol))

	def keyboard_input(self, dt):
		if pyglet.window.key.ESCAPE in self.keys_held: # exits the game
			pyglet.app.exit()
			sys.exit() # fallback

	def on_mouse_press(self, x, y, button, modifiers):
		worldMouse = camera.worldMouse(x, y, self.camera.newPositionX, self.camera.newPositionY, 
										   self.camera.newWeightedScale, (self.width,self.height))

		if self.mode == 'Segment':
			self.builder.add_segment(button, worldMouse)
		if self.mode == 'Collectable':
			self.builder.add_collectable(button, worldMouse)

		if button == 1:
			self.builder.clicked_pos = worldMouse
			print(self.builder.clicked_pos)

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		aspect = (self.width/self.height)
		# Free Camera
		self.cameraPos = self.camera.edge_bounce(dx,dy,[self.cameraPosX,self.cameraPosY])
		self.cameraPosX = self.cameraPos[0]
		self.cameraPosY = self.cameraPos[1]
		if buttons == 4 or buttons == 5:
			self.cameraPosX -= dx*((self.camera.newWeightedScale*aspect)/(self.width/2))
			self.cameraPosY -= dy*((self.camera.newWeightedScale)/(self.height/2))
		#
		worldMouse = camera.worldMouse(x, y, self.camera.newPositionX, self.camera.newPositionY, 
										   self.camera.newWeightedScale, (self.width,self.height))
		if self.mode == 'Segment':
			if buttons == 1 or buttons == 5:
				self.builder.guide(buttons, worldMouse)
				self.drag_info = (int(worldMouse[0]),int(worldMouse[1]))

	def on_mouse_release(self, x, y, button, modifiers):
		worldMouse = camera.worldMouse(x, y, self.camera.newPositionX, self.camera.newPositionY, 
										   self.camera.newWeightedScale, (self.width,self.height))
		if self.mode == 'Segment':
			self.builder.add_segment(button, worldMouse)
	def on_mouse_motion(self, x, y, dx, dy):
		worldMouse = camera.worldMouse(x, y, self.camera.newPositionX, self.camera.newPositionY, 
										   self.camera.newWeightedScale, (self.width,self.height))
		self.pos_label.text = "Current position: ("+"%.3f"%worldMouse[0]+", "+"%.3f"%worldMouse[1]+")"

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		if self.camera.scale < self.level.mapHeight//2 and \
					self.camera.scale < (self.level.mapWidth//2) / self.aspect:
			if scroll_y < 0:
				self.scroll_zoom += 20*abs(scroll_y)
				#print("Zooming out by:", 20*abs(scroll_y))
		if self.camera.scale > 50:
			if scroll_y > 0:
				self.scroll_zoom -= 20*abs(scroll_y)
				#print("Zooming in by:", 20*abs(scroll_y))
		
if __name__ == '__main__':
	#window = FirstWindow(1440,900, fullscreen = True, caption = 'FragileTruck v0.0.1')
	window = FirstWindow(1280, 720, caption = 'FragileTruck v0.0.1')
	pyglet.app.run()