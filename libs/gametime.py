import time
class GameTime(object):
	def __init__(self):
		self.mil = 0
		self.sec = 0
		self.min = 0
	def tick(self):
		self.mil += 10/6
		if self.mil >= 99:
			self.mil = 0
			self.sec += 1
		if self.sec > 59:
			self.sec = 0
			self.min += 1
		return str(self.min).zfill(2)+':'+str(self.sec).zfill(2)+':'+str(int(self.mil)).zfill(2)