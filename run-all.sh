#!/usr/bin/env bash
set -xeou pipefail
#run clone and extraction passed to identify function names for the combination generator
./coverage-improver.sh $@
#extract filter fils (i.e. combinations) from the list of available function names
./combinator.sh $@
#generat prottected binaries
./generator.sh $@
if [ $? -eq 0 ]; then
	echo 'OK generator'
else
	echo 'FAIL generator'
	exit
fi
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

