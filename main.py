import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import sys, os
import math
from math import sin,cos,tan,degrees
lib_path = os.path.abspath('libs/')
sys.path.append(lib_path)
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
import collectable
import flyintext
import PiTweener
from random import randrange,uniform
pyglet.resource.path = ['resources','resources/images','resources/temp','resources/temp/images']
pyglet.resource.reindex()

class FirstWindow(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super(FirstWindow, self).__init__(*args, **kwargs)
		self.aspect = (self.width/self.height)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_LINE_SMOOTH)
		#self.set_vsync(False)

		self.debug_batch = pyglet.graphics.Batch()
		self.level_batch = pyglet.graphics.Batch()
		self.ui_batch = pyglet.graphics.Batch()

		self.levelForeground3 	= pyglet.graphics.OrderedGroup(4)
		self.levelForeground2 	= pyglet.graphics.OrderedGroup(3)
		self.levelForeground 	= pyglet.graphics.OrderedGroup(2)
		self.levelBackground 	= pyglet.graphics.OrderedGroup(1)
		self.parallaxBackground = pyglet.graphics.OrderedGroup(0)
		#self.fps_display 		= pyglet.clock.ClockDisplay()

		self.space = pymunk.Space()
		self.space.enablne_contact_graph = True
		self.space.gravity = (0,-800)
		#self.space.sleep_time_threshold = .05

		self.map_zip = "levels/dkcopy.zip"
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
		self.player = player.Player(self.space, (self.level.start_Position_X,self.level.start_Position_Y), 
									self.level_batch, self.levelForeground, self.levelForeground2, self.levelForeground3)
		self.camera = camera.Camera((self.width,self.height), (self.level.mapWidth,self.level.mapHeight), (0,0))
		
		# Vehicle Particles
		self.vehicle_particles = particle.Particle(self.space, (0,0,0), self.level_batch, self.levelForeground)
		self.space.add_collision_handler(1,2,None,self.vehicle_particles.colliding, None, self.vehicle_particles.collided)

		pyglet.clock.schedule_interval(self.keyboard_input, 1/60.0) #schedule a function to move 60x per second (0.01==60x/s, 0.05==20x/s)
		pyglet.clock.schedule_interval(self.update, 1/120.0) #updates pymunk stuff

		self.scroll_zoom = 0
		self.keys_held = [] # maintain a list of keys held
		self.debug = False

	def on_draw(self):
		self.space.step(0.015)
		self.level.update(self.player.car_body.position, 
						  (self.camera.newPositionX,self.camera.newPositionY),
						  (self.camera.newWeightedScale*self.aspect,self.camera.newWeightedScale),
						  self.keys_held)
		self.player_velocity = abs(self.player.car_body.velocity[0]/3.5) + abs(self.player.car_body.velocity[1]/4.5)
		self.camera.update(self.player.car_body.position, 
							(self.player_velocity/2 + self.scroll_zoom + self.height//4), 
							sin(self.player.car_body.angle)*4, 
							[20,15],20)
		
		self.clear()
		glClearColor(20,50,20,0)
		self.player.draw()
		self.level_batch.draw()
		self.debug_batch.draw()
		#self.player.debug_draw() # LAGGY
		self.vehicle_particles.draw()

		worldPos = camera.worldMouse(self.player.car_body.position[0], self.player.car_body.position[1], 
									self.camera.newPositionX, self.camera.newPositionY, 
									self.camera.newWeightedScale, (self.width,self.height))

		self.camera.hud_mode() # draw hud after this
		self.fps_label.text = 'FPS: ' + str(int(pyglet.clock.get_fps()))
		self.ui_batch.draw()

	def update(self, dt):
		if self.vehicle_particles.collidingBool and \
				abs(self.player.left_wheel_b.angular_velocity) > 10 and abs(self.player.left_wheel_b.angular_velocity) < 60:
			self.vehicle_particles.add((self.player.left_wheel_b.angular_velocity*2,uniform(20,abs(self.player.left_wheel_b.angular_velocity)*4)), 1)
		self.vehicle_particles.cleanup(55)

	def on_key_press(self, symbol, modifiers):
		self.keys_held.append(symbol)
		if symbol == pyglet.window.key.D:
			if self.debug == False: 
				self.debug = True
			else: self.debug = False
	
		if symbol == pyglet.window.key.R:
			self.player.reset()
			self.scroll_zoom = 0
		if symbol == pyglet.window.key.T:
			self.scroll_zoom = self.height//4
		if symbol == pyglet.window.key.C:
			self.level.remove()
		
		
	def on_key_release(self, symbol, modifiers):
		self.keys_held.pop(self.keys_held.index(symbol))

	def keyboard_input(self, dt):
		self.player.controls(self.keys_held)
		if pyglet.window.key.ESCAPE in self.keys_held: # exits the game
			pyglet.app.exit()
			sys.exit() # fallback

	def on_mouse_press(self, x, y, button, modifiers):
		worldMouse = camera.worldMouse(x, y, self.camera.newPositionX, self.camera.newPositionY, 
									   self.camera.newWeightedScale, (self.width,self.height))
		if button == 4:
			self.player.mouse_grab_press(worldMouse)
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		aspect = (self.width/self.height)
		worldMouse = camera.worldMouse(x, y, self.camera.newPositionX, self.camera.newPositionY, 
									   self.camera.newWeightedScale, (self.width,self.height))
		if buttons == 4:
			self.player.mouse_grab_drag(worldMouse)
	def on_mouse_release(self, x, y, button, modifiers):
		if button == 4:
			self.player.mouse_grab_release()
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		if self.camera.scale < self.level.mapHeight//2 and \
					self.camera.scale < (self.level.mapWidth//2) / self.aspect:
			if scroll_y <= -1.0:
				self.scroll_zoom += 30*abs(scroll_y)
				#print("Zooming out by:", 30*abs(scroll_y))
		if self.camera.scale > 100:
			if scroll_y >= 1.0:
				self.scroll_zoom -= 30*abs(scroll_y)
				#print("Zooming in by:", 30*abs(scroll_y))
		
if __name__ == '__main__':
	window = FirstWindow(1280, 720, caption = 'FragileTruck v0.0.1', fullscreen=False)
	pyglet.app.run()