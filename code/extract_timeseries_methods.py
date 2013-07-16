import ipdb
import numpy
import pylab
import datetime
import random

from dividebyday import divide_by_day, binarize_timeseries

def parsedate(datestring):
    part1, part2 = datestring.split(' ')
    
    year, month, day = part1.split('-')
    
    hour, minute, second = part2.split(':')
    
    return year, month, day, hour, minute, second

def coarse_resolution(binarized, iresolution = 60):
    # Recall: The current resolution is in seconds. We want to be able
    # to group together anything from seconds

    # The number of bins we'll have after coarsening.

    n_coarsebins = numpy.divide(binarized.shape[0], iresolution)

    # An (empty) binary time series to hold the
    # coarsened time series.

    binarized_coarse = numpy.zeros(n_coarsebins)

    for cind in range(n_coarsebins):
        binarized_coarse[cind] = numpy.sum(binarized[(cind*iresolution):((cind + 1)*iresolution)])
    
    # Convert the *number* of tweets in the time interval
    # into *whether* a tweet occurs in that time interval.
    
    binarized_coarse[binarized_coarse != 0] = 1
    
    return binarized_coarse

def plot_raster(binarized, num_bins, axarr, axind, colored = False):
    if len(axarr) == 1:
        ax = axarr
    else:
        ax = axarr[axind]

    if colored:
        if 0 <= axind <= 39: # This is the training set
            ax.set_axis_bgcolor("g")
        elif 39 <= axind <= 44:
            ax.set_axis_bgcolor("y")
        else:
            ax.set_axis_bgcolor("r")

    if numpy.sum(binarized) == 0: # There's nothing to plot.
        pass
    else: # There's something to plot.
        ax.vlines(numpy.arange(num_bins)[binarized==1], -0.5, 0.5)

    ax.yaxis.set_visible(False)
    ax.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        color = 'white')

def include_date(date):
    if (date.month == 9) and (date.day == 7 or date.day == 8 or date.day == 20): # Dates in September to exclude
        toinclude = False
    elif (date.month == 10) and (date.day == 18):
        toinclude = False
    elif date > datetime.datetime(month = 11, day = 18, year = 2012, hour = 23):
        toinclude = False
    else:
        toinclude = True

    return toinclude

def export_ts(ts, user_id, num_bins, toplot = False, saveplot = True, iresolution = None):
    if iresolution != None:
        fname = 'timeseries/byday-{0}s-{1}.dat'.format(iresolution, user_id)
    else:
        fname = 'timeseries/byday-1s-{0}.dat'.format(user_id)
    
    ofile = open(fname, 'w')

    if toplot == True or saveplot == True:
        f, axarr = pylab.subplots(len(ts), sharex = True)

    if iresolution != None:
        num_bins_coarse = num_bins / iresolution # Account for the fact that we plan to coarsen the timeseries

    for axind, day in enumerate(ts):
        if len(axarr) == 1:
            ax = axarr
        else:
            ax = axarr[axind]

        if day[0] == None: # We've hit on a day that didn't have any Twitter activity

            binarized = numpy.zeros(num_bins)
        else: # The day has legitimate tweets
            binarized = binarize_timeseries(day, num_bins)

        if iresolution != None:
            binarized = coarse_resolution(binarized, iresolution = iresolution)

            if day[0] != None: # We only need to plot the raster if there are points to plot
                if toplot == True or saveplot == True:
                    plot_raster(binarized, num_bins_coarse, axarr, axind)
            else: # We still need to fix how the axes look, even when we don't plot
                if toplot == True or saveplot == True:
                    ax.yaxis.set_visible(False)
        else:
            if day[0] != None:
                if toplot == True or saveplot == True:
                    plot_raster(binarized, num_bins, axarr, axind)
            else: # We still need to fix how the axes look, even when we don't plot
                if toplot == True or saveplot == True:
                    ax.yaxis.set_visible(False)

        for symbol in binarized:
            ofile.write("{0}".format(int(symbol)))

        ofile.write("\n")

    if toplot == True or saveplot == True:
        if iresolution == None:
            pylab.xlabel('Time (each time tick corresponds to 1 s)')
        else:
            pylab.xlabel('Time (each time tick corresponds to {} s)'.format(iresolution))

        pylab.locator_params(axis = 'x', nbins = 5)

    if saveplot == True:
        if iresolution == None:
            pylab.savefig('raster-1s-{0}.pdf'.format(user_id))
        else:
            pylab.savefig('raster-{0}s-{1}.pdf'.format(iresolution, user_id))

        pylab.close(f)
    
    if toplot == True:
        pylab.show()

    ofile.close()