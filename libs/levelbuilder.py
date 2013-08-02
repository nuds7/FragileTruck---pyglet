import pymunk
import pyglet
from pyglet.gl import *
from datetime import datetime

def pairs(l,n):
	return zip(*[l[i::n] for i in range(n)])

class LevelBuilder:
	def __init__(self, debug_batch, ordered_group, ordered_group2, ordered_group3):
		### Segments
		self.segment_points = []
		self.segments_to_add = []
		self.segments_draw = debug_batch.add(1, pyglet.gl.GL_LINES, ordered_group3,
                            					('v2f'),
                            					('c3B')
												)

		self.points_draw = []
		self.points_draw = debug_batch.add(1, pyglet.gl.GL_POINTS, ordered_group,
                            					('v2f'),
                            					('c3B')
												)

		self.guide_line_draw = []
		self.guide_line_draw = debug_batch.add(2, pyglet.gl.GL_LINES, ordered_group2,
                            					('v2f', [0,0,0,0]),
                            					('c4B', (230,20,85,173)*2)
												)
		self.old_segment_points = []
		self.old_segments_draw = debug_batch.add(2, pyglet.gl.GL_LINES, ordered_group2,
                            					('v2f'),
                            					('c3B')
												)
		self.collectables_to_add = []
		self.collectable_points = []
		self.collectable_draw = debug_batch.add(1, pyglet.gl.GL_POINTS, ordered_group,
                            					('v2f'),
                            					('c3B')
												)
		self.old_collectable_points = []
		self.old_collectable_draw = debug_batch.add(1, pyglet.gl.GL_POINTS, ordered_group,
                            					('v2f'),
                            					('c3B')
												)
		###
		self.clicked_pos = 0,0

		print("Builder started.")

	def write_to_file(self, symbol, modifiers):
		if modifiers & pyglet.window.key.MOD_CTRL and symbol == pyglet.window.key.S:
			map_file = open("leveleditoroutput.txt", "a")
			self.segments_to_add = pairs(self.segments_to_add, 2)
			print("Writing to "+"leveleditoroutput.txt...")
			map_file.write("# "+str(datetime.now())+" #\n")
			
			for v in self.segments_to_add:
				print("Segment between points",str(v[0]),",",str(v[1]))
				map_file.write("pymunk.Segment(static_body, "+str(v[0])+", "+str(v[1])+", 4)\n")

			if len(self.segment_points) == 0:
				print("No segments were written.")

			for v in self.collectables_to_add:
				print("Collectables at points",str(v[0]),",",str(v[1]))
				map_file.write("collectable.Collectable(("+str(v[0])+", "+str(v[1])+"), [127,127,127], 'wrench.png')\n")

			if len(self.collectable_points) == 0:
				print("No collectables were written.")

			print("Done!")

			self.segments_to_add = []
			for p in self.segment_points:
				self.old_segment_points.append(p)
			self.segment_points = []

			self.collectables_to_add = []
			for p in self.collectable_points:
				self.old_collectable_points.append(p)
			self.collectable_points = []

	def undo(self, symbol, modifiers, mode):

		if mode == 'Segment':
			if modifiers & pyglet.window.key.MOD_CTRL and symbol == pyglet.window.key.Z:
				print("Removing segment...")
				if len(self.segments_to_add) > 1:
					print("Removed physical",	 str(self.segments_to_add.pop()),str(self.segments_to_add.pop()))
					print("Removed draw points", str(self.segment_points.pop()),str(self.segment_points.pop()),
						   						 str(self.segment_points.pop()),str(self.segment_points.pop())
						   						 )
					self.guide_line_draw.vertices = [0,0,0,0]

		if mode == 'Collectable':
			if modifiers & pyglet.window.key.MOD_CTRL and symbol == pyglet.window.key.Z:
				print("Removing collectable...")
				if len(self.collectables_to_add) > 0:
					print("Removed collectable at ", str(self.collectables_to_add.pop()))
					print("Removed collectable draw point", str(self.collectable_points.pop()),str(self.collectable_points.pop()))

	def add_segment(self, button, world_mouse_pos):
		if button == 1:
			self.segment_points.append(world_mouse_pos[0])
			self.segment_points.append(world_mouse_pos[1])
			self.segments_to_add.append(world_mouse_pos)

	def add_collectable(self, button, world_mouse_pos):
		if button == 1:
			self.collectable_points.append(world_mouse_pos[0])
			self.collectable_points.append(world_mouse_pos[1])
			self.collectables_to_add.append(world_mouse_pos)

	def update(self):
		self.segments_draw.resize(len(self.segment_points)//2)
		self.segments_draw.vertices = self.segment_points
		if len(self.segment_points) % 4 == 0:
			self.segments_draw.colors = (55,190,110,5,158,200)*(len(self.segment_points)//4)

		self.points_draw.resize(len(self.segment_points)//2)
		self.points_draw.vertices = self.segment_points
		self.points_draw.colors = (205,18,90)*(len(self.segment_points)//2)

		self.collectable_draw.resize(len(self.collectable_points)//2)
		self.collectable_draw.vertices = self.collectable_points
		self.collectable_draw.colors = (180,75,10)*(len(self.collectable_points)//2)

		self.old_segments_draw.resize(len(self.old_segment_points)//2)
		self.old_segments_draw.vertices = self.old_segment_points
		self.old_segments_draw.colors = (5,20,5)*(len(self.old_segment_points)//2)

		self.old_collectable_draw.resize(len(self.old_collectable_points)//2)
		self.old_collectable_draw.vertices = self.old_collectable_points
		self.old_collectable_draw.colors = (0,0,20)*(len(self.old_collectable_points)//2)


	def guide(self, buttons, world_mouse_pos):
		self.guide_line_draw.vertices = [self.clicked_pos[0],self.clicked_pos[1],world_mouse_pos[0],world_mouse_pos[1]]

class CreateBridge:
	def __init__(self, debug_batch, ordered_group, ordered_group2, ordered_group3):
		pass