import collections
import numpy

def get_adjacency(fname):
	# Get the directed, weighted
	# adjacency matrix from a file. Also get
	# out the number of vertices.

	adj_matrix = collections.defaultdict(list)

	Nv = 0

	ofile = open(fname)

	ofile.readline() # To take care of the header

	line = ofile.readline()

	while line != '':
		from_ind, to_ind, weight = line.split(',')

		adj_matrix[int(from_ind)].append((int(to_ind), float(weight)))

		line = ofile.readline()

		Nv = numpy.max((int(from_ind), int(to_ind), Nv))

	ofile.close()

	# Since we started labeling nodes at 0.

	Nv = Nv + 1

	return adj_matrix, Nv