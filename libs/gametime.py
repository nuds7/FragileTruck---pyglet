import time
import PiTweener
class GameTime(object):
	def __init__(self):
		self.mil = 0
		self.sec = 0
		self.min = 0
		self.time_tween = PiTweener.Tweener()
		self.time_tween.add_tween(self,
								  mil 					= 99,
								  tween_time 			= 1,
								  tween_type 			= self.time_tween.LINEAR,
								  on_complete_function 	= self.tween_complete)
	def tick(self):
		self.time_tween.update()
		if self.sec > 59:
			self.sec = 0
			self.min += 1
		return str(self.min).zfill(2)+':'+str(self.sec).zfill(2)+':'+str(int(self.mil)).zfill(2)
	def tween_complete(self):
		self.mil = 0
		self.sec += 1
		self.time_tween.add_tween(self,
								  mil 					= 99,
								  tween_time 			= 1,
								  tween_type 			= self.time_tween.LINEAR,
								  on_complete_function 	= self.tween_complete)
