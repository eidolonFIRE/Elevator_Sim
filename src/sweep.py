import sys
from time import time
import copy
from multiprocessing import Pool

from building import Building_traditional, Building_destination
import peep


reps = 1
elevators = 1
floors = 2
peeps = 10
elevCapacity = 8
build = "traditional"


for idx, txt in enumerate(sys.argv):

	if "-r" in txt:
		reps = int(sys.argv[idx+1])

	elif "-e" in txt:
		elevators = int(sys.argv[idx+1])
	elif "-c" in txt:
		elevCapacity = int(sys.argv[idx+1])

	elif "-f" in txt:
		floors = int(sys.argv[idx+1])

	elif "-p" in txt:
		peeps = int(sys.argv[idx+1])

	elif "-dest" in txt:
		build = "dest"

	elif "-h" in txt:
		print("\
	r: runs to average\n\
\n\
	e: elevators\n\
	c: capacity of elevators\n\
	f: floors\n\
	p: peeps\n\
\n\
	h: print help\n")





def worker(floors):
	global elevators
	global peeps 
	global elevCapacity
	global reps
	global build


	flrData_avg      = [0] * elevators
	flrData_lobby    = [0] * elevators
	flrData_elevUtil = [0] * elevators

	ppsAdj = peeps * floors
	for r in range(reps):
		peepsQ = peep.buildQueue({"A": ppsAdj//2, "B": ppsAdj-(ppsAdj//2)}, floors)
		for elevs in range(1,elevators+1):
			if "trad" in build:
				myTestBuilding = Building_traditional(floors=floors, elevators=elevs, people=copy.deepcopy(peepsQ), elevCapacity=elevCapacity)
			elif "dest" in build:
				myTestBuilding = Building_destination(floors=floors, elevators=elevs, people=copy.deepcopy(peepsQ), elevCapacity=elevCapacity)
			myTestBuilding.run(verbose = False)
			flrData_avg[elevs-1]      += myTestBuilding.calcAvg() / reps
			flrData_lobby[elevs-1]    += myTestBuilding.calcLobbyShare() / reps
			flrData_elevUtil[elevs-1] += myTestBuilding.calcAvgElevUtil() / reps

	return (flrData_avg, flrData_lobby, flrData_elevUtil) 
	
	 


# run all the workers


start = time()
p = Pool()
data = p.map(worker, range(2, floors+1))
end = time()




# print results

print("\n=== Average Trip Time ===")
print "floors, " + ",".join(["%delevs"%x for x in range(1,elevators+1)])
for flr, d in enumerate(data):
	print "%2d, "%(flr+2) + ",".join(["%6.2f"%x for x in d[0]])

print("\n=== Average Lobby Time ===")
print "floors, " + ",".join(["%delevs"%x for x in range(1,elevators+1)])
for flr, d in enumerate(data):
	print "%2d, "%(flr+2) + ",".join(["%6.2f"%x for x in d[1]])

# print("\n=== Average Elevator Utilization ===")
# print "floors, " + ",".join(["%delevs"%x for x in range(1,elevators+1)])
# for flr, d in enumerate(data):
# 	print "%2d, "%(flr+2) + ",".join(["%6.2f"%x for x in d[2]])


print("Elapsed time  %d:%d  "%((end-start)/60,(end-start)%60))