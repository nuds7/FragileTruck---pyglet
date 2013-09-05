import pyglet
from pyglet.gl import *
import pymunk
from pymunk import Vec2d
import configparser
import zipfile
import loaders
import PiTweener
from menu import State_Button

class GroupWithMask(pyglet.graphics.Group):
	def __init__(self, x, y, width, height, parent=None):
		super(GroupWithMask, self).__init__(parent)
		self.x = x
		self.y = y
		self.width = width
		self.height = height

	def set_state(self):
		pyglet.gl.glScissor(self.x, self.y, self.width, self.height)
		pyglet.gl.glEnable(pyglet.gl.GL_SCISSOR_TEST)

	def unset_state(self):
		pyglet.gl.glDisable(pyglet.gl.GL_SCISSOR_TEST)

class ListFadeIn(object):
	def __init__(self, list_with_sprites, tween_time, bg_sprite = None):
		self.list_with_sprites = list_with_sprites
		self.tweener = PiTweener.Tweener()
		self.opacity = 0
		self.tweener.add_tween(self,
							   opacity  	= 255,
						  	   tween_time 	= tween_time,
						  	   tween_type 	= self.tweener.OUT_CUBIC,)
		self.bg_sprite = bg_sprite

	def update(self):
		self.tweener.update()
		for li in self.list_with_sprites:
			li.sprite.opacity = self.opacity
		if self.bg_sprite != None:
			self.bg_sprite.opacity = self.opacity

class ScrollMenu(object):
	def __init__(self, x, y, width, height, item_list, parent_group):
		self.pos = x,y
		#parent_group 	= pyglet.graphics.OrderedGroup(1)
		self.group_1 	= pyglet.graphics.OrderedGroup(20, 		parent = parent_group)
		self.group_2 	= pyglet.graphics.OrderedGroup(21, 		parent = parent_group)
		self.mask 		= GroupWithMask(x-width//2, y-height//2, 
										width, height, 			parent = self.group_2)
		self.group_3 	= pyglet.graphics.OrderedGroup(22, 		parent = parent_group)
		self.group_4 	= pyglet.graphics.OrderedGroup(23, 		parent = parent_group)

		self.buttons = []
		self.y_offset = 0
		for item in item_list:
			button = State_Button([x, y+self.y_offset+(height//2)-30], 
								  'menu/images/level_long.png',
								  padding=(0,-4,0,-2))
			# keep a note of the space between
			# the first button and the next
			button.y_offset = self.y_offset 
			self.y_offset -= button.sprite.image.height
			self.buttons.append(button)

		# check if the list is even worthy of 
		# being scrollable
		if abs(self.y_offset) > height:
			self.scrollable = True
		else:
			self.scrollable = False
		
		self.bb = pymunk.BB(x - width//2,
							y - height//2, 
							x + width//2,
							y + height//2) 

		self.top_left 		= x - width//2, y + height//2
		self.bottom_left 	= x - width//2, y - height//2
		self.top_right 		= x + width//2, y + height//2
		self.bottom_right 	= x + width//2, y - height//2

		self.red = (255,0,0,255)
		self.green = (0,255,0,255)

		self.weighted = 0
		self.scroll_y = 0
		self.contains_mouse = False

		self.top_limit 		= y + height//2 - \
							  self.buttons[0].sprite.image.height//2 - 3
		self.bottom_stopper = y - height//2 + abs(self.y_offset) - \
							  self.buttons[0].sprite.image.height//2 + 2

		self.scroll_amount = 0
		self.rate = 10

		self.close_button = State_Button([x+120, y+194], 
								  		 'menu/images/x.png',
								  		 padding=(-1,-1,-1,-1))

	def setup_batch(self, debug_batch, surface_batch):
		for button in self.buttons:
			button.setup_pyglet_batch(debug_batch, surface_batch, self.mask, None, self.group_4)
		self.bb_outline = debug_batch.add_indexed(4, pyglet.gl.GL_LINES, self.group_4, [0,1,1,2,2,3,3,0], 
											('v2f', (self.top_left[0],		self.top_left[1],
													 self.bottom_left[0],	self.bottom_left[1],
													 self.bottom_right[0],	self.bottom_right[1],
													 self.top_right[0],		self.top_right[1])),
											('c4B', (255,0,0,255)*4))

		img_pos = self.pos[0],self.pos[1]+9

		self.bg = loaders.spriteloader('menu/images/level_select_menu.png',
								  placeholder 			= 'placeholder.png',
								  pos 					= img_pos,
								  anchor 				= ('center','center'),
								  linear_interpolation 	= True)
		self.bg.batch = surface_batch
		self.bg.group = self.group_1

		self.fade_in = ListFadeIn(self.buttons, 1, bg_sprite = self.bg)

		self.close_button.setup_pyglet_batch(debug_batch, surface_batch, self.group_2, None, self.group_4)

	def button_press(self, mouse_pos, button_pressed):
		if self.contains_mouse:
			for button in self.buttons:
				button.press(mouse_pos, button_pressed)
		self.close_button.press(mouse_pos, button_pressed)
	def button_release(self, mouse_pos, button_pressed):
		if self.contains_mouse:
			for button in self.buttons:
				button.release(mouse_pos, button_pressed, (0,0))
		self.close_button.release(mouse_pos, button_pressed, (0,0))
	def button_hover(self, mouse_pos):
		for button in self.buttons:
			button.hover(mouse_pos)

		if self.bb.contains_vect(mouse_pos):
			self.contains_mouse = True
			self.bb_outline.colors = self.green*4
		else:
			self.contains_mouse = False
			self.bb_outline.colors = self.red*4
		self.close_button.hover(mouse_pos)

	def scroll(self, y):
		if self.contains_mouse:
			self.scroll_y = y

	def update(self):
		if self.scrollable: # only scroll if it is scrollable
			self.fade_in.update()

			if self.scroll_y < 0: # scrolling down
				if self.buttons[0].sprite.y > self.top_limit:
					self.scroll_y = self.scroll_y*30
					self.rate = 10
				if self.buttons[0].sprite.y < self.top_limit:
					# fake force scroll
					self.scroll_y = -100
					self.rate = 20
			elif self.scroll_y > 0: # scrolling up
				if self.buttons[0].sprite.y < self.bottom_stopper:
					self.scroll_y = self.scroll_y*30
					self.rate = 10
				if self.buttons[0].sprite.y > self.bottom_stopper:
					# fake force scroll
					self.scroll_y = 100
					self.rate = 20
	
			if self.buttons[0].sprite.y 		< self.top_limit:
				self.buttons[0].sprite.y 		= self.top_limit
				self.buttons[0].hover_sprite.y 	= self.top_limit
				self.buttons[0].press_sprite.y 	= self.top_limit
			elif self.buttons[0].sprite.y 		> self.bottom_stopper:
				self.buttons[0].sprite.y 		= self.bottom_stopper
				self.buttons[0].hover_sprite.y 	= self.bottom_stopper
				self.buttons[0].press_sprite.y 	= self.bottom_stopper
	
			self.weighted = ((self.weighted*(self.rate-1))+(self.scroll_y)) / self.rate
			self.buttons[0].scroll(self.weighted)
			self.buttons[0].update_bb()
	
			for button in self.buttons[1:]:
				# make all buttons reference the first
				button.sprite.y 		= self.buttons[0].sprite.y+button.y_offset
				button.hover_sprite.y 	= self.buttons[0].sprite.y+button.y_offset
				button.press_sprite.y 	= self.buttons[0].sprite.y+button.y_offset
				button.update_bb()
	
			self.scroll_y = 0