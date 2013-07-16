import datetime
import numpy
import pylab
import ipdb

def is_same_day(day1, day2):
	if (day1.day != day2.day):
		is_same = False
	elif (day1.month != day2.month):
		is_same = False
	elif (day1.year != day2.year):
		is_same = False
	else:
		is_same = True

	return is_same

def is_next_day(day1, day2):
	# We'll ask 'Is day2 the day after day1?'

	next_day = day1 + datetime.timedelta(days = 1)

	if (next_day.day != day2.day):
		is_same = False
	elif (next_day.month != day2.month):
		is_same = False
	elif (next_day.year != day2.year):
		is_same = False
	else:
		is_same = True

	return is_same

def is_in_window(day, starttime, endtime):
	diff_back = (day - starttime).total_seconds()
	diff_forward = (endtime - day).total_seconds()
	if (diff_back < 0) or (diff_forward < 0):
		is_in = False
	else:
		is_in = True

	return is_in

def binarize_timeseries(day, num_bins):
	binarized = numpy.zeros(num_bins)

	binarized[day] = 1

	return binarized

def divide_by_day(reference_start, reference_stop, ts, user_id = 'NA', to_reference_stop = True):
	# Idea: Set a starttime and an endtime. Collect all of the ts[i]
	# that lie between starttime and endtime. Generate a binary timeseries
	# from that.

	# Use reference_start and reference_stop to decide what day we should
	# start from and end on in terms of generating a time series for 
	# each user.

	# to_reference_stop is a flag that decides whether we should
	# continue padding forward in time with empty days. If True,
	# we do this. If false, we stop when we run out of timepoints
	# in ts.

	# For now, set these to 6am to 10pm

	starttime = datetime.datetime(year = reference_start.year, month = reference_start.month, day = reference_start.day, hour = 6)
	endtime   = datetime.datetime(year = reference_start.year, month = reference_start.month, day = reference_start.day, hour = 22)

	num_bins = (endtime - starttime).total_seconds() + 1

	# ts_by_day is a list of lists, where the internal lists contain the
	# timeseries broken up by day

	ts_by_day = [[]]

	# days is a list of the the days that correspond to each of the lists
	# in ts_by_day. This will make throwing out 'bad' days easier later
	# on.

	days = []

	newday_appended = False # Keep track of whether I've appended for the new day.

	cur_day = ts[0]

	# For the first timepoint we see, we need to check if we need to pre-pad
	# with empty days. For example, if the reference date is 9/7/12, and we
	# start at 9/10/12, we need to prepad days for 9/7/12, 9/8/12, and 9/9/12.

	timepoint = ts[0]

	# Check if we've started on the reference_start

	if is_same_day(timepoint, starttime):
		pass
	else:
		# We need to prepad days until timepoint is the day after
		# starttime.

		while not is_same_day(day1 = timepoint, day2 = starttime):
			days.append(starttime)

			if len(ts_by_day[-1]) == 0:
				ts_by_day[-1].append(None)
			else:
				ts_by_day.append([None])

			starttime += datetime.timedelta(days = 1)
			endtime += datetime.timedelta(days = 1)

		ts_by_day.append([]) # This initializes ts_by_day
							 # to the expected initial state.
							 # before prepadding.

	for counter in range(0, len(ts)):
		timepoint = ts[counter]

		# if timepoint.month == 11 and timepoint.day == 11:
		# 	ipdb.set_trace()

		# Check if we're still in the same day bracketed 
		# by starttime and endtime.

		if (is_same_day(timepoint, starttime)): # we're in the same day, so append if we're in the window
			if (is_in_window(timepoint, starttime, endtime)): # We're in the desired window
				ts_by_day[-1].append((timepoint - starttime).total_seconds())

				if newday_appended == False: # We haven't appended for this day yet
					days.append(starttime)

					newday_appended = True

			else: # we're not in the desired window, so don't record it
				pass

		else: # we're not in the same day, so append a new day to ts_by_day

			# Check if we need to add a blank day that we missed
			# because all of the day's tweets occurred outside the window of
			# interest.

			if len(ts_by_day[-1]) == 0:
				ts_by_day[-1].append(None)

				days.append(cur_day)

			# Add a list [None] for each day where no Tweets occur.

			if not is_next_day(starttime, timepoint): # The new timepoint isn't the next day, so we want to add [None]'s to our list until we get to timepoint
				while not is_next_day(starttime, timepoint):
					# We'll increment the day until we reach the current timepoint

					starttime += datetime.timedelta(days = 1)

					if len(ts_by_day[-1]) == 0:
						ts_by_day[-1].append(None)
					else:
						ts_by_day.append([None])

					days.append(starttime)

			if len(ts_by_day[-1]) != 0:
				ts_by_day.append([])

			newday_appended = False

			# Update our window to the current day

			starttime = starttime.replace(day = timepoint.day, month = timepoint.month, year = timepoint.year)

			endtime = endtime.replace(day = timepoint.day, month = timepoint.month, year = timepoint.year)

			if (is_in_window(timepoint, starttime, endtime)): # We're in the desired window
				ts_by_day[-1].append((timepoint - starttime).total_seconds())

				days.append(starttime) # Keep track of the day

				newday_appended = True # Keep track that I've accounted for this day
			else:
				pass
				
		# Record the day, in case we need to include an
		# *empty* day, which is coded as None.

		cur_day = timepoint

	if to_reference_stop:
		# If we run out of timepoints before we reach reference_stop,
		# we want to continue padding

		while not is_same_day(reference_stop, starttime):
					# We'll increment the day until we reach the reference_stop

					starttime += datetime.timedelta(days = 1)

					if len(ts_by_day[-1]) == 0:
						ts_by_day[-1].append(None)
					else:
						ts_by_day.append([None])

					days.append(starttime)


	# This gets rid of a trailing list that got appended
	# but was never added to.

	if len(ts_by_day[-1]) == 0:
		ts_by_day.pop(-1)

	assert len(ts_by_day) == len(days), "Warning: The number of days you have time series for does not match the number of days you have indices for."

	return ts_by_day, days, num_bins