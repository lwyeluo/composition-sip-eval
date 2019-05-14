python ./runexec-binaries.py $1 -p $2
python ./measure.py $1
python ./plot-dump.py -m $1/measurements-1.json -p True

