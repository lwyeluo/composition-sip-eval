#!/usr/bin/env bash
source env.sh

USR_LIB_DIR=/usr/local/lib
FILES=$1/*.bc
COVERAGEPATH=$2/
configs=/home/sip/eval/lib-config
for f in $FILES
do
	bitcode=$f
	echo $f
	filename=${f##*/}
    	output=$COVERAGEPATH$filename

    	#if [ $# -eq 1 ]; then
        if [ -f "$output" ]; then
		echo "skipping $output generation, it already exists"
        	continue
        fi
    	#fi

	libconfig=$configs/$filename
	echo "$libconfig"
	output_dir=$COVERAGEPATH/reports/$filename
	mkdir -p $output_dir

	echo "Output will be written to $output"
	${OPT} -load $USR_LIB_DIR/libInputDependency.so \
        -load $USR_LIB_DIR/libTransforms.so \
        $bitcode \
        -lib-config=$libconfig \
        -strip-debug \
        -unreachableblockelim \
        -goto-unsafe \
        -transparent-cache \
	-delete-unreachables \
        -dependency-stats \
        -dependency-stats-file=$output_dir/dependency.stats \
        -globaldce \
        -extract-functions \
        -extraction-stats \
        -extraction-stats-file=$output_dir/extract.stats \
        -o $output
	if [ $? -eq 0 ]; then
		echo 'OK Transform'
	else
		echo 'FAIL Transform'
		exit
	fi
done
