import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import sys, os
import math
from math import sin,cos,tan
lib_path = os.path.abspath('libs/')
sys.path.append(lib_path)
import camera
import player
import levelassembler
import box
import jelly
import jellypolygon
import bridge

pyglet.resource.path = ['resources','resources/images']
pyglet.resource.reindex()

class FirstWindow(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super(FirstWindow, self).__init__(*args, **kwargs) #set size
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		self.batch = pyglet.graphics.Batch()
		self.fps_display = pyglet.clock.ClockDisplay()
		self.space = pymunk.Space()
		self.space.gravity = (0,-800)
		self.space.sleep_time_threshold = .05
		self.map_zip = "levels/pyglettest2.zip"
		self.level = levelassembler.Game_Level(self.map_zip, self.space)
		self.level.pyglet_draw(self.batch)

		self.label = pyglet.text.Label('FragileTruck - 0.0.1', 
										font_name = 'Calibri', font_size = 8, bold = True,
										x = self.width, y = 6, 
										anchor_x = 'right', anchor_y = 'center')

		self.player = player.Player(self.space, (self.level.start_Position_X,self.level.start_Position_Y), (self.level.mapWidth,self.level.mapHeight))
		self.camera = camera.Camera((self.width,self.height), (self.level.mapWidth,self.level.mapHeight), (0,0))
		#self.box = box.CreatePymunkBox(.1, (50,20), 0.5, (50,300), self.space)
		self.trans_blue = 125,175,250,200
		self.trans_green = 125,250,175,200
		self.trans_red = 255,125,125,200
		self.trans_black = 25,25,25,200
		
		self.jelly = jelly.Jelly(self.space, 30, (1575,350), 2, 3, self.trans_blue, (self.level.mapWidth,self.level.mapHeight))
		self.jelly2 = jelly.Jelly(self.space, 60, (1550,480), 6, 4, self.trans_green, (self.level.mapWidth,self.level.mapHeight))
		self.jelly3 = jelly.Jelly(self.space, 20, (1570,580), 8, 5, self.trans_red, (self.level.mapWidth,self.level.mapHeight))
		self.jelly4 = jelly.JellyTypeTwo(self.space, 4, (120,340), 8, 6, self.trans_blue, (self.level.mapWidth,self.level.mapHeight))
		self.jelly5 = jelly.JellyTypeTwo(self.space, 4, (130,380), 8, 7, self.trans_green, (self.level.mapWidth,self.level.mapHeight))

		self.bridge = bridge.Bridge(self.space, (350, 350), (45,5), 10)

		pyglet.clock.schedule_interval(self.keyboard_input, 1/60.0) #schedule a function to move 60x per second (0.01==60x/s, 0.05==20x/s)
		pyglet.clock.schedule_interval(self.update, 1/120.0) #updates pymunk stuff

		self.checks = pyglet.image.create(64, 64, pyglet.image.CheckerImagePattern())
		self.background = pyglet.image.TileableTexture.create_for_image(self.checks)
		self.scroll_zoom = 0

		self.keys_held = [] # maintain a list of keys held
		self.debug = False

	def on_draw(self):
		self.clear()
		self.background.blit_tiled(0, 0, 0, self.level.mapWidth, self.level.mapHeight)
		self.batch.draw()
		self.jelly.draw()
		self.jelly2.draw()
		self.jelly3.draw()
		self.jelly4.draw()
		self.jelly5.draw()
		
		self.bridge.draw()
		if self.debug == True:
			self.player.debug_draw()
		if not self.debug:
			self.player.draw(self.batch)
		

		self.camera.hud_mode() # draw hud after this
		self.label.draw()
		self.fps_display.draw()

	def update(self, dt):
		self.space.step(0.015)
		self.player_velocity = abs(self.player.car_body.velocity[0]/3.5) + abs(self.player.car_body.velocity[1]/4.5)
		self.camera.update(self.player.car_body.position, (self.player_velocity/2 + 250+self.scroll_zoom), 0, (20,10))
		self.level.update((self.camera.newPositionX,self.camera.newPositionY))

	def on_key_press(self, symbol, modifiers):
		self.keys_held.append(symbol)
		if symbol == pyglet.window.key.D:
			if self.debug == False: 
				self.debug = True
			else: self.debug = False
		
	def on_key_release(self, symbol, modifiers):
		self.keys_held.pop(self.keys_held.index(symbol))
	def keyboard_input(self, dt):
		if pyglet.window.key.ESCAPE in self.keys_held: # exits the game
			pyglet.app.exit()
			sys.exit() # fallback
		# Moves with arrow keys
		if pyglet.window.key.R in self.keys_held:
			self.player.reset()
			self.scroll_zoom = 0
		if pyglet.window.key.UP in self.keys_held:
			self.player.force(self.player.car_body,(0,80))
		# Movement
		if pyglet.window.key.LEFT in self.keys_held:
			if pyglet.window.key.LSHIFT in self.keys_held: # Boost
				self.player.left_wheel_b.angular_velocity += 7
			else: # Regular
				self.player.left_wheel_b.angular_velocity += 3

		if pyglet.window.key.RIGHT in self.keys_held:
			if pyglet.window.key.LSHIFT in self.keys_held: # Boost
				self.player.left_wheel_b.angular_velocity -= 7
			else: # Regular
				self.player.left_wheel_b.angular_velocity -= 3

		if pyglet.window.key.DOWN in self.keys_held:
			self.player.left_wheel_b.angular_velocity 		*= 0.49 # brakes
			self.player.right_wheel_b.angular_velocity 		*= 0.49
			self.player.car_body.angular_velocity 			*= 0.49
		if not pyglet.window.key.LEFT in self.keys_held and not pyglet.window.key.RIGHT in self.keys_held:
			self.player.left_wheel_b.angular_velocity    	*= .95 # fake friction for wheel 
			self.player.right_wheel_b.angular_velocity   	*= .95

	def on_mouse_press(self, x, y, button, modifiers):
		pass
	def on_mouse_release(self, x, y, button, modifiers):
		pass
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		if scroll_y <= -1.0:
			self.scroll_zoom += 30*abs(scroll_y)
			print("Zooming out by:", 30*abs(scroll_y))
		if scroll_y >= 1.0:
			self.scroll_zoom -= 30*abs(scroll_y)
			print("Zooming in by:", 30*abs(scroll_y))
		
if __name__ == '__main__':
	window = FirstWindow(1280,720)
	pyglet.app.run()