from random import randint
from random import choice
from sys import stdout
from time import sleep
from time import time

from elev import *
from peep import *

import subprocess




class Building_base(object):
	"""
	A collection of elevators.
	This entity is acting as the elevator controller as well.
	"""
	def __init__(self, floors = 2, elevators = 1, people = {"A":1}, elevCapacity = 8):
		super(Building_base, self).__init__()
		self.floors = floors
		self.elevators = [Elevator(elevCapacity) for x in range(elevators)]
		self.people = people
		self.remaining = sum(people.values())
		self.starting = self.remaining

		# empty queue for each floor
		self.floorQs = [[] for x in range(floors)]

		# time cumulators
		self.time_queue = 0
		self.time_queue_div = 0
		self.time_trav = 0
		self.time_trav_div = 0
		self.time_tot = 0
		self.avgRuntime = 0.0



	def DrawNextPeep(self, dist):
		x = choice("".join([k*v for k,v in dist.items()]))
		self.people[x] -= 1
		if x == "A":
			return PeepA(self.floors)
		elif x == "B":
			return PeepB(self.floors)
		else:
			assert("Error: unknown peep selected.")
			return None


	def PrintState(self):
		stdout.write("\033[0;0H")

		stdout.write(("Flr.{:^%d}.  .   Lobby   .    Busy\n"%(len(self.elevators)*3)).format("Elevators" if len(self.elevators) > 3 else "Elev") )
		
		for floor in range(self.floors-1, -1, -1):
			stdout.write("%2d |"%floor)

			# elevators
			for elev in self.elevators:
				stdout.write(("[%d]" if elev.openDoors else "]%d[")%len(elev.peeps) if elev.curfloor == floor else (" * " if floor in elev.queue else "   "))

			# call buttons
			stdout.write("|")
			stdout.write(("^" if self.floorCalls[floor][0] else " ") + ("v" if self.floorCalls[floor][1] else " ") + "|")

			# peeps
			stdout.write("{:<10} - {:<10} \n".format(
				"".join([str(x.queue[-1][0]) if x.busy <= 0 else "" for x in self.floorQs[floor]]),
				"".join([str(x.queue[-1][0]) if x.busy > 0 else "" for x in self.floorQs[floor]]),
				))

		stdout.write("    ")
		for elev in self.elevators:
			if elev.dir > 0:
				stdout.write(" ^ ")
			elif elev.dir < 0:
				stdout.write(" v ")
			elif elev.dir == 0:
				stdout.write("   ")
		stdout.write("                            \n")
		
		stdout.write("     People: %3d coming, %3d cur, %3d remain \n"%(sum(self.people.values()), self.remaining - sum(self.people.values()), self.remaining))
		stdout.write("  Elev Util: %5.1f %%     (%5.1f %% idle) \n"%(self.calcElevUtil(), self.calcElevIdle()))
		if self.time_queue_div:
			avg = float(self.time_queue) / self.time_queue_div
		else:
			avg = 0
		stdout.write(" Lobby Wait: %5.1f avg   (%5.1f %% trip) \n"%(avg, self.calcLobbyShare()))

		stdout.write("                \n")

	def calcElevUtil(self):
		return 100.0*sum([float(len(x.peeps))/x.capacity for x in self.elevators])/len(self.elevators)

	def calcElevIdle(self):
		return 100.0*sum([not abs(x.dir) for x in self.elevators])/float(len(self.elevators))

	def calcAvgElevUtil(self):
		return 100.0*sum([float(x.time_util)/x.capacity for x in self.elevators])/len(self.elevators)/self.time_tot

	def calcLobbyShare(self):
		if not self.time_queue_div or not self.time_trav_div:
			return 0
		else:
			return 100.0*(self.time_queue/self.time_queue_div) / (self.time_queue/self.time_queue_div + self.time_trav/self.time_trav_div)

	def calcAvgRuntime(self):
		return self.avgRuntime / self.time_tot * 1000000

	def calcAvg(self):
		return (float(self.time_queue)/self.time_queue_div + float(self.time_trav)/self.time_trav_div)




	def run(self, verbose = True, speed=0.2, gif=False):
		frame = 0
		while self.remaining:
			frameUnique = False
			start = time()
			self.time_tot += 1

			# add a person to first floor queue
			if randint(0, 1000 / self.starting) == 0:
				if sum(self.people.values()):
					self.floorQs[0].append(self.DrawNextPeep(self.people))
					# frameUnique = True
			
			for idx, floor in enumerate(self.floorQs):
				for peep in floor:
					if peep.busy > 0:
						# tick down busy timer
						peep.busy -= 1
						if peep.busy == 0:
							# call elevator
							self.peepEntersFloor(peep, idx)
							frameUnique = True
					else:
						# tick up peep busy cumulators
						peep.time_queue += 1

			# run elevators
			for elev in self.elevators:
				# timers
				for peep in elev.peeps:
					peep.time_trav += 1
				elev.time_util += len(elev.peeps)

				# traversing between floors
				if elev.traversing:
					elev.traversing -= 1

				# doors open
				elif elev.openDoors:
					elev.openDoors -= 1

					# try to unload peeps
					for peep in elev.peeps:
						if peep.queue[-1][0] == elev.curfloor:
							elev.peeps.remove(peep)
							elev.openDoors += elev.cost_boarding
							f, peep.busy = peep.queue.pop()
							if peep.busy >= 0:
								self.floorQs[elev.curfloor].append(peep)
								frameUnique = True
								self.time_trav += peep.time_trav
								self.time_trav_div += 1
							else:
								# check for finished peeps
								self.remaining -= 1

					# try to load peeps
					i_p = 0
					while len(elev.peeps) < elev.capacity and i_p < len(self.floorQs[elev.curfloor]):
						# move peep onto elevator
						if self.floorQs[elev.curfloor][i_p].busy == 0:
							if (self.decideBoardElev(elev, self.floorQs[elev.curfloor][i_p])):
								elev.openDoors += elev.cost_boarding
								elev.peeps.append(self.floorQs[elev.curfloor].pop(i_p))
								self.peepEntersElev(elev.peeps[-1], elev)
								self.time_queue += elev.peeps[-1].time_queue
								self.time_queue_div += 1
								elev.peeps[-1].time_queue = 0
								frameUnique = True
						i_p += 1

					# clear call button and this floor from queue
					# TODO: optimize this
					if elev.openDoors == 0:
						idx = 0 if elev.dir == 1 else 1
						callUp = False
						callDown = False
						for peep in self.floorQs[elev.curfloor]:
							if peep.busy:
								continue
							if peep.queue[-1][0] > elev.curfloor:
								callUp = True
							if peep.queue[-1][0] < elev.curfloor:
								callDown = True
							if callUp and callDown:
								break
						self.floorCalls[elev.curfloor] = [callUp, callDown]

				# deciding next move
				elif elev.dir == 0:
					self.elevIdle(elev)
					
				# move elevator
				else:
					if len(elev.queue) == 0:
						elev.dir = 0
					else:
						frameUnique = True
						elev.curfloor += elev.dir
						if elev.curfloor >= self.floors - 1:
							elev.dir = -1
						elif elev.curfloor == 0:
							elev.dir = 1
						# check if should open
						if elev.curfloor in elev.queue \
							or (self.floorCalls[elev.curfloor][0] and elev.dir == 1) \
							or (self.floorCalls[elev.curfloor][1] and elev.dir == -1):
							elev.openDoors = elev.cost_doors
							if elev.curfloor in elev.queue:
								elev.queue.remove(elev.curfloor)
						else:
							if len(elev.queue):
								elev.traversing = elev.cost_traverse
							else:
								elev.dir = 0

			end = time()
			self.avgRuntime += (end-start)

			if verbose and frameUnique:
				self.PrintState()
				if gif:
					print("frame: %d"%frame)
					sleep(0.2)
					subprocess.Popen(["shutter", "-a", "-e", "-n", "--disable_systray", "--output=renders/render%04d.png"%frame], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					frame += 1
					sleep(1)
				elif speed >= 0:
					sleep(max(speed - (end-start)*2, 0))
				else:
					raw_input()






#==========================================================
#
#    Building
#
#----------------------------------------------------------
class Building_traditional(Building_base):
	"""
	Traditional elevator type
	"""
	def __init__(self, floors, elevators, people, elevCapacity):
		super(Building_traditional, self).__init__(floors, elevators, people, elevCapacity)
		# [up, down] call buttons activated
		self.floorCalls = [[False,False] for x in range(floors)]


	def peepEntersFloor(self, peep, floor):
		# call elevator
		if peep.queue[-1][0] > floor:
			# going up
			self.floorCalls[floor][0] = True
		else:
			# going down
			self.floorCalls[floor][1] = True


	def peepEntersElev(self, peep, elev):
		# push button inside elevator
		floorRequest = peep.queue[-1][0]
		if floorRequest not in elev.queue:
			elev.queue.append(floorRequest)


	def decideBoardElev(self, elev, peep):
		if (peep.queue[-1][0] > elev.curfloor and elev.dir == 1)\
			or (peep.queue[-1][0] < elev.curfloor and elev.dir == -1):
			return True
		else:
			return False


	def elevIdle(self, elev):
		for idx,x in enumerate(self.floorCalls):
			if x[0] or x[1]:
				flagDo = True
				# don't go if another elevator is already scheduled to stop there
				# or if another idle elevator is closer
				for t,others in enumerate(self.elevators):
					if t == idx:
						continue
					if idx in others.queue or ((others.dir is 0 or others.openDoors) and abs(idx - others.curfloor) < abs(idx - elev.curfloor)):
						flagDo = False
						break

				if flagDo:
					if idx > elev.curfloor:
						elev.dir = 1
						elev.traversing = elev.cost_traverse
						elev.queue.append(idx)
					elif idx < elev.curfloor:
						elev.dir = -1
						elev.traversing = elev.cost_traverse
						elev.queue.append(idx)
					else:
						elev.dir = (1 if x[0] else -1)
						elev.openDoors = elev.cost_boarding
					break




