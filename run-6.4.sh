#!/usr/bin/env bash
set -xeou pipefail
rm -r -f binaries*
rm -r -f coverage
#run clone and extraction passed to identify function names for the combination generator
./coverage-improver.sh $@
#extract filter fils (i.e. combinations) from the list of available function names
#for this experiment we only need coverage of 100% protection, no partial protections needed
rm -r -f combination
rm -r -f constraints
./combinator.sh 0 100
#create performance data with block frequencies
./blockfrequency.sh $@


############### BEGIN Section 6.4 ##################
#generate maximum protected binaries aka obj=manifest
./generator.sh $@
#extract constraints from the maximum manifest setting
python constraint_extractor.py binaries-manifest

#optimize for overhead with the maximum protection constraints
./generator-ilp.sh binaries-overhead "overhead"
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
