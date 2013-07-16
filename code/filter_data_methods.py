import ipdb
import cssr_interface
import numpy
import collections
import sys

class state:
	def __init__(self, p_emit0 = None, s_emit0 = None, s_emit1 = None):
		self.p_emit0 = p_emit0
		self.s_emit0 = s_emit0
		self.s_emit1 = s_emit1
	
	
	def setEmit0State(self, state, prob):
		self.s_emit0 = state
		self.p_emit0 = prob
	
	def setEmit1State(self, state):
		self.s_emit1 = state

def get_equivalence_classes(fname):
	ofile = open('{0}.dat_results'.format(fname))

	# Start at state = 0, and then loop up to state = N, where 
	# N is the number of states

	state = 0
	state_list = {}

	ofile.readline()

	line = ofile.readline()

	while line != '':
		while line.split()[0] != 'distribution:':
			state_list[line.rstrip()] = state
			
			line = ofile.readline()
		state = state + 1
		for lineind in xrange(4):
			ofile.readline()
		line = ofile.readline()

	ofile.close()

	# Get out the history length used.

	L = -1

	for history in state_list:
		L = max(L, len(history))

	return state_list, L

def get_CSM(fname):
	ofile = open('{0}.dat_results'.format(fname))

	CSM = {} # A dictionary structure for the CSM

	line = ofile.readline()

	while line != '':
		state = int(line.split()[2])

		while 'distribution' not in line:
			line = ofile.readline()

		CSM[state] = float(line.split()[-1])

		for ind in xrange(3):
			ofile.readline()

		line = ofile.readline()

	ofile.close()

	return CSM

def get_epsilon_machine(fname):
	ofile = open('{}.dat_inf.dot'.format(fname))

	line = ofile.readline()

	while line[0] != '0':
		line = ofile.readline()

	epsilon_machine = collections.defaultdict(state)

	while line != '}':
		lsplit = line.split()

		from_state = lsplit[0]
		to_state = lsplit[2]
		esymbol = int(lsplit[5][1])
		eprob = float(lsplit[6])
		
		if esymbol == 0:
			epsilon_machine[from_state].setEmit0State(to_state, eprob)
		elif esymbol == 1:
			epsilon_machine[from_state].setEmit1State(to_state)
		
		line = ofile.readline()

	ofile.close()

	return epsilon_machine

def CSM_filter(CSM, zero_order_CSM, states, epsilon_machine, ts, L, verbose = True):
	# We look at most L time steps into the past. We can
	# synchronize on L - 1 timesteps, by virtue of how CSSR
	# does its filtering.

	# Note: We'll start predicting *L-1* days in. So,
	# our first prediction will be for day L.

	prediction = ''

	state_series = ''

	# We can predict on day L, since we have L - 1 days.

	cur_state = str(states.get(ts[0:L-1], 'M'))

	state_series += cur_state

	synchronized = False # Whether or not we've synchronized to the current state.
						 # Basically, can we tell what state we're in yet.

	# WE MIGHT HAVE TO REPEAT THIS MULTIPLE TIMES!!!

	if cur_state == 'M':
		if verbose == True:
			print 'Warning: The sequence \'{}\' isn\'t allowed by this CSM!'.format(ts[0:L-1])

		prediction += str(zero_order_CSM) # Since we've never seen this sequence before, we'll predict
										  # based on the most common symbol
		# prediction += 'M'
	else:
		if CSM[int(cur_state)] > 0.5:
			prediction += '1'
		else:
			prediction += '0'

		synchronized = True

	for i in xrange(L, len(ts)):
		# Now that we've synchronized, we get the new state
		# by looking at the transition that *must* have
		# occurred, given our epsilon machine.

		if synchronized:
			if ts[i-1] == '1':
				cur_state = epsilon_machine[str(cur_state)].s_emit1
			elif ts[i-1] == '0':
				cur_state = epsilon_machine[str(cur_state)].s_emit0

			if cur_state == None:
				# We have made a transition that isn't allowed by the epsilon
				# machine, so we need to resync.

				synchronized = False

				cur_state = states.get(ts[i - L:i], 'M')

				if cur_state == 'M':
					if verbose == True:
						print 'Warning: The sequence \'{}\' isn\'t allowed by this CSM!'.format(ts[i - L:i])

					prediction += str(zero_order_CSM) # Since we've never seen this sequence before, we'll predict
										  			  # based on the most common symbol

				else:
					if CSM[int(cur_state)] > 0.5:
						prediction += '1'
					else:
						prediction += '0'

					synchronized = True
			else: # We haven't made a disallowed transition, so we can update like usual.
				if CSM[int(cur_state)] > 0.5:
					prediction += '1'
				else:
					prediction += '0'

			state_series += ';{}'.format(str(cur_state))
		else:
			cur_state = states.get(ts[i - L:i], 'M')

			if cur_state == 'M':
				if verbose == True:
					print 'Warning: The sequence \'{}\' isn\'t allowed by this CSM!'.format(ts[i - L:i])

				prediction += str(zero_order_CSM) # Since we've never seen this sequence before, we'll predict
												  # based on the most common symbol
				# prediction += 'M'
			else:
				if CSM[int(cur_state)] > 0.5:
					prediction += '1'
				else:
					prediction += '0'

				synchronized = True

			state_series += ';{}'.format(str(cur_state))

	return prediction, state_series

def zero_filter(majority_class, ts):
	# We return a prediction that is all the majority
	# class. Thus, if the user usually tweeted,
	# we'll always predict tweeting and vice versa.

	prediction = ''

	for ind in xrange(len(ts)):
		prediction += str(majority_class)

	return prediction

def compute_precision(ts_true, ts_prediction):
	numerator = 0    # In precision, the numerator is the number of true
						 # positives which are predicted correctly.
	denominator = 0	 # In precision, the denominator is the total number
					 # of predicted positives.

	for char_ind in xrange(len(ts_true)):
		if ts_prediction[char_ind] == '1': # We predicted a 1
			denominator += 1

			if ts_true[char_ind] == '1': # We predicted a 1, and it is also the right
									   # answer.
				numerator += 1

	if denominator == 0:
		print 'Warning: you didn\'t predict any tweets! By convention, set precision to 1.'

		precision = 1
	else:
		precision = numerator/float(denominator)

	return precision

def compute_recall(ts_true, ts_prediction):
	numerator = 0    # In precision, the numerator is the number of true
					 # positives which are predicted correctly.
	denominator = 0	 # In precision, the denominator is the total number
					 # of true positives.

	for char_ind in xrange(len(ts_true)):
		if ts_true[char_ind] == '1': # The true value is a 1
			denominator += 1

			if ts_prediction[char_ind] == '1': # We predicted a 1, and it is also the right
									   		 # answer.
				numerator += 1

	if denominator == 0:
		print 'Warning: no tweets were in this day! By convention, set recall to 1.'

		recall = 1
	else:
		recall = numerator/float(denominator)

	return recall

def compute_metrics(ts_true, ts_prediction, metric = None):
	# choices: 'accuracy', 'precision', 'recall', 'F'

	if metric == None or metric == 'accuracy': # By default, compute accuracy rate.
		correct = 0

		for char_ind in xrange(len(ts_true)):
			if ts_true[char_ind] == ts_prediction[char_ind]:
				correct += 1

		accuracy_rate = correct / float(len(ts_true))

		return accuracy_rate
	elif metric == 'precision':
		precision = compute_precision(ts_true, ts_prediction)

		return precision

	elif metric == 'recall':
			
		recall = compute_recall(ts_true, ts_prediction)

		return recall

	elif metric == 'F':
		precision = compute_precision(ts_true, ts_prediction)
		recall = compute_recall(ts_true, ts_prediction)

		if (precision + recall) == 0:
			F = 0
		else:
			F = 2*precision*recall/float(precision + recall)

		return F

	else:
		print "Please choose one of \'accuracy\', \'precision\', \'recall\', or \'F\'."

		return None

def run_tests(fname, CSM, zero_order_CSM, states, epsilon_machine, L, L_max = None, metric = None, type = 'CSM', print_predictions = False, print_state_series = False, verbose = True):
	# NOTE: The filename should *already have* the suffix
	# '-tune', '-test', etc.

	# If a maximum L wasn't passed (i.e. we're not trying to 
	# compare CSMs on the same timeseries data), assume that
	# we want to use *all* of the timeseries in our test.

	if L_max == None:
		L_max = L

	datafile = open('{}.dat'.format(fname))

	days = [line.rstrip() for line in datafile]

	datafile.close()

	correct_rates = numpy.zeros(len(days))

	for day_ind, day in enumerate(days):

		if type == 'CSM':
			prediction, state_series = CSM_filter(CSM, zero_order_CSM, states, epsilon_machine, ts = day, L = L, verbose = verbose)

			if print_predictions:
				# Visually compare the prediction to the true timeseries

				print 'True Timeseries / Predicted Timeseries\n'

				print day[L-1:] + '\n\n' + prediction + '\n'

			if print_state_series:
				# Print out the estimated (filtered) states that the system
				# was in at each timepoint.

				print 'Filtered State Series\n'

				print state_series + '\n'

		else:
			prediction = zero_filter(CSM, ts = day)
		
		# Originally, I had

		# ts_true = day[L_max - 1:]
		# ts_prediction = prediction[(L_max - L):]

		# here. I've changed that we always start
		# predicting after seeing L_max of the timeseries.
		# The CSM can start predicting with L_max - 1
		# of the timeseries, but this makes it easier to
		# compare across different methods.

		ts_true = day[L_max:]
		ts_prediction = prediction[(L_max - L + 1):] # This bit makes sure we predict
												 	 # on the same amount of timeseries
												 	 # regardless of L. Otherwise we 
												 	 # might artificially inflate the
												 	 # accuracy rate for large L CSMs.		
												 
		# For a given L, compute the metric rate on the tuning set.
		# Allowed metrics are 'accuracy', 'precision', 'recall', 'F'.

		correct_rates[day_ind] = compute_metrics(ts_true, ts_prediction, metric = metric)

	return correct_rates

def get_top_K_users(K = 5):
	ofile = open('user_lookup/tweet_counts_labeled.tsv')

	ofile.readline()

	users = []

	for k in range(K):
		line = ofile.readline().split('\t')

		users.append(line[0])

	ofile.close()

	return users

def get_K_users(K = 5, start = 0):
	# Get the start through (start + K) most frequent
	# tweeting users.
	#
	# That is, rank the users by their tweet rate
	# over the period of recording and then
	# pick out the user_ids for the start to start + K
	# users.

	ofile = open('user_lookup/tweet_counts_labeled.tsv')

	ofile.readline()

	users = []

	for tmp in xrange(start): # Skip over the first start users
		ofile.readline()

	for k in xrange(K):
		line = ofile.readline().split('\t')

		users.append(line[0])

	ofile.close()

	return users

def get_tweet_rate(fname):
	days = [line.rstrip('\n') for line in open(fname + '.dat')]

	tot_symbols = 0 # The total number of symbols.

	num_ones = 0 # The number of 1s in the timeseries.

	for day in days:
		for symbol in day:
			tot_symbols += 1
			if symbol == '1':
				num_ones += 1

	return num_ones / float(tot_symbols)

def generate_zero_order_CSM(fname):
	# Takes in a multiline file, and returns the 
	# 'majority class' from the timeseries. So
	# if a person mostly tweets, we return 1.
	# Otherwise, we return 0.

	tweet_rate = get_tweet_rate(fname)

	if tweet_rate > 0.5:
		return 1
	else:
		return 0