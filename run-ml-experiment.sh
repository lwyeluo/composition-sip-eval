
function waitforjobs {
	while test $(jobs -p | wc -w) -ge "$1"; do wait -n; done
}

bash generate-ml-files.sh
for ds in 'simple-cov' 'mibench-cov'; do
	waitforjobs $(nproc)
	echo SPAWNING $(nproc) processes to generate CSV files from labled BC samples
	#echo bash ../program-dependence-graph/collect-seg-dataset-features.sh LABELED-BCs/$ds skip &
	#echo bash ../program-dependence-graph/collect-seg-dataset-features.sh LABELED-BCs/$ds skip &
	#echo bash ../program-dependence-graph/collect-seg-dataset-features.sh LABELED-BCs/$ds  skip &
	#echo bash ../program-dependence-graph/collect-seg-dataset-features.sh LABELED-BCs/$ds skip &
	bash ../program-dependence-graph/collect-seg-dataset-features.sh LABELED-BCs/$ds skip > /dev/null &
	bash ../program-dependence-graph/collect-seg-dataset-features.sh LABELED-BCs/$ds skip > /dev/null &
	bash ../program-dependence-graph/collect-seg-dataset-features.sh LABELED-BCs/$ds skip > /dev/null &
	bash ../program-dependence-graph/collect-seg-dataset-features.sh LABELED-BCs/$ds skip > /dev/null &
done
waitforjobs 1
for ds in 'simple-cov' 'mibench-cov'; do
	waitforjobs $(nproc)
	echo SPAWNING $(nproc) processes to generate H5 files from the CSV files
	bash ../sip-ml/ml-scripts/run-extractions.sh ../eval/LABELED-BCs/$ds/ RESULTS-ML/$ds & 
	bash ../sip-ml/ml-scripts/run-extractions.sh ../eval/LABELED-BCs/$ds/ RESULTS-ML/$ds & 
	bash ../sip-ml/ml-scripts/run-extractions.sh ../eval/LABELED-BCs/$ds/ RESULTS-ML/$ds & 
	bash ../sip-ml/ml-scripts/run-extractions.sh ../eval/LABELED-BCs/$ds/ RESULTS-ML/$ds & 
done
waitforjobs 1
for ds in 'simple-cov' 'mibench-cov'; do
	waitforjobs $(nproc)
	echo SPAWNING $(nproc) processes to train ML models 
	bash ../sip-ml/ml-scripts/run-predictions.sh RESULTS-ML/$ds/ & 
	bash ../sip-ml/ml-scripts/run-predictions.sh RESULTS-ML/$ds/ &
	bash ../sip-ml/ml-scripts/run-predictions.sh RESULTS-ML/$ds/ &
	bash ../sip-ml/ml-scripts/run-predictions.sh RESULTS-ML/$ds/ &
done
waitforjobs 1
for ds in 'simple-cov' 'mibench-cov'; do
	echo DUMPING CSV result files in RESULTS-ML/$ds/
	python3 ../sip-ml/ml-scripts/dump-fscore-table.py RESULTS-ML/$ds/
done


