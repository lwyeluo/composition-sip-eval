#!/usr/bin/env bash
source env.sh

EVAL_LIB=/home/sip/eval/passes/build/lib
FILES=/home/sip/eval/coverage/*.bc
coverage_dir=/home/sip/eval/coverage
CSVPATH=/home/sip/eval/combination
num_combination=20
func_coverage="$@"
#func_coverage="0 10 25 50 100"
#func_coverage="0 100"
for f in ${FILES}
do
	bitcode=${f}
	echo ${f}
	filename=${f##*/}
	filedir="$CSVPATH/$filename"

	mkdir -p ${filedir}
	for coverage in ${func_coverage}
	do
		output="$filedir/$coverage"
		if [ $# -eq 1 ]; then
		    SKIP=1
		    for (( i=0; i<$num_combination; i++ ))
		    do
                if [ ! -f "$output/$i" ]; then
                    SKIP=0
                fi
            done

            if [ "$SKIP" -eq "1" ]; then
                echo "skipping $output generation, it already exists"
                continue
            fi
        fi

		mkdir -p ${output}
		if [ ${coverage} -ne 0 ]; then
			echo "handling coverage ${coverage}"
			echo "Output will be written to ${output}"

			${OPT} -load $EVAL_LIB/libEval.so \
			    ${bitcode} \
			    -combinator-func \
			    -coverage=$coverage \
			    -combinations=${num_combination} \
			    -out-path=${output}/ \
			    -o /dev/null

			if [ $? -eq 0 ]; then
				echo 'OK Transform'
			else
				echo 'FAIL Transform'
				exit
			fi
		fi
	done
done
