#!/usr/bin/env bash
set -euo pipefail
source env.sh

objective='manifest'






USR_LIB_DIR=/usr/local/lib
INPUT_DEP_PATH=${USR_LIB_DIR}
DG_PATH=${USR_LIB_DIR}
OH_LIB=${OH_PATH}/$BUILD_DIR
echo $OH_LIB
echo $USR_LIB_DIR
bc_files=/home/sip/eval/coverage/*.bc
combination_path=/home/sip/eval/combination/
binary_path="/home/sip/eval/binaries-acsac-${objective}"
config_path=/home/sip/eval/lib-config/
link_libraries=/home/sip/eval/link-libraries/
args_path=/home/sip/eval/cmdline-args
constraints_path=/home/sip/eval/constraints
blockfrequency=/home/sip/eval/blockfrequency
#REPEAT=( 0 )
#REPEAT=( 0 1 2 )
#REPEAT=( 0 1 )
REPEAT=( 0 )
STRATEGIES=('ilp' ) #either of 'ilp' or 'random' 

mkdir -p binaries

for bc in ${bc_files}
do
	bitcode=${bc}
	echo "Starting with ${bc}"
	filename=${bc##*/}
	libconfig=${config_path}${filename}
	cmd_args=""
	if [ -f "${args_path}/${filename}" ]; then
		cmd_args="${args_path}/${filename}"
	fi
	combination_dir=${combination_path}${filename}/*

	libraries=""
	if [ -f "${link_libraries}${filename}" ]; then
		libraries=$(<${link_libraries}${filename})
	fi

	echo "Libraries to link with $libraries"
	for coverage_dir in ${combination_dir}
	do
	        coverage_name=${coverage_dir##*/}	
		output_dir=${binary_path}/${filename}/${coverage_name}
		mkdir -p ${output_dir}
		#Generate unprotected binary for the baseline

		if [ ${coverage_name} -eq 0 ]; then
			#avoid regenerating if desired

			if [ $# -eq 1 ]; then
			    CONT=0
                {
                    flock -x 200

                    if [ -d "$output_dir/0/1" ]; then
                        echo "Skipping $output_dir"
                        CONT=1
                    else
                        mkdir -p ${output_dir}/0/1
                    fi
                } 200>/var/lock/cfgenerator
                if [ "$CONT" -eq "1" ]; then
                    continue
                fi
            else
                mkdir -p ${output_dir}/0/1
			fi
			echo "Handling baseline"
			${LLC} ${bitcode} -o ${output_dir}/out.s
			#make a dummy combination=0 and a dummy attempt=1 just for the sake of complying with the directory structure
			g++ -no-pie -fPIC -std=c++0x -g -rdynamic ${output_dir}/out.s -o ${output_dir}/0/1/${filename} ${libraries}
			rm ${output_dir}/out.s
			continue
		fi
		for coverage in ${coverage_dir}/*
		do
			combination_file=${coverage##*/}
                        constraints_file=$constraints_path/$filename/$coverage_name/$combination_file 
			output_dir=${binary_path}/${filename}/${coverage_name}/${combination_file}
                        echo $constraints_file
                        constraints_args=""
                        if [ -f "${constraints_file}" ]; then
                          constraints_args=$(<${constraints_file})
                        fi  
			echo $output_dir
                        echo $constraints_args


			echo "Handling combination file $coverage"
			echo "Protect $bc with function combination file $coverage"
			#repeat protection for random network of protection
			for i in ${REPEAT[@]}
			do
			    output_dir=${binary_path}/${filename}/${coverage_name}/${combination_file}/${i}
				echo "Protect here $i"

				#avoid regenerating if desired
                if [ $# -eq 1 ]; then
                    CONT=0
                    {
                        flock -x 200

                        if [ -d "$output_dir" ]; then
                            echo "Skipping $output_dir"
                            CONT=1
                        else
                            mkdir -p ${output_dir}
                        fi
                    } 200>/var/lock/cfgenerator
                    if [ "$CONT" -eq "1" ]; then
                        continue
                    fi
                else
                   mkdir -p ${output_dir}
                fi

                echo 'Remove old files'
                rm patch_guide ||:
                rm guide.txt ||:
                rm protected ||:
                rm out.bc ||:
                rm out ||:

                echo 'Transform Protections'
                cmd="${OPT}"
                # Input & Output
                cmd="${cmd} ${bc}"
                cmd="${cmd} -o ${output_dir}/out.bc"
                # All needed libs
                cmd="${cmd} -load ${INPUT_DEP_PATH}/libInputDependency.so"
                cmd="${cmd} -load ${DG_PATH}/libLLVMdg.so"
                cmd="${cmd} -load ${USR_LIB_DIR}/libUtils.so"
                cmd="${cmd} -load ${USR_LIB_DIR}/libCompositionFramework.so"
                cmd="${cmd} -load ${USR_LIB_DIR}/libSCPass.so"
                cmd="${cmd} -load ${OH_LIB}/liboblivious-hashing.so"
#                cmd="${cmd} -load ${INPUT_DEP_PATH}/libTransforms.so"
                #cmd="${cmd} -load ${CFI_PATH}/$BUILD_DIR/libControlFlowIntegrity.so"
#                cmd="${cmd} -load ${CMM_PATH}/$BUILD_DIR/libCodeMobilityMock.so"
                # General flags
                cmd="${cmd} -strip-debug"
                cmd="${cmd} -unreachableblockelim"
                cmd="${cmd} -globaldce"
                cmd="${cmd} -use-cache"
                cmd="${cmd} -goto-unsafe"
                cmd="${cmd} -block-freq"
                cmd="${cmd} -pgo-instr-use"
                cmd="${cmd} -pgo-test-profile-file=${blockfrequency}/${filename}/${filename}.prof"
                cmd="${cmd} -profile-sample-accurate"
		cmd="${cmd} -debug-pass=Structure"
                # SC flags
                cmd="${cmd} -use-other-functions"
                cmd="${cmd} -extracted-only"
                cmd="${cmd} -connectivity=1"
                cmd="${cmd} -dump-checkers-network=${output_dir}/network_file"
                cmd="${cmd} -dump-sc-stat=${output_dir}/sc.stats"
                cmd="${cmd} -filter-file=${coverage}"
                # OH flags
                cmd="${cmd} -protect-data-dep-loops"
                cmd="${cmd} -num-hash 1"
                cmd="${cmd} -dump-oh-stat=${output_dir}/oh.stats"
                cmd="${cmd} -exclude-main-unreachables"
                cmd="${cmd} -main-reach-cached"
                # CFI flags
                #cmd="${cmd} -cfi-template ${CFI_PATH}/stack_analysis/StackAnalysis.c"
                #cmd="${cmd} -cfi-outputdir ${output_dir}"
                # CF flags
                cmd="${cmd} -cf-strategy=${STRATEGIES[0]}"
                cmd="${cmd} -cf-dump-graphs"
                cmd="${cmd} -cf-stats=${output_dir}/composition.stats"
		cmd="${cmd} -cf-ilp-prob=${output_dir}/problem.txt"
		cmd="${cmd} -cf-ilp-sol=${output_dir}/solution.txt"
		cmd="${cmd} -cf-ilp-sol-readable=${output_dir}/solution_readable.txt"
                cmd="${cmd} -cf-patchinfo=${output_dir}/cf-patchinfo.json"
#                cmd="${cmd} -cf-ilp-implicit-bound=1401"
#                cmd="${cmd} -cf-ilp-explicit-bound=1284"
                #cmd="${cmd} -cf-ilp-overhead-bound=353"
                #cmd="${cmd} -cf-ilp-connectivity-bound=4"
                #cmd="${cmd} -cf-ilp-blockconnectivity-bound=6"
          #      cmd="${cmd} ${constraints_args}"
                cmd="${cmd} -cf-ilp-obj=${objective}"
                # PASS ORDER
                cmd="${cmd} -sc"
                #cmd="${cmd} -control-flow-integrity"
#                cmd="${cmd} -code-mobility"
                cmd="${cmd} -oh-insert"
                cmd="${cmd} -short-range-oh"
                cmd="${cmd} -composition-framework"
	        cmd="${cmd} -time-passes"
                # End of command
#		gdb --args ${cmd}
#		heaptrack ${cmd}
#		perf record --call-graph dwarf ${cmd}
                ${cmd} |& tee "${output_dir}/transform.console"
                echo "EAT ME:\n$cmd"

                echo ${output_dir}
                if [ $? -eq 0 ]; then
                    echo 'OK Transform'
                else
                    echo !!
                    echo 'FAIL Transform'
                    exit
                fi

                # compiling external libraries to bitcodes
                LIB_FILES=()
                g++ -no-pie -fPIC ${OH_PATH}/assertions/response_broken.cpp -c -o "${output_dir}/oh_rtlib.o"
                LIB_FILES+=( "${output_dir}/oh_rtlib.o" )

                #gcc -no-pie -fPIC -g -rdynamic -c "${output_dir}/NewStackAnalysis.c" -o "${output_dir}/cfi_rtlib.o"
                #LIB_FILES+=( "${output_dir}/cfi_rtlib.o" )

                gcc -no-pie -fPIC -g -rdynamic -c "${SC_PATH}/rtlib.c" -o "${output_dir}/sc_rtlib.o"
                LIB_FILES+=( "${output_dir}/sc_rtlib.o" )

                g++ -no-pie -fPIC -std=c++11 -g -rdynamic -shared -Wl,-soname,librtlib.so \
                    -o "${output_dir}/librtlib.so" ${LIB_FILES[@]} -lssl -lcrypto

                if [ $? -eq 0 ]; then
                    echo 'OK Link'
                else
                    echo !!
                    echo 'FAIL Link'
                    exit
                fi


                echo 'Post patching binary after hash calls'
                ${LLC} ${output_dir}/out.bc -o ${output_dir}/out.s
                if [ $? -eq 0 ]; then
                    echo 'OK Transform'
                else
                    echo 'FAIL llc'
                    exit
                fi

                gcc -g -no-pie -fPIC -rdynamic ${output_dir}/out.s -o ${output_dir}/${filename} -L ${output_dir} -lrtlib ${libraries}
                if [ $? -eq 0 ]; then
                    echo 'OK gcc final binary'
                else
                    echo "$link_libraries$filename"
                    echo "$libraries"
                    echo 'FAIL gcc final binary'
                    exit
                fi

                cp "${output_dir}/${filename}" "${output_dir}/${filename}_backup"
                #remove temp files
                #rm ${output_dir}/out.s ||:

                echo 'Starting patcher, this will wait for input when nothing is provided'
	        echo python "${CF_PATH}/hook/patcher.py" "${output_dir}/${filename}" -m "${output_dir}/cf-patchinfo.json" -p "patchers.json" -o "${output_dir}" --args-path "${cmd_args}" &> "${output_dir}/patcher.console"
                /usr/bin/time -f "totaltime: %e %U %S" -o "${output_dir}/patchTime.txt" python "${CF_PATH}/hook/patcher.py" "${output_dir}/${filename}" -m "${output_dir}/cf-patchinfo.json" -p "patchers.json" -o "${output_dir}" --args-path "${cmd_args}" &> "${output_dir}/patcher.console"

                if [ $? -eq 0 ]; then
                    echo 'OK GDB Patch'
                    if [ -f ${output_dir}/${filename}"tmp" ]; then
                        mv ${output_dir}/${filename}"tmp" ${output_dir}/${filename}
                    fi
                    chmod +x ${output_dir}/${filename}
		else 
		    echo 'Patcher Failed'
                fi
			done
		done
	done
echo "Finished $bitcode"
done
echo 'Generator is done!'
