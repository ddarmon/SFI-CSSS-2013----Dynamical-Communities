import numpy

from extract_timeseries_methods import *

from network_methods import get_adjacency

adj_matrix, Nv = get_adjacency('adj_mat.txt')

# ires = 60*5
ires = 5

for ind in range(Nv):
	if (ind % 10) == 0:
		print 'Coarsening user {}...'.format(ind)
		
	user = str(ind)

	ofile = open('sample{}.dat'.format(user))

	# The inverse resolution to use. That is,
	# ires is the number of seconds to bin together.
	# In the case below, ires = 600 means we'll
	# bin together disjoint intervals of 600 seconds
	# (10 minutes), coarsening to a 1 if a tweet
	# occurred and a 0 if a tweet did not occur
	# in that time bin.

	wfile = open('sample-{}s-{}.dat'.format(ires, user), 'w')

	for ind, line in enumerate(ofile):
		data = line.rstrip()

		binarized = numpy.fromstring(data, dtype = 'int8') - 48

		binarized_coarse = coarse_resolution(binarized, iresolution = ires)

		for symbol in binarized_coarse:
			wfile.write("{0}".format(int(symbol)))

		wfile.write('\n')

	wfile.close()

	ofile.close()