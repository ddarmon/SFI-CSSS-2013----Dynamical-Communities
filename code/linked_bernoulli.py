# Generate a realization from coupled
# inhomogeneous Bernoulli processes
# with a prescribed weighted, directed 
# adjacency matrix. 

import numpy
import pylab
import ipdb

from network_methods import get_adjacency

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Various parameters:

# The amplitude of the base rate, from
# 0 to lam_max.

p_max = 0.001

# The period of the oscillation.

T = 86400.

# The frequency of oscillation.

omega = (2*numpy.pi)/T

# Loop until we've reached the appropriate amount of 
# time.

# T_final = 86400*5
T_final = 86400

# The weighted adjacency matrix, stored as a dictionary of the form:
# {from_node : [(to_node1, weight1), (to_node2, weight2)]}

# adj_matrix = {0 : [(1, uniform_weight), (2, uniform_weight), (3, uniform_weight), (4, uniform_weight), (5, 0.005)], 5 : [(6, uniform_weight), (7, uniform_weight), (8, uniform_weight), (0, 0.005)]}

adj_matrix, Nv = get_adjacency('adj_mat.txt')

scale_weights = 0.25 # How much to scale all of the weights by

def p(t):
	# return p_max*(0.5 + 0.5*numpy.sin(omega*t))

	return p_max*numpy.ones(t.shape)

# The baseline rate, before accounting for any spikes.

Pt = p(numpy.tile(numpy.arange(T_final), (Nv, 1)))

# A placeholder for all of the spikes. It is a 
# Nv by T_final array.

Xt = numpy.zeros((Nv, T_final))

# Us is all of the random draws we will need.

Us = numpy.random.rand(Nv, T_final)

# The skeleton to add for each observed spike.

impulse_skeleton = numpy.concatenate((numpy.ones(1), numpy.power(numpy.arange(1., 50.), -3)))

for t in range(0, T_final):
	if (t % 1000) == 0:
		print 'At timestep {}...'.format(t)

	# Determine which nodes were active.

	active_bool = (Us[:, t] < Pt[:, t])

	active_inds  = numpy.arange(Nv)[active_bool]

	# Update the matrix of states.

	Xt[active_inds, t] = 1

	# Update Pt based on which nodes spikes.
	# To do this, we look at the weighted
	# adjacency matrix and only add a
	# contribution to the appropriate nodes.

	for from_ind in active_inds:
		neighbors = adj_matrix.get(from_ind, [])

		# Account for when impulse_skeleton is longer
		# than the remaining timeseries.

		diff_T = T_final - t

		if diff_T <= len(impulse_skeleton):
			amount_forward = diff_T
		else:
			amount_forward = len(impulse_skeleton)+1


		for to_ind, to_weight in neighbors:
			Pt[to_ind, t+1:t+amount_forward] += scale_weights*to_weight*impulse_skeleton[:amount_forward-1]

# Save the spikes to output files.

for ind in range(Nv):
	if (ind % 10) == 0:
		print 'Saving data for vertex {}...'.format(ind)
	ofile = open('sample{}.dat'.format(ind), 'w')
	for spike in Xt[ind, :]:
		ofile.write('{}'.format(int(spike)))
	ofile.close()

# Look at how spikes propagate through dynamical communities.

# pylab.plot(Xt[:40,:].sum(axis = 0), '.')
# pylab.plot(Xt[40:80,:].sum(axis = 0), '.')
# pylab.plot(Xt[80:120,:].sum(axis = 0), '.')
# pylab.plot(Xt[120:160,:].sum(axis = 0), '.')

# Plot a few figures.

# f, axarr = pylab.subplots(Nv, sharex = True)

# for axind in range(Nv):
# 	axarr[axind].vlines(numpy.arange(T_final)[Xt[axind, :] == 1], ymin = -0.5, ymax = 0.5)
# 	axarr[axind].yaxis.set_visible(False)

# f, axarr = pylab.subplots(Nv, sharex = True)

# for axind in range(Nv):
# 	axarr[axind].plot(numpy.arange(T_final), Pt[axind, :])
# 	axarr[axind].yaxis.set_visible(False)

# pylab.show()