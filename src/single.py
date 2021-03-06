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
		speed = 1.0 / float(sys.argv[idx+1])**2
		verbose = True

	elif "step" in txt:
		speed = -1
		verbose = True

	elif "-v" in txt:
		verbose = True

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
		verbose = True

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


if verbose:
	print(chr(27) + "[2J")

tot_lobby = 0
tot_avg = 0
tot_elevUtil = 0
tot_runtime = 0

ppsAdj = peeps * floors

for x in range(reps):
	peepQ = peep.buildQueue({"A": ppsAdj//2, "B": ppsAdj-(ppsAdj//2)}, floors)
	if "trad" in build:
		myTestBuilding = Building_traditional(floors=floors, elevators=elevators, people=peepQ, elevCapacity=elevCapacity)
	elif "dest" in build:
		myTestBuilding = Building_destination(floors=floors, elevators=elevators, people=peepQ, elevCapacity=elevCapacity)
	myTestBuilding.run(verbose=verbose, speed=speed, gif = gif)
	
	tot_avg += myTestBuilding.calcAvg() / reps
	tot_lobby += myTestBuilding.calcLobbyShare() / reps
	tot_elevUtil += myTestBuilding.calcAvgElevUtil() / reps
	tot_runtime += myTestBuilding.calcAvgRuntime() / reps
	# sys.stdout.write("%d/%d  \r"%(x, reps))


print("Average waiting time: %2.1f%% lobby, %5.1f avg/trip"%(tot_lobby, tot_avg))
print("Elevator Utilization: %2.1f%%"%(tot_elevUtil))
print("Alg Avg Runtime: %f"%(tot_runtime))
