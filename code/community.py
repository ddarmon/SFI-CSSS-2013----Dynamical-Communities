# This script takes in a weighted (or unweighted) edge list and outputs
# each node by-community using the Blondel-Guillaume-Lambiotte-Lefebvre
# multilevel community detection algorithm.

import igraph
import numpy

is_weighted = True

graph_name = 'adj_mat_weighted-tabbed.txt'

# print 'Warning: The code is currently set up to work *only* with the informational coherence files. To change, set suffix to \'\'.'
# print 'Warning: The code is currently set up to work *only* on the dense network, ignoring structural ties. To change, set suffix2 to \'\'.'

g = igraph.Graph.Read_Ncol(f = graph_name, names = True, directed = False)

weights = numpy.array([float(line.strip().split('\t')[2]) for line in open(graph_name)])

# This is a kludge fix to deal with a segmentation fault
# that occurs in the community detection code
# that I *think* has to do with those users who aren't
# 'connected enough' to other users. It doesn't seem
# to impact the 'normal' cases too much. I think the
# C code must have trouble dealing with true 0 weights.

# weights[weights <= 0] = 1e-10

if is_weighted:
	# comm = g.community_multilevel(weights = weights)
	comm = g.community_fastgreedy(weights = weights).as_clustering()
else:
	comm = g.community_multilevel(weights = None)

memberships = comm.membership

if is_weighted:
	wfile = open('membership_synthetic-weighted.txt','w')
else:
	wfile = open('membership_synthetic.txt','w')

wfile.write('user_id\tcluster_label\n')

comm_lookup = {}

for ind, membership in enumerate(memberships):
	comm_lookup[g.vs()[ind]['name']] = membership

for ind in range(len(memberships)):
	wfile.write('{}\t{}\n'.format(ind, comm_lookup[str(ind)]))

wfile.close()