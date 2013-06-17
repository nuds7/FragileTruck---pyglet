import pyglet
from pyglet.gl import *
import PiTweener
class FlyInText(object):
	def __init__(self, screen_size, start_pos, target_pos, ui_batch):
		self.screen_size = screen_size
		self.target_pos = target_pos
		self.text = pyglet.text.Label(text = 'TEST',
											font_name = 'Calibri', font_size = 30, bold = False,
											x = 0, y = 0, 
											anchor_x = 'right', anchor_y = 'bottom',
											color = (0,0,0,200),
											batch = ui_batch)
		self.text_x = 0
		#self.text.x = self.textX

	def update(self):
		self.text.x = self.text_x

	def on_complete(self):
		print("Done tweening.")