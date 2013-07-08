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
import levelbuilder
import box
import bridge
import particle
import box
import mobi
import collectable
import menu
import configparser
import zipfile
import loaders
import trigger
import math
from menu import Button
from box import Boxes
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

def clear_space(space):
	for c in space.constraints:
		space.remove(c)
	for s in space.shapes:
		space.remove(s)
	for b in space.bodies:
		space.remove(b)

class Scene(object):
	def __init__(self, 
				 map_zip, 
				 screen_res,):
		pass
	#def render(self, screen):
	#    raise NotImplementedError
	def update(self):
		raise NotImplementedError
	def world_pos(self, x, y):
		raise NotImplementedError
	def camera_scroll_zoom(self, scroll_y):
		raise NotImplementedError
	def on_mouse_press(self, button, world_mouse):
		raise NotImplementedError
	def on_mouse_drag(self, buttons, world_mouse):
		raise NotImplementedError
	def on_mouse_release(self, button):
		raise NotImplementedError
	#def handle_events(self, events):
	#    raise NotImplementedError

class Editor_Scene(Scene):
	def __init__(self, 
				map_zip, 
				screen_res,):
		super(Editor_Scene, self).__init__(map_zip, 
										screen_res)
		self.debug_batch 		= pyglet.graphics.Batch()
		self.background_batch 	= pyglet.graphics.Batch()
		self.level_batch 		= pyglet.graphics.Batch()
		self.ui_batch 			= pyglet.graphics.Batch()
		self.lfg3 				= pyglet.graphics.OrderedGroup(18)
		self.lfg2 				= pyglet.graphics.OrderedGroup(16)
		self.lfg 				= pyglet.graphics.OrderedGroup(14)
		self.lbg 				= pyglet.graphics.OrderedGroup(12)
		self.pbg4				= pyglet.graphics.OrderedGroup(10)
		self.pbg3				= pyglet.graphics.OrderedGroup(8)
		self.pbg2 				= pyglet.graphics.OrderedGroup(6)
		self.pbg 				= pyglet.graphics.OrderedGroup(4)
		self.bg 				= pyglet.graphics.OrderedGroup(2)

		self.space 							= pymunk.Space()
		self.space.enablne_contact_graph 	= True
		self.space.gravity 					= (0,-800)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_LINE_SMOOTH)
		glPointSize(4)
		glLineWidth(2)
		self.screen_res = screen_res
		self.aspect = screen_res[0]/screen_res[1]

		self.level = levelassembler.Level(map_zip,
										  self.space,
										  self.screen_res,
										  self.debug_batch,
										  self.background_batch,
										  self.level_batch,
										  self.ui_batch,
										  self.lfg3,
										  self.lfg2,
										  self.lfg,
										  self.lbg,
										  self.pbg4,
										  self.pbg3,
										  self.pbg2,
										  self.pbg,
										  self.bg,
										  editor_mode = True
										  )

		self.cameraPosX = self.level.mapWidth//2
		self.cameraPosY = self.level.mapHeight//2
		self.camera = camera.Camera(screen_res, (self.level.mapWidth,self.level.mapHeight), (0,0))

		self.builder = levelbuilder.LevelBuilder(self.debug_batch, self.lfg3, self.lfg2, self.lfg)
		self.mode = 'None'
		self.mode_label = pyglet.text.Label(text = self.mode,
											font_name = 'Calibri', font_size = 8, bold = True,
											x = 1, y = 0, 
											anchor_x = 'left', anchor_y = 'bottom',
											color = (0,0,0,255),
											batch = self.ui_batch)
		self.mode_label.set_style('background_color', (255,255,255,80))
		self.info_label 		= pyglet.text.Label(text = 'Current position: (0, 0)',
													font_name = 'Calibri', font_size = 8, bold = True,
													x = self.screen_res[0], y = 0, 
													anchor_x = 'right', anchor_y = 'bottom',
													color = (0,0,0,255),
													batch = self.ui_batch)
		self.info_label.set_style('background_color', (255,255,255,80))

		self.drag_info = [0,0]

		self.camera_zoom = self.screen_res[1]/4
		self.debug = False
	def update(self, keys_held):
		self.space.step(0.015)
		self.level.update(keys_held, 
						  (self.camera.newPositionX,self.camera.newPositionY), 
						  (self.camera.newPositionX,self.camera.newPositionY),
						  0)

		self.camera.update((self.cameraPosX,self.cameraPosY), 
						   self.camera_zoom, 
						   0, [5,5],10)

		glClearColor(.2,.2,.2,1)
		self.level_batch.draw()
		self.debug_batch.draw()
		self.camera.hud_mode()
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

	def world_pos(self, x, y):
		wX = (self.camera.newPositionX - (self.camera.newWeightedScale*self.aspect)) \
							+ x*((self.camera.newWeightedScale*self.aspect)/self.screen_res[0])*2 
		wY = (self.camera.newPositionY - (self.camera.newWeightedScale)) \
							+ y*((self.camera.newWeightedScale)/self.screen_res[1])*2
		wPos = wX, wY
		return wPos
	def keyboard_input(self, dt):
		pass
	def on_key_press(self, symbol, modifiers):

		self.builder.write_to_file(symbol, modifiers)
		self.builder.undo(symbol, modifiers, self.mode)

		if symbol == pyglet.window.key.ESCAPE:
			self.manager.go_to(Menu_Scene('resources/menu/MAIN_MENU.zip', 
									      self.screen_res,))
		if symbol == pyglet.window.key.D:
			if self.debug == False: 
				self.debug = True
			else: self.debug = False

		if symbol == pyglet.window.key.R:
			self.camera_zoom = self.screen_res[1]/4
		if symbol == pyglet.window.key.T:
			self.camera_zoom = self.screen_res[1]/2

		if symbol == pyglet.window.key._1:
			self.mode = 'Segment'
		if symbol == pyglet.window.key._2:
			self.mode = 'Collectable'
		if symbol == pyglet.window.key._0:
			self.mode = 'None'
		self.builder.write_to_file(symbol, modifiers)
		self.builder.undo(symbol, modifiers, self.mode)
	def on_key_release(self, symbol, modifiers):
		pass
	def on_mouse_press(self, x, y, button, modifiers, world_mouse):
		if self.mode == 'Segment':
			self.builder.add_segment(button, world_mouse)
		if self.mode == 'Collectable':
			self.builder.add_collectable(button, world_mouse)
		if button == 1:
			self.builder.clicked_pos = world_mouse
			print(self.builder.clicked_pos)
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers, world_mouse):
		# Free Camera
		self.cameraPos = self.camera.edge_bounce(dx,dy,[self.cameraPosX,self.cameraPosY])
		self.cameraPosX = self.cameraPos[0]
		self.cameraPosY = self.cameraPos[1]
		if buttons == 4 or buttons == 5:
			self.cameraPosX -= dx*((self.camera.newWeightedScale*self.aspect)/(self.screen_res[0]/2))
			self.cameraPosY -= dy*((self.camera.newWeightedScale)/(self.screen_res[1]/2))
		if self.mode == 'Segment':
			if buttons == 1 or buttons == 5:
				self.builder.guide(buttons, world_mouse)
				self.drag_info = (int(world_mouse[0]),int(world_mouse[1]))
	def on_mouse_release(self, x, y, button, modifiers, world_mouse):
		if self.mode == 'Segment':
			self.builder.add_segment(button, world_mouse)
	def on_mouse_motion(self, x, y, dx, dy, world_mouse):
		self.info_label.text = "Current position: ("+"%.3f"%world_mouse[0]+", "+"%.3f"%world_mouse[1]+")"
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		if self.camera.scale < self.screen_res[1]:
			if scroll_y < 0:
				self.camera_zoom += 20*abs(scroll_y)
				#print("Zooming out by:", 20*abs(scroll_y))
		if self.camera.scale > 50:
			if scroll_y > 0:
				self.camera_zoom -= 20*abs(scroll_y)
				#print("Zooming in by:", 20*abs(scroll_y))


class Game_Scene(Scene):
	def __init__(self, 
				map_zip, 
				screen_res,):
		super(Game_Scene, self).__init__(map_zip, 
										screen_res)
		self.debug_batch 		= pyglet.graphics.Batch()
		self.background_batch 	= pyglet.graphics.Batch()
		self.level_batch 		= pyglet.graphics.Batch()
		self.ui_batch 			= pyglet.graphics.Batch()
		self.lfg3 				= pyglet.graphics.OrderedGroup(18)
		self.lfg2 				= pyglet.graphics.OrderedGroup(16)
		self.lfg 				= pyglet.graphics.OrderedGroup(14)
		self.lbg 				= pyglet.graphics.OrderedGroup(12)
		self.pbg4				= pyglet.graphics.OrderedGroup(10)
		self.pbg3				= pyglet.graphics.OrderedGroup(8)
		self.pbg2 				= pyglet.graphics.OrderedGroup(6)
		self.pbg 				= pyglet.graphics.OrderedGroup(4)
		self.bg 				= pyglet.graphics.OrderedGroup(2)

		self.space 							= pymunk.Space()
		self.space.enablne_contact_graph 	= True
		self.space.gravity 					= (0,-800)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_LINE_SMOOTH)
		glPointSize(4)
		glLineWidth(2)
		self.screen_res = screen_res
		self.aspect = screen_res[0]/screen_res[1]

		self.level = levelassembler.Level(map_zip,
										  self.space,
										  self.screen_res,
										  self.debug_batch,
										  self.background_batch,
										  self.level_batch,
										  self.ui_batch,
										  self.lfg3,
										  self.lfg2,
										  self.lfg,
										  self.lbg,
										  self.pbg4,
										  self.pbg3,
										  self.pbg2,
										  self.pbg,
										  self.bg,
										  )

		self.cameraPosX = self.level.mapWidth//2
		self.cameraPosY = self.level.mapHeight//2
		self.camera = camera.Camera(screen_res, (self.level.mapWidth,self.level.mapHeight), (0,0))

		self.camera_zoom = self.screen_res[1]/4
		self.debug = False
	def update(self, keys_held):
		self.space.step(0.015)
		self.level.update(keys_held, 
						  self.level.player.car_body.position, 
						  (self.camera.newPositionX,self.camera.newPositionY),
						  self.level.player.car_body.angle)

		self.camera.update(self.level.player.car_body.position, 
							(self.camera_zoom), 
							0, [20,15],20)

		glClearColor(1,1,1,1)
		if not self.debug:
			self.level_batch.draw()
		else:
			self.debug_batch.draw()
		self.camera.hud_mode()
		self.ui_batch.draw()

	def world_pos(self, x, y):
		wX = (self.camera.newPositionX - (self.camera.newWeightedScale*self.aspect)) \
							+ x*((self.camera.newWeightedScale*self.aspect)/self.screen_res[0])*2 
		wY = (self.camera.newPositionY - (self.camera.newWeightedScale)) \
							+ y*((self.camera.newWeightedScale)/self.screen_res[1])*2
		wPos = wX, wY
		return wPos
	def keyboard_input(self, dt):
		pass
	def on_key_press(self, symbol, modifiers):
		if symbol == pyglet.window.key.ESCAPE:
			self.manager.go_to(Menu_Scene('resources/menu/MAIN_MENU.zip', 
										  self.screen_res))
		if symbol == pyglet.window.key.D:
			if self.debug == False: 
				self.debug = True
			else: self.debug = False
		if symbol == pyglet.window.key.R:
			self.camera_zoom = self.screen_res[1]/4
		if symbol == pyglet.window.key.T:
			self.camera_zoom = self.screen_res[1]/2
	def on_key_release(self, symbol, modifiers):
		pass
	def on_mouse_press(self, x, y, button, modifiers, world_mouse):
		if button == 4:
			self.level.player.mouse_grab_press(world_mouse)
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers, world_mouse):
		if buttons == 4:
			self.level.player.mouse_grab_drag(world_mouse)
	def on_mouse_release(self, x, y, button, modifiers, world_mouse):
		if button == 4:
			self.level.player.mouse_grab_release()
	def on_mouse_motion(self, x, y, dx, dy, world_mouse):
		pass
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		if self.camera.scale < self.level.mapHeight//2 and \
					self.camera.scale < (self.level.mapWidth//2) / self.aspect:
			if scroll_y < 0:
				self.camera_zoom += 20*abs(scroll_y)
		if self.camera.scale >= self.screen_res[1]/4:
			if scroll_y > 0:
				self.camera_zoom -= 20*abs(scroll_y)

class Menu_Scene(Scene):
	def __init__(self, 
				map_zip,  
				screen_res,):
		super(Menu_Scene, self).__init__(map_zip, 
										screen_res,)
		self.debug_batch 		= pyglet.graphics.Batch()
		self.background_batch 	= pyglet.graphics.Batch()
		self.level_batch 		= pyglet.graphics.Batch()
		self.ui_batch 			= pyglet.graphics.Batch()
		self.lfg3 				= pyglet.graphics.OrderedGroup(18)
		self.lfg2 				= pyglet.graphics.OrderedGroup(16)
		self.lfg 				= pyglet.graphics.OrderedGroup(14)
		self.lbg 				= pyglet.graphics.OrderedGroup(12)
		self.pbg4				= pyglet.graphics.OrderedGroup(10)
		self.pbg3				= pyglet.graphics.OrderedGroup(8)
		self.pbg2 				= pyglet.graphics.OrderedGroup(6)
		self.pbg 				= pyglet.graphics.OrderedGroup(4)
		self.bg 				= pyglet.graphics.OrderedGroup(2)

		self.space 							= pymunk.Space()
		self.space.enablne_contact_graph 	= True
		self.space.gravity 					= (0,-800)
		self.screen_res = screen_res
		self.aspect = screen_res[0]/screen_res[1]

		self.menu = levelassembler.Menu(map_zip,
										self.space,
										self.screen_res,
										self.debug_batch,
										self.background_batch,
										self.level_batch,
										self.ui_batch,
										self.lfg3,
										self.lfg2,
										self.lfg,
										self.lbg,
										self.pbg4,
										self.pbg3,
										self.pbg2,
										self.pbg,
										self.bg)

		self.editor_label = pyglet.text.Label(text = 'Editor',
												font_name = 'Calibri', font_size = 8, bold = True,
												x = self.screen_res[0]-1, y = 0, 
												anchor_x = 'right', anchor_y = 'bottom',
												color = (255,25,25,0),
												batch = self.ui_batch)
		self.editor_label.set_style('background_color', (0,0,0,0)) 

		self.camera = camera.Camera(screen_res, (self.menu.mapWidth,self.menu.mapHeight), (0,0))
		self.cameraPosX = self.menu.cameraStartX
		self.cameraPosY = self.menu.cameraStartY
		self.camera_zoom = self.screen_res[1]/2
		self.debug = False
		self.level_selected = ''
		self.keys_held = []

	def update(self, keys_held):
		self.keys_held = keys_held
		self.space.step(0.015)
		self.camera.update((self.cameraPosX,self.cameraPosY), 
						   self.camera_zoom, 
						   0, [10,10],20)
		self.menu.update()

		if pyglet.window.key.E in self.keys_held:
			self.editor_label.set_style('background_color', (0,0,0,80))
			self.editor_label.color = (255,25,25,150)
		else:
			self.editor_label.set_style('background_color', (0,0,0,0))
			self.editor_label.color = (255,25,25,0)

		glClearColor(.1,.1,.1,.5)
		if not self.debug: 
			self.level_batch.draw()
		if self.debug:
			self.debug_batch.draw()
		self.camera.hud_mode()
		self.ui_batch.draw()

	def world_pos(self, x, y):
		wX = (self.camera.newPositionX - (self.camera.newWeightedScale*self.aspect)) \
							+ x*((self.camera.newWeightedScale*self.aspect)/self.screen_res[0])*2 
		wY = (self.camera.newPositionY - (self.camera.newWeightedScale)) \
							+ y*((self.camera.newWeightedScale)/self.screen_res[1])*2
		wPos = wX, wY
		return wPos

	def on_key_press(self, symbol, modifiers):
		if symbol == pyglet.window.key.ESCAPE:
			self.manager.go_to(Menu_Scene('resources/menu/MAIN_MENU.zip', 
										  self.screen_res))
		if symbol == pyglet.window.key.D:
			if self.debug == False: self.debug = True
			else: self.debug = False
		if symbol == pyglet.window.key.R:
			self.camera_zoom = self.screen_res[1]/4
		if symbol == pyglet.window.key.T:
			self.camera_zoom = self.screen_res[1]/2
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		if self.camera.scale < self.menu.mapHeight//2 and \
					self.camera.scale < (self.menu.mapWidth//2) / self.aspect:
			if scroll_y < 0:
				self.camera_zoom += 30*abs(scroll_y)
		if self.camera.scale > 100:
			if scroll_y > 0:
				self.camera_zoom -= 30*abs(scroll_y)
	def on_mouse_press(self, x, y, button, modifiers, world_mouse):
		for b in self.menu.buttons:
			b.click(world_mouse, button, (self.camera.newPositionX,self.camera.newPositionY))
			if b.camera_move == True:
				self.cameraPosX = b.camera_target_x
				self.cameraPosY = b.camera_target_y
		for box in self.menu.level_boxes:
			box.mouse_buttons = button
			if button == 2 or button == 3:
				box.mouse_grab_press(world_mouse)
			if box.clicked:
				if pyglet.window.key.E in self.keys_held:
					self.manager.go_to(Editor_Scene(
										'levels/'+box.name, 
										self.screen_res))
				else:
					self.manager.go_to(Game_Scene(
										'levels/'+box.name, 
										self.screen_res))
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers, world_mouse):
		if buttons == 4:
			self.cameraPos = self.camera.edge_bounce(dx,dy,[self.cameraPosX,self.cameraPosY])
			self.cameraPosX,self.cameraPosY = self.cameraPos[0],self.cameraPos[1]
			#self.cameraPosY = self.cameraPos[1]
			self.cameraPosX -= dx*((self.camera.newWeightedScale*self.aspect)/(self.screen_res[0]/2))
			self.cameraPosY -= dy*((self.camera.newWeightedScale)/(self.screen_res[1]/2))
		if buttons == 2:
			for box in self.menu.level_boxes:
				box.mouse_grab_drag(world_mouse)
	def on_mouse_release(self, x, y, button, modifiers, world_mouse):
		if button == 2:
			for box in self.menu.level_boxes:
				box.mouse_grab_release()
	def on_mouse_motion(self, x, y, dx, dy, world_mouse):
		for button in self.menu.buttons:
			button.hover(world_mouse)
		for box in self.menu.level_boxes:
			box.mouse_pos = world_mouse

class SceneManager(object):
	def __init__(self, 
				map_zip, 
				screen_res, ):
		self.go_to(Menu_Scene(
				map_zip, 
				screen_res,))
	def go_to(self, scene):
		self.scene = scene
		self.scene.manager = self