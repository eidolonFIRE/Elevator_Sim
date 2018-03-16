from building import Building_traditional
import sys
from time import time



reps = 1
elevators = 1
floors = 2
peeps = 10
elevCapacity = 8


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




data = []

def Single(reps, floors, elevators, peeps, elevCapacity):
	for x in range(reps):
		myTestBuilding = Building_traditional(floors=floors, elevators=elevators, people={"A":peeps//2, "B":peeps-(peeps//2)}, elevCapacity=elevCapacity)
		myTestBuilding.run(verbose = False)
	return myTestBuilding.calcAvg() / reps


start = time()

print "floors, " + ",".join(["%delevs"%x for x in range(1,elevators+1)])
for flr in range(2, floors+1):
	data = []
	for elevs in range(1,elevators+1):
		# sys.stdout.write("%d/%d  \r"%(elevs-1,elevators-2))
		data.append(Single(reps,flr,elevs,peeps,elevCapacity))
	print "%d,"%flr + ",".join(["%.2f"%x for x in data])

end = time()

print("Elapsed time: %f"%((end-start)/60))