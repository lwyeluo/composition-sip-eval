#!/usr/bin/env bash
set -xeou pipefail

for dataset in 'simple' 'mibench'
do
	#run clone and extraction passed to identify function names for the combination generator
	./coverage-improver.sh $dataset-dataset $dataset-cov
	#extract filter fils (i.e. combinations) from the list of available function names
	./combinator.sh $dataset-cov $dataset-comb
	#create performance data with block frequencies
	./blockfrequency.sh $dataset-cov 
	#generate maximum protected binaries aka obj=manifest
	./generator.sh manifest $dataset-cov $dataset-comb $dataset-out-manifest
	if [ $? -eq 0 ]; then
		echo 'OK Generator ALL MANIFESTS'
	else
		echo 'FAIL Generator ALL MANIFESTS'
		exit
	fi
	#extract constraints from the maximum manifest setting
	python3 constraint_extractor.py $dataset-out-manifest
	./generator.sh overhead $dataset-cov $dataset-comb $dataset-out-overhead constraints
	if [ $? -eq 0 ]; then
                echo 'OK Generator Overhead MANIFESTS'
        else
                echo 'FAIL Generator Overhead MANIFESTS'
                exit
        fi
	#optimize for overhead with the maximum protection constraints
	for optimization in 'explicit' 'implicit'
	do
		./generator.sh $optimization $dataset-cov $dataset-comb $dataset-out-$optimization 
		if [ $? -eq 0 ]; then
			echo 'OK OPTIMIZATION GENERATOR'
		else
			echo 'FAIL Generator OPTIMIZATION'
			exit
		fi
		python3 dump-defeatability.py $dataset-out-$optimization
	done
	python3 dump-defeatability.py $dataset-out-overhead 
done
echo 'Results are dumped'
