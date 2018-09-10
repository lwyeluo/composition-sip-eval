OPT=opt
INPUT_DEP_PATH=/usr/local/lib/
FILES=/home/sip/eval/local_dataset/*.bc
COVERAGEPATH=/home/sip/eval/coverage/
configs=/home/sip/eval/lib-config
for f in $FILES
do
	bitcode=$f
	echo $f
	filename=${f##*/}
	libconfig=$configs/$filename
	echo "$libconfig"
	output_dir=$COVERAGEPATH/reports/$filename
	mkdir -p $output_dir
	output=$COVERAGEPATH$filename
        if [ $# -eq 1 ]; then
             if [ -f "$output" ]; then
                 echo "skipping $output generation, it already exists"
                 continue
             fi
        fi
	echo "Output will be written to $output"
	${OPT} -load $INPUT_DEP_PATH/libInputDependency.so -load /usr/local/lib/libLLVMdg.so -load $INPUT_DEP_PATH/libTransforms.so $bitcode -lib-config=$libconfig -strip-debug -unreachableblockelim -goto-unsafe  -extract-functions -transparent-cache -dependency-stats -dependency-stats-file=$output_dir/dependency.stats -extraction-stats -extraction-stats-file=$output_dir/extract.stats -globaldce -o $output
	if [ $? -eq 0 ]; then
		echo 'OK Transform'
	else
		echo 'FAIL Transform'
		echo "${OPT} -load $INPUT_DEP_PATH/libInputDependency.so -load $INPUT_DEP_PATH/libTransforms.so $bitcode -clone-functions -extract-functions -o $output"
		exit
	fi
done
