#!/usr/bin/env bash
set -euo pipefail
source env.sh

bc_files=/home/sip/eval/coverage/*.bc
combination_path=/home/sip/eval/combination/
binary_path=/home/sip/eval/binaries-explicit
#REPEAT=( 0 )
#REPEAT=( 0 1 2 )
#REPEAT=( 0 1 )
REPEAT=( 1 )

for bc in ${bc_files}
do
	bitcode=${bc}
	echo ${bc}
	filename=${bc##*/}

	combination_dir=${combination_path}${filename}/*

	for coverage_dir in ${combination_dir}
	do
		coverage_name=${coverage_dir##*/}
		output_dir=${binary_path}/${filename}/${coverage_name}

		#Generate unprotected binary for the baseline
		for coverage in ${coverage_dir}/*
		do
			combination_file=${coverage##*/}

			#repeat protection for random network of protection
			for i in ${REPEAT[@]}
			do
				output_dir=${binary_path}/${filename}/${coverage_name}/${combination_file}/${i}

				if [[ -d ${output_dir} ]]; then
					[[ ! $(grep "Objective" ${output_dir}/solution.txt | awk '{print $3}') -eq $(jq .stats.numberOfProtectedDistinctInstructions ${output_dir}/composition.stats) ]] && echo "bad case"
				fi
			done
		done
	done
done
echo 'Generator is done!'
