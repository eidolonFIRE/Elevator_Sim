from random import randint




#==========================================================
#
#    People
#
#----------------------------------------------------------
class PeepBase(object):
	"""
	Base Human person
	"""
	def __init__(self, floors):
		super(PeepBase, self).__init__()
		self.floor = 0
		self.floors = floors
		self.busy = 1

		# queue in reverse order...
		# [<floor>, <time spend there>]
		self.queue = [
			[0,-1] # return to lobby and exit
		]
		self.trips = 1

		# cumulative time tickers
		self.time_queue = 0
		self.time_trav = 0

	def AddRandFloor(self, time = [10,20]):
		self.trips += 1
		x = randint(0,self.floors-1)
		while x == self.queue[-1][0]:
			x = randint(0,self.floors-1)
		self.queue.append([x,randint(*time)])
		if x == 0:
			self.AddRandFloor()


class PeepA(PeepBase):
	"""
	Behavior:
		- enter first floor
		- move to random floor for a while
		- move back to first floor (and exit)
	"""
	def __init__(self, floors):
		super(PeepA, self).__init__(floors)
		self.AddRandFloor(time = [700,1000])

class PeepB(PeepBase):
	"""
	Behavior:
		- enter first floor
		- move between a few random floors
		- move back to first floor (and exit)
	"""
	def __init__(self, floors):
		super(PeepB, self).__init__(floors)
		for x in range(randint(4,10)):
			self.AddRandFloor(time = [50,100])
		
				
