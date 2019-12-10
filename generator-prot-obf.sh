#!/usr/bin/env bash
set -euo pipefail
source env.sh

# Parse arguments
if [ $# -lt 4 ]; then
  echo "usage: generator-prot-obfus.sh PROTECTION-OPTIONS OBFUSCATION-OPTIONS DATASET OUTDIRECTORY"
  echo "  PROTECTION OPTIONS:"
  echo "    CFI, OH, SC: protections, no combination yet"
  echo "  OBFUSCATION OPTIONS:"
  echo "    SUB, CFF, BCF: obfuscations, combine with dash, e.g. SUB-CFF"
  echo "  DATASET:"
  echo "    path to a dataset of BC files"
  echo "  OUTDIRECTORY:"
  echo "    out directory path"
  exit 1
fi


Protection=$1
Obfuscation=$2
Dataset=$3
OutDir=$4

echo $Protection
echo $Obfuscation
echo $Dataset
echo $OutDir


USR_LIB_DIR=/usr/local/lib
INPUT_DEP_PATH=${USR_LIB_DIR}
DG_PATH=${USR_LIB_DIR}
OH_LIB=${OH_PATH}/$BUILD_DIR
bc_files=${Dataset}/*.bc
#bc_files=$(ls -r ${Dataset}/*.bc)

combination_path=/home/sip/eval/combination/
binary_path=${OutDir}
config_path=/home/sip/eval/lib-config/
link_libraries=/home/sip/eval/link-libraries/
args_path=/home/sip/eval/cmdline-args
blockfrequency=/home/sip/eval/blockfrequency
STRATEGIES=('ilp' ) #either of 'ilp' or 'random' 

mkdir -p ${binary_path}

for bc in ${bc_files}
do
	bitcode=${bc}
	echo "Starting with ${bc}"
	filename=${bc##*/}
	pathless=$(basename -- "$bc")
	outfilename=${pathless%.*}
	plainoutfile="${outfilename}-${Obfuscation}.bc"
	outfilename="${outfilename}-${Protection}-${Obfuscation}.bc"
	outfilename=${outfilename/.x/}
	
        if [ ! -f ${binary_path}/$plainoutfile ]; then
	  echo "Create one unprotected instance"
	  cp $bitcode ${binary_path}/$plainoutfile
	  if [[ $Obfuscation != "NONE"* ]]; then
        	echo 'Obfuscating...'
        	bash obfuscate.sh -o ${Obfuscation} -a ${binary_path}/${plainoutfile} ${binary_path}/${plainoutfile}
        	if [ $? -ne 0 ]; then
            	  echo Failed to Obfuscate baseline with ${Obfuscation} setting
            	  exit 1
                fi
          fi
        fi



	echo $outfilename
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
	#for coverage_dir in ${combination_dir}
	#do
            #coverage_name=${coverage_dir##*/}
	    #we only do this on fully protected binaries
	    #if [ ${coverage_name} -ne 100 ]; then
		#echo skip coverage files other than 100 
		#continue
	    #fi
	    #for coverage in ${coverage_dir}/*
	    #do
		#combination_file=${coverage##*/}
		output_dir=${binary_path}

		if [ -f ${output_dir}/${outfilename} ]; then
		   echo Found protected file ${output_dir}/${outfilename}
		   continue
		else 
		   echo Did not find ${output_dir}/${outfilename}
		fi

		combination_file=${combination_path}${filename}/100/0
		if [ ! -f ${combination_file} ]; then
		   echo Did not find 100 combination file ${combination_file}
	           exit 1
	        fi	   
		
		#echo "Handling combination file $coverage"
		#echo "Protect $bc with function combination file $coverage"

                echo 'Transform Protections'
                cmd="${OPT}"
                # Input & Output
                cmd="${cmd} ${bc}"
                cmd="${cmd} -o ${output_dir}/${outfilename}"
                # All needed libs
                cmd="${cmd} -load ${INPUT_DEP_PATH}/libInputDependency.so"
                cmd="${cmd} -load ${DG_PATH}/libLLVMdg.so"
                cmd="${cmd} -load ${USR_LIB_DIR}/libUtils.so"
                cmd="${cmd} -load ${USR_LIB_DIR}/libCompositionFramework.so"
                cmd="${cmd} -load ${INPUT_DEP_PATH}/libTransforms.so"
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
		if [[ $Protection == "SC"* ]]; then
                  # SC flags
                  cmd="${cmd} -load /home/sip/self-checksumming/build/libSCPass.so"
                  cmd="${cmd} -use-other-functions"
                  cmd="${cmd} -connectivity=4"
                  #cmd="${cmd} -dump-checkers-network=${output_dir}/network_file"
                  #cmd="${cmd} -dump-sc-stat=${output_dir}/sc.stats"
                  cmd="${cmd} -filter-file=${combination_file}"
		elif [[ $Protection == "OH"* ]]; then
                  # OH flags
                  cmd="${cmd} -load ${OH_LIB}/liboblivious-hashing.so"
                  cmd="${cmd} -num-hash 1"
                  cmd="${cmd} -dump-oh-stat=${output_dir}/oh.stats"
                  cmd="${cmd} -exclude-main-unreachables"
                  cmd="${cmd} -main-reach-cached"
                  #cmd="${cmd} -protect-data-dep-loops"
		elif [[ $Protection == "CFI"* ]]; then
                  # CFI flags
                  cmd="${cmd} -load ${CFI_PATH}/$BUILD_DIR/libControlFlowIntegrity.so"
                  cmd="${cmd} -cfi-template ${CFI_PATH}/stack_analysis/StackAnalysis.c"
                  cmd="${cmd} -cfi-outputdir ${output_dir}"
		fi
                # CF flags
                cmd="${cmd} -cf-strategy=${STRATEGIES[0]}"
                cmd="${cmd} -cf-dump-graphs"
                cmd="${cmd} -cf-stats=${output_dir}/composition.stats"
		#cmd="${cmd} -cf-ilp-prob=${output_dir}/problem.txt"
		#cmd="${cmd} -cf-ilp-sol=${output_dir}/solution.txt"
		#cmd="${cmd} -cf-ilp-sol-readable=${output_dir}/solution_readable.txt"
                #cmd="${cmd} -cf-patchinfo=${output_dir}/cf-patchinfo.json"
#                cmd="${cmd} -cf-ilp-implicit-bound=1401"
#                cmd="${cmd} -cf-ilp-explicit-bound=1284"
                #cmd="${cmd} -cf-ilp-overhead-bound=353"
                #cmd="${cmd} -cf-ilp-connectivity-bound=4"
                #cmd="${cmd} -cf-ilp-blockconnectivity-bound=6"
                cmd="${cmd} -cf-ilp-obj=manifest"
                # PASS ORDER
		if [[ $Protection == "SC"* ]]; then
                  cmd="${cmd} -sc"
		elif [[ $Protection == "CFI"* ]]; then
                  cmd="${cmd} -control-flow-integrity"
		elif [[ $Protection == "OH"* ]]; then
                  cmd="${cmd} -oh-insert"
                  cmd="${cmd} -short-range-oh"
		fi
                cmd="${cmd} -composition-framework"
	        cmd="${cmd} -time-passes"
                # End of command

                echo "EAT ME:\n$cmd"
                ${cmd} |& tee "${output_dir}/transform.console"

                echo ${output_dir}
                if [ $? -eq 0 ]; then
                    echo 'OK Transform'
                else
                    echo !!
                    echo 'FAIL Transform'
                    exit
                fi
		LIBS="${output_dir}/${outfilename}"
		if [[ $Protection == "OH"* ]]; then
                  LIBS="${LIBS} protection-libs/ohlib.bc" 
                elif [[ $Protection == "CFI"* ]]; then
		  echo 'Link CFIlib.bc'
                  LIBS="${LIBS} protection-libs/cfilib.bc" 
                elif [[ $Protection == "SC"* ]]; then
                  LIBS="${LIBS} protection-libs/sclib.bc" 
                fi
               
	        echo ${LIBS}
		#LINK protection libs
                llvm-link-7 ${LIBS} -o ${output_dir}/${outfilename}

                if [ $? -eq 0 ]; then
                    echo 'OK Link'
                else
                    echo !!
                    echo 'FAIL Link'
                    exit
                fi

                CUSTOM_PASSES_LIB=/home/sip/offtree-o-llvm/passes/build/lib

		#inline1 protection function calls
		opt-7 -load $CUSTOM_PASSES_LIB/libCIFPass.so ${output_dir}/${outfilename} -o ${output_dir}/${outfilename} -cif
                if [ $? -ne 0 ]; then
                  echo Failed inline step 1
                  exit 1
                fi
                
		opt-7 -load $CUSTOM_PASSES_LIB/libDIFPass.so ${output_dir}/${outfilename} -o ${output_dir}/${outfilename} -dif
                if [ $? -ne 0 ]; then
                  echo Failed inline step 2
                  exit 1
                fi

                #Obfuscate programs
                if [[ $Obfuscation != "NONE"* ]]; then
		  echo 'Obfuscating...'
		  bash obfuscate.sh -o ${Obfuscation} -a ${output_dir}/${outfilename} ${output_dir}/${outfilename}
		  if [ $? -ne 0 ]; then
		    echo Failed to Obfuscate with ${Obfuscation} setting
		    exit 1
	          fi
		fi

		                
                echo "Done with '${outfilename}'"
	        #clean unneccerary files
	        find ${output_dir} -type f ! -name '*.bc' -delete 

#	done
#	done
echo "Finished $bitcode"
done
echo 'Generator is done!'
