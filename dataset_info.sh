#!/usr/bin/env bash
set -xeuo pipefail

CLANG=clang
OPT=opt
LLC=llc
LLVM_LINK=llvm-link
INPUT_DEP_PATH=/usr/local/lib/

SC_PATH=/home/sip/self-checksumming
CF_PATH=/home/sip/composition-framework
CFI_PATH=/home/sip/sip-control-flow-integrity
CMM_PATH=/home/sip/code-mobility-mock
OH_PATH=/home/sip/sip-oblivious-hashing

USR_LIB_DIR=/usr/local/lib
INPUT_DEP_PATH=${USR_LIB_DIR}
DG_PATH=${USR_LIB_DIR}
OH_LIB=$OH_PATH/cmake-build-debug

FILES=/home/sip/eval/dataset/*.bc
DATAPATH=/home/sip/eval/dataset_info/
configs=/home/sip/eval/lib-config


for f in $FILES
do
	bitcode=$f
	echo $f
	filename=${f##*/}
	libconfig=$configs/$filename
	output_dir=$DATAPATH/$filename
	mkdir -p $output_dir
    cd $output_dir

	cmd="${OPT}"
	# Input & Output
	cmd="${cmd} ${bitcode}"
	cmd="${cmd} -o ${output_dir}/out.bc"
	# All needed libs
	cmd="${cmd} -load ${INPUT_DEP_PATH}/libInputDependency.so"
	cmd="${cmd} -load ${DG_PATH}/libLLVMdg.so"
	cmd="${cmd} -load ${USR_LIB_DIR}/libUtils.so"
	cmd="${cmd} -load ${USR_LIB_DIR}/libCompositionFramework.so "
	cmd="${cmd} -load ${USR_LIB_DIR}/libSCPass.so"
	cmd="${cmd} -load ${OH_LIB}/liboblivious-hashing.so"
	cmd="${cmd} -load ${INPUT_DEP_PATH}/libTransforms.so"
	cmd="${cmd} -load ${CFI_PATH}/cmake-build-debug/libControlFlowIntegrity.so"
	cmd="${cmd} -load ${CMM_PATH}/cmake-build-debug/libCodeMobilityMock.so"
	# General flags
	cmd="${cmd} -strip-debug"
	cmd="${cmd} -unreachableblockelim"
	cmd="${cmd} -globaldce"
	cmd="${cmd} -use-cache"
	cmd="${cmd} -goto-unsafe"
	# Input-Dep flags
	cmd="${cmd} -dependency-stats"
	# SC flags
	cmd="${cmd} -extracted-only"
	cmd="${cmd} -use-other-functions"
	cmd="${cmd} -connectivity=1"
	cmd="${cmd} -dump-checkers-network=${output_dir}/network_file"
	cmd="${cmd} -dump-sc-stat=${output_dir}/sc.stats"
	# OH flags
	cmd="${cmd} -protect-data-dep-loops"
	cmd="${cmd} -num-hash 1"
	cmd="${cmd} -dump-oh-stat=${output_dir}/oh.stats"
	# CFI flags
	cmd="${cmd} -cfi-template ${CFI_PATH}/stack_analysis/StackAnalysis.c"
	# CF flags
	cmd="${cmd} -cf-strategy=random"
	cmd="${cmd} -cf-stats=${output_dir}/composition.stats"
	cmd="${cmd} -cf-patchinfo=${output_dir}/cf-patchinfo.json"
	# PASS ORDER
	cmd="${cmd} -sc"
	cmd="${cmd} -control-flow-integrity"
	cmd="${cmd} -code-mobility"
	cmd="${cmd} -oh-insert"
	cmd="${cmd} -short-range-oh"
	cmd="${cmd} -constraint-protection"
	# End of command
	${cmd} |& tee "${output_dir}/transform.console"

	cd -
	if [ $? -eq 0 ]; then
		echo 'OK module size'
	else
		echo 'FAIL module size'
		exit
	fi
done

