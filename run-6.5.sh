#!/usr/bin/env bash
set -xeou pipefail
#rm -r -f binaries*
#rm -r -f coverage
#run clone and extraction passed to identify function names for the combination generator
./coverage-improver.sh 
#create performance data with block frequencies
./blockfrequency.sh 

#we need all the combinations to compare with the SROH paper (heuristic-based)
#rm -r -f combination
./combinator.sh 0 10 25 50 100


############### BEGIN Section 6.5 ##################
#IMPORTANT: make sure there is no constraints, otherwise the ilp generator will force them on the solution
rm -r -f constraints
#generate SROH benchmark (based on https://github.com/mr-ma/sip-eval/tree/acsac)
./generator-ilp-acsac.sh manifest 
#extract constraints from the maximum manifest setting
python constraint_extractor.py binaries-acsac-manifest constraints-acsac
#Constraints will be read when available
#optimize for overhead with the maximum protection constraints
./generator-ilp-acsac.sh "overhead"
if [ $? -eq 0 ]; then
        echo 'OK Generator '
else
        echo 'FAIL Generator'
        exit
fi

#run binaries
./runexec-binaries.py binaries-acsac-manifest
if [ $? -eq 0 ]; then
        echo 'OK runexec binaries-manifest '
else
        echo 'FAIL runexec binaries-manifest '
        exit
fi

#run binaries
./runexec-binaries.py binaries-acsac-overhead
if [ $? -eq 0 ]; then
        echo 'OK runexec binaries-overhead '
else
        echo 'FAIL runexec binaries-overhead '
        exit
fi

./measure.py binaries-acsac-manifest/
./measure.py binaries-acsac-overhead/
############### END Section 6.4 ##################


python plot-dump-combined.py -p True
echo 'Benchmark is dumped into performance-evaluation-combined-percentage.pdf' 

