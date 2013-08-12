#!/bin/sh

# given the original spike data files in a direct sub-directory "timeseries_clean", transforms the 01-streams of the
# given resolution/binsize (1, 300, 600, 900) and transforms it into csv files (with trailing commas) of the timepoints
# at which tweets happened (i.e. a list of time offsets of when tweets happened) in subdirectory 1/300/600/...
# this representation is much more compact and hence also quicker to read in by any analysis tools, particularly
# for the lower resolutions (from a couple megs down to 5-10kb for a resolution of 1)

if [ "$#" -ne 1 ];
then 
  echo "Usage: ./timeseries-to-spike-csv.sh <binsize>"
  exit 1
fi
BIN=$1
mkdir $BIN
for file in `ls timeseries_clean/byday-${BIN}s-*.dat`; do
  target="$BIN/`basename $file`"
  awk -v FS="" -v RS="" -v ORS="" '{offset=1; for(i=1;i<=NF;i++) if ($i == "0") ; else if ($i == "1") print (i-offset) ","; else if ($i == "\n") { print "\n"; offset = i+1 } }' $file > "$target"
done

# time ./timeseries-to-spike-csv.sh 600
# 
# real	0m49.474s
# user	0m20.410s
# sys	0m17.014s
