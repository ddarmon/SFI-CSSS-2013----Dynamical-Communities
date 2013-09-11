# Code that, given two possible clusterings of nodes
# into communities, computes variation of information
# between the two clusterings. This algorithm is based
# on
# 	*Comparing Clusters-An Information Based Distance by
#	Marina Meila.
#
#	DMD, 200813-00-17

from sets import Set
import numpy
import pylab
import ipdb

from itertools import islice

from filter_data_methods import get_top_K_users
import cssr_interface

# Begin by reading in the clusterings

def get_clusters(fname, user_subset = None):
	# A dictionary of the form
	# {cluster label : set of nodes in cluster}
	# using the Set object.

	clusters = {}

	ofile = open(fname)

	# Skip the header.

	ofile.readline()

	line = ofile.readline()

	count = 0

	while line != '':
		nodeid, label = line.strip().split('\t')

		if user_subset != None:
			if user_subset.get(nodeid, False):
				# If we haven't seen the label yet,
				# create an empty set for it.

				if label not in clusters:
					clusters[label] = Set([])

				# Add the corresponding node
				# to the cluster.

				clusters[label].add(nodeid)

				count += 1
			else:
				pass
		else:
			# If we haven't seen the label yet,
			# create an empty set for it.

			if label not in clusters:
				clusters[label] = Set([])

			# Add the corresponding node
			# to the cluster.

			clusters[label].add(nodeid)

			count += 1

		line = ofile.readline()

	ofile.close()

	return clusters, count

def my_log2(p):
	# Use the information theoretic
	# convention that 0 log 0 = 0.
	if p == 0:
		return 0
	else:
		return numpy.log2(p)

def my_ratio(p, q):
	# Use the information theoretic
	# convention that 0 log 0 / 0 = 0.

	if p == 0 and q == 0:
		return 0
	else:
		return p/q

vmy_log2 = numpy.vectorize(my_log2)

vmy_ratio = numpy.vectorize(my_ratio)

def compute_VI(fname1, fname2, user_subset = None):
	if user_subset == None:
		clusters0, count0 = get_clusters(fname1)

		clusters1, count1 = get_clusters(fname2)
	else:
		clusters0, count0 = get_clusters(fname1, user_subset)

		clusters1, count1 = get_clusters(fname2, user_subset)

	assert count0 == count1, "Error: The clusterings should have the same number of nodes."

	# Generate a 
	# (number of clusters 0)*(number of clusters 1)
	# confusion matrix.

	N = numpy.zeros((len(clusters0), len(clusters1)))

	# Populate the confusion matrix.

	for i, clusterid0 in enumerate(clusters0):
		cluster_i = clusters0[clusterid0]

		for j, clusterid1 in enumerate(clusters1):
			cluster_j = clusters1[clusterid1]

			N[i, j] = len(cluster_i & cluster_j)

	# Compute an empirical distribution from the
	# two clusterings, namely the probability
	# a node chosen at random is in a particular
	# cluster in the first clustering *and* a
	# particular cluster in the second clustering.

	p01 = N / float(count0)

	# Compute the marginal distributions.

	p0 = numpy.sum(p01, axis = 1)
	p1 = numpy.sum(p01, axis = 0)

	# Compute the marginal entropies.

	H0 = -numpy.sum(vmy_log2(p0)*p0)
	H1 = -numpy.sum(vmy_log2(p1)*p1)

	# Compute the mutual information.

	ratio = vmy_ratio(vmy_ratio(p01, p0[:, numpy.newaxis]), p1[numpy.newaxis, :])

	I = numpy.sum(vmy_log2(ratio)*p01)

	# Compute the variation of information

	VI = H0 + H1 - 2*I

	# Report the normalized variation of information.

	norVI = VI / numpy.log2(count0)

	return VI, norVI, N

# Use user_subset to only consider the community that
# users within user_subset have been assigned to in the
# computation of VI.

user_subset = None

fnames = ['membership_synthetic.txt', 'membership_synthetic-weighted.txt']
# fnames = ['membership_synthetic-true.txt', 'membership_synthetic-weighted.txt']

norVIs = numpy.nan*numpy.zeros((len(fnames), len(fnames)))

# Plot the confusion matrix.

for ind1 in range(len(fnames)):
	fname1 = fnames[ind1]

	for ind2 in range(ind1+1, len(fnames)):
		fname2 = fnames[ind2]

		print ind1, ind2, fname1, fname2

		VI, norVI, N = compute_VI(fname2, fname1, user_subset)

		norVIs[ind1, ind2] = norVI

		N[N == 0] = numpy.nan

		pylab.figure()
		pylab.imshow(N, interpolation = 'nearest')
		pylab.xlabel('Community : Method 1')
		pylab.ylabel('Community : Method 2')
		pylab.colorbar()
		pylab.show()

for fname in fnames:
	print fname

pylab.figure()
pylab.imshow(norVIs, interpolation = 'nearest', vmin = 0, vmax = 1)
pylab.colorbar()
pylab.show()