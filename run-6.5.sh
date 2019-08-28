#!/usr/bin/env bash
set -xeou pipefail
#run clone and extraction passed to identify function names for the combination generator
./coverage-improver.sh $@
#extract filter fils (i.e. combinations) from the list of available function names
./combinator.sh $@
#create performance data with block frequencies
./blockfrequency.sh $@


############### BEGIN Section 6.4 ##################

#extract constraints from the maximum manifest setting
python constraint_extractor.py binaries-manifest

#optimize for overhead with the maximum protection constraints
./generator-ilp.sh binaries-manifest "overhead"
if [ $? -eq 0 ]; then
        echo 'OK Generator 6.4'
else
        echo 'FAIL Generator 6.4'
        exit
fi

#run binaries
./runexec-binaries.py binaries-manifest
if [ $? -eq 0 ]; then
        echo 'OK runexec binaries-manifest 6.4'
else
        echo 'FAIL runexec binaries-manifest 6.4'
        exit
fi

#run binaries
./runexec-binaries.py binaries-overhead
if [ $? -eq 0 ]; then
        echo 'OK runexec binaries-overhead 6.4'
else
        echo 'FAIL runexec binaries-overhead 6.4'
        exit
fi

./measure.py binaries-manifest/
./measure.py binaries-overhead/
python dump-ilp-results.py
echo 'Results are dumped in ilp_optimization_results.csv'
############### END Section 6.4 ##################


#run each protected program and measure the overhead imposed by the protection
./runexec-binaries.py binaries/
if [ $? -eq 0 ]; then
	echo 'OK runexec'
else
	echo 'FAIL runexec'
	exit
fi
#extract measured cpu and memory overhead
./measure.py binaries/
if [ $? -eq 0 ]; then
	echo 'OK measure'
else
	echo 'FAIL measure'
	exit
fi
#dump clone and extraction coverage improvement latex table
#python measure-coverage-improvements.py
#plot the extracted overhead data and dump protection coverage latex table
python plot-dump.py

