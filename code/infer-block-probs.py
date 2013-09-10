# When the community structure is known,
# this code infers the probability of inside / outside
# edges in the obvious way.

# DMD, 090913-21-22

import numpy
from network_methods import get_adjacency

adj_mat, Nv = get_adjacency('adj_mat.txt')

A = numpy.zeros((Nv, Nv))

for out_node in adj_mat:
	for in_node, weight in adj_mat[out_node]:
		# We'll record the entire adjacency
		# matrix, to make inferring the
		# in / out degrees easier.

		A[out_node, in_node] = 1
		A[in_node, out_node] = 1

for row_ind in range(Nv):
	print row_ind, numpy.sum(A[row_ind, :])

# Recall that vertices 0..39 are in community 1,
# 40..79 are in community 2, etc.

in_props = numpy.zeros(Nv)
out_props = numpy.zeros(Nv)

per_comm = 40.

for node_ind in range(Nv):
	if node_ind < 40:
		in_props[node_ind] = A[:40, node_ind].sum()/per_comm
		out_props[node_ind] = A[40:, node_ind].sum()/(Nv - per_comm)
	elif node_ind > 40 and node_ind < 80:
		in_props[node_ind] = A[40:80, node_ind].sum()/per_comm
		out_props[node_ind] = (A[:40, node_ind].sum() + A[80:, node_ind].sum())/(Nv - per_comm)
	elif node_ind > 80 and node_ind < 120:
		in_props[node_ind] = A[80:120, node_ind].sum()/per_comm
		out_props[node_ind] = (A[:80, node_ind].sum() + A[120:, node_ind].sum())/(Nv - per_comm)
	elif node_ind > 120:
		in_props[node_ind] = A[120:, node_ind].sum()/per_comm
		out_props[node_ind] = A[:120, node_ind].sum()/(Nv - per_comm)

print 'p_in = {}'.format(in_props.mean())
print 'p_out = {}'.format(out_props.mean())

# p_in = 0.1, p_out = 0.05