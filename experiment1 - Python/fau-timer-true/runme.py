import fau_timer
import time as t

times = 100 # number of request send to the server

# Open file for output
f = open('output.csv', 'w')

# Do the request "times" times
for i in range(times):
        # initialize fau_timer
        fau_timer.init()

	start_ticks = fau_timer.get_ticks()
	for j in range(10000000):
		1+1
	end_ticks = fau_timer.get_ticks()

	print "11Request %i: CPU Ticks: %s" % (i, end_ticks - start_ticks)


# Close output file       
f.close()
