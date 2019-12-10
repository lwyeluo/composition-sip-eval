#!/usr/bin/env bash
set -euo pipefail
source env.sh

EVAL_LIB=/home/sip/eval/passes/build/lib
FILES=/home/sip/eval/mibench-cov/*.bc
CSVPATH=/home/sip/eval/blockfrequency
link_libraries=/home/sip/eval/link-libraries/
args_path=/home/sip/eval/cmdline-args

export LD_PRELOAD="$SC_PATH/hook/build/libminm.so"

for f in ${FILES}
do
	bitcode=${f}
	echo ${f}
	filename=${f##*/}
	filedir="$CSVPATH/$filename"

	mkdir -p ${filedir}

    output="$filedir"

    echo "Output will be written to ${output}"

    libraries=""
	if [ -f "${link_libraries}${filename}" ]; then
		libraries=$(<${link_libraries}${filename})
	fi

    ${CLANG} ${bitcode} \
        -fprofile-generate \
        -o "${output}/${filename}" \
        ${libraries}

    if [ $? -eq 0 ]; then
        echo 'OK Transform'
    else
        echo 'FAIL Transform'
        exit
    fi


	cmd_args=""
	if [ -f "${args_path}/${filename}" ]; then
		cmd_args=$(tr '\n' ' ' < "${args_path}/${filename}")
	fi
	set +e
    echo ${output}/${filename} ${cmd_args} "> /dev/null"
    eval "${output}/${filename} ${cmd_args} > /dev/null"
    set -e

    mv $(pwd)/default_*.profraw "${output}/default.profraw"
    llvm-profdata-7 merge "${output}/default.profraw" -output="${output}/${filename}.prof"
    rm "${output}/default.profraw"
done


