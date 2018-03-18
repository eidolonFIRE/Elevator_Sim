
#==========================================================
#
#    Elevator
#
#----------------------------------------------------------
class Elevator(object):
	"""
	Base elevator
	"""
	def __init__(self, capacity):
		super(Elevator, self).__init__()
		self.curfloor = 0
		self.dir = 0
		self.capacity = capacity

		self.peeps = []
		self.queue = []

		# timers
		self.traversing = 0
		self.openDoors = 0

		# time costs in seconds
		self.cost_traverse = 5
		self.cost_doors = 3
		self.cost_boarding = 1
		self.speed = self.cost_traverse

		# accumulators
		self.time_util = 0

