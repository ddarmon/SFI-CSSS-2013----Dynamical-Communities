# Code to compute the mutual information between two users, given a
# the files containing their timeseries.

import collections
import numpy
import random
import glob
import pylab

from filter_data_methods import *

from network_methods import get_adjacency

# window = 60*5
window = 5

prefix = 'sample-{}s-'.format(window)
# prefix = 'sample'
suffix = ''

adj_matrix, Nv = get_adjacency('adj_mat.txt')

mi_mat = numpy.zeros((Nv, Nv))

inds = range(Nv)

# Simulate when we *don't* know 
# the blocks.

# random.shuffle(inds)

for i in range(Nv):
	print 'Working on user {}...'.format(i)
	
	ind1 = inds[i]
	for j in range(i + 1, Nv):
		ind2 = inds[j]
		user1 = str(ind1)
		user2 = str(ind2)

		fname1 = '{}{}{}.dat'.format(prefix, user1, suffix)

		# Read in the two timeseries of interest.

		ofile = open(fname1)

		# Since mutual information doesn't incorporate any sort
		# of lag, we'll concatenate all of the days together.

		timeseries1 = ''

		for line in ofile:
			timeseries1 += line.rstrip('\n')

		ofile.close()

		count_array = collections.defaultdict(int)

		fname2 = '{}{}{}.dat'.format(prefix, user2, suffix)

		ofile = open(fname2)

		timeseries2 = ''

		for line in ofile:
			timeseries2 += line.rstrip('\n')

		ofile.close()

		# Compute the joint counts.

		n = len(timeseries1)

		assert n == len(timeseries2), 'The time series are of different length!'

		# The symbols we'll use. Assume binary.

		symbols = ['0', '1']

		n_symbols = len(symbols)

		# This computes the count table

		for ind in range(n):
			count_array[(timeseries1[ind], timeseries2[ind])] += 1

		# Generate the estimated joint pmf

		jpmf = numpy.zeros((n_symbols, n_symbols))

		for ind_x, symbol_x in enumerate(symbols):
			for ind_y, symbol_y in enumerate(symbols):
				jpmf[ind_x, ind_y] = count_array[(symbol_x, symbol_y)]/float(n)

		# Compute the estimated mutual information from the pmf

		mi = 0

		for ind_x in range(n_symbols):
			denom1 = jpmf[ind_x, :].sum() # p(x)

			for ind_y in range(n_symbols):
				num = jpmf[ind_x, ind_y] # p(x, y)
				
				denom2 = jpmf[:, ind_y].sum() # p(y)

				denom = denom1*denom2 # p(x)*p(y)

				# By convention, 0 log(0 / 0) = 0
				# and 0 log(0 / denom) = 0. We won't have
				# to worry about running into num log(num / 0)
				# since we're dealing with a discrete alphabet.

				if num == 0: # Handle the mutual information convention.
					pass
				else:
					mi += num * numpy.log2(num/denom)

		# Normalize the mutual information, using the fact that
		# I[X; Y] <= min{H[X], H[Y]}, to give the informational
		# coherence,
		# 	IC[X; Y] = I[X; Y] / min{H[X], H[Y]}
		# again the convention that 0/0 = 0.

		# Estimate the entropy of X

		H_x = 0

		for ind_x in range(n_symbols):
			p = jpmf[ind_x, :].sum()

			if p == 0:
				pass
			else:
				H_x += p*numpy.log2(p)

		H_x = -H_x

		# Estimate the entropy of Y

		H_y = 0

		for ind_y in range(n_symbols):
			p = jpmf[:, ind_y].sum()

			if p == 0:
				pass
			else:
				H_y += p*numpy.log2(p)

		H_y = -H_y

		# Estimate the normalized mutual information.

		Hmin = numpy.min((H_x, H_y))

		if Hmin == 0 and mi == 1:
			nmi = 1
		elif Hmin == 0 and mi == 0:
			nmi = 0
		else:
			nmi = mi / Hmin

		mi_mat[i, j] = nmi

vmax = numpy.max(mi_mat)

mi_mat = mi_mat + mi_mat.T

# mi_mat[mi_mat == 0] = numpy.nan

pylab.figure()
pylab.imshow(mi_mat, interpolation = 'nearest', vmin = 0, vmax = vmax)
pylab.xlabel('User $j$')
pylab.ylabel('User $i$')
pylab.colorbar()
pylab.savefig('adj_weighted.png')

pylab.show()

# Save the edges weighted by the mutual
# information between the edges.

A = numpy.zeros((Nv, Nv))

wfile = open('adj_mat_weighted.txt', 'w')

for fromnode in adj_matrix:
	for tonode, comm_weight in adj_matrix[fromnode]:
		if fromnode < tonode:
			A[fromnode, tonode] = 1
		else:
			A[tonode, fromnode] = 1

		wfile.write('{},{},{}\n'.format(fromnode, tonode, mi_mat[fromnode, tonode]))

wfile.close()

pylab.figure()
pylab.imshow(A + A.T, interpolation = 'nearest', vmin = 0, vmax = vmax, cmap = 'Greys')
pylab.xlabel('User $j$')
pylab.ylabel('User $i$')

pylab.savefig('adj_unweighted.png')

pylab.show()