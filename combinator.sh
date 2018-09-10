OPT=opt
EVAL_LIB=/home/sip/eval/passes/build/lib
FILES=/home/sip/eval/coverage/*.bc
coverage_dir=/home/sip/eval/coverage
CSVPATH=/home/sip/eval/combination/
num_combination=20
func_coverage="0 10 25 50 100"
for f in $FILES
do
	bitcode=$f
	echo $f
	filename=${f##*/}
	filedir="$CSVPATH$filename/"
	rm -r $filedir
	mkdir -p $filedir
	for coverage in $func_coverage
	do
		output="$filedir$coverage/"
		mkdir -p $output
		if [ $coverage -ne 0 ]; then
			echo "handling coverage $coverage"
			echo "Output will be written to $output"
			${OPT} -load $EVAL_LIB/libEval.so $bitcode -combinator-func -coverage=$coverage -combinations=$num_combination -out-path=$output -o /dev/null
			if [ $? -eq 0 ]; then
				echo 'OK Transform'
			else
				echo 'FAIL Transform'
				exit
			fi
		fi
	done
done
