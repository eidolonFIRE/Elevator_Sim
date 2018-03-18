from building import Building_traditional, Building_destination
import peep

import sys


speed = 0.1
verbose = False
reps = 1
elevators = 1
floors = 2
peeps = 10
elevCapacity = 8
gif = False
build = "traditional"

for idx, txt in enumerate(sys.argv):
	if "-s" in txt:
		if idx == len(sys.argv)-1 or "step" in sys.argv[idx+1] or "-" in sys.argv[idx+1]:
			speed = -1
		else:
			speed = 1.0 / float(sys.argv[idx+1])**2

	elif "-v" in txt:
		verbose = True
		print(chr(27) + "[2J")

	elif "-r" in txt:
		reps = int(sys.argv[idx+1])

	elif "-e" in txt:
		elevators = int(sys.argv[idx+1])
	elif "-c" in txt:
		elevCapacity = int(sys.argv[idx+1])

	elif "-f" in txt:
		floors = int(sys.argv[idx+1])

	elif "-p" in txt:
		peeps = int(sys.argv[idx+1])

	elif "-gif" in txt:
		gif = True

	elif "-dest" in txt:
		build = "dest"

	elif "-h" in txt:
		print("\
	v: verbose (render visuals)\n\
	s: frame delay when verbose (seconds)\n\
	gif: save each frame using shutter\n\
\n\
	r: runs to average\n\
\n\
	e: elevators\n\
	c: capacity of elevators\n\
	f: floors\n\
	p: peeps\n\
\n\
	h: print help\n")




tot_lobby = 0
tot_avg = 0
tot_elevUtil = 0
tot_runtime = 0

ppsAdj = peeps * floors
peepQ = peep.buildQueue({"A": ppsAdj//2, "B": ppsAdj-(ppsAdj//2)}, floors)

for x in range(reps):
	if "trad" in build:
		myTestBuilding = Building_traditional(floors=floors, elevators=elevators, people=peepQ, elevCapacity=elevCapacity)
	elif "dest" in build:
		myTestBuilding = Building_destination(floors=floors, elevators=elevators, people=peepQ, elevCapacity=elevCapacity)
	myTestBuilding.run(verbose=verbose, speed=speed, gif = gif)
	
	tot_avg += myTestBuilding.calcAvg()
	tot_lobby += myTestBuilding.calcLobbyShare()
	tot_elevUtil += myTestBuilding.calcAvgElevUtil()
	tot_runtime += myTestBuilding.calcAvgRuntime()
	sys.stdout.write("%d/%d  \r"%(x, reps))


print("Average waiting time: %2.1f%% lobby, %d avg/trip"%(tot_lobby / reps, tot_avg / reps))
print("Elevator Utilization: %2.1f%%"%(tot_elevUtil/reps))
print("Alg Avg Runtime: %f"%(tot_runtime/reps))
