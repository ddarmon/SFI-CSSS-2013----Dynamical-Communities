# This script extracts the state series for computing informational
# coherence.

import ipdb
import cssr_interface
import numpy
import collections
import glob
import pylab

from filter_data_methods import *

def get_total_state_series(fname):
	# Get out all the CSM related structures we need.

	CSM = get_CSM(fname = fname)

	epsilon_machine = get_epsilon_machine(fname = fname)

	zero_order_CSM = generate_zero_order_CSM(fname)

	# Get out the timeseries.

	ofile = open('{}.dat'.format(fname))

	days = [line.rstrip('\n') for line in ofile]

	states, L = get_equivalence_classes(fname)

	overall_states = []

	for day in days:
		prediction, state_series = CSM_filter(CSM, zero_order_CSM, states, epsilon_machine, day, L, verbose = False)

		day_states = state_series.split(';')

		overall_states.extend(day_states[(L_max - L + 1):])

	return overall_states

L_max = 11

suffix = ''
user1  = '1'
user2  = '3'

fname1 = 'sample{}{}'.format(user1, suffix)

timeseries1 = get_total_state_series(fname1)

# Get out the state labels for the first
# time series.

symbols_x = []

for sym in timeseries1:
	if sym not in symbols_x:
		symbols_x.append(sym)

# Create a new, empty count array

count_array = collections.defaultdict(int)

fname2 = 'sample{}{}'.format(user2, suffix)

timeseries2 = get_total_state_series(fname2)

# Get out the symbols for the second timeseries

symbols_y = []

for sym in timeseries2:
	if sym not in symbols_y:
		symbols_y.append(sym)

# Compute the joint counts.

n = len(timeseries1)

assert n == len(timeseries2), 'The time series are of different length!'

n_symbols_x = len(symbols_x)
n_symbols_y = len(symbols_y)

# This computes the count table

for ind in range(n):
	count_array[(timeseries1[ind], timeseries2[ind])] += 1

# Generate the estimated joint pmf

jpmf = numpy.zeros((n_symbols_x, n_symbols_y))

for ind_x, symbol_x in enumerate(symbols_x):
	for ind_y, symbol_y in enumerate(symbols_y):
		jpmf[ind_x, ind_y] = count_array[(symbol_x, symbol_y)]/float(n)

# Compute the estimated mutual information from the pmf

mi = 0

for ind_x in range(n_symbols_x):
	denom1 = jpmf[ind_x, :].sum() # p(x)

	for ind_y in range(n_symbols_y):
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

p_x = jpmf.sum(axis = 1) # The marginal pmf for X

for ind_x in range(n_symbols_x):
	p = p_x[ind_x]

	if p == 0:
		pass
	else:
		H_x += p*numpy.log2(p)

H_x = -H_x

# Estimate the entropy of Y

H_y = 0

p_y = jpmf.sum(axis = 0) # The marginal pmf for Y

for ind_y in range(n_symbols_y):
	p = p_y[ind_y]

	if p == 0:
		pass
	else:
		H_y += p*numpy.log2(p)

H_y = -H_y

# Estimate the informational coherence.

if mi == 0 or numpy.min((H_x, H_y)) == 0: # We use the convention that 0/0 = 0.
	ic = 0
elif len(symbols_x) == 1 or len(symbols_y) == 1:
	ic = 0	# A single state process cannot have non-zero informational coherence.
else:
	ic = mi / numpy.min((H_x, H_y))

print 'The mutual information between the two timeseries is... {}'.format(mi)
print 'The informational coherence between the two timeseries is... {}'.format(ic)