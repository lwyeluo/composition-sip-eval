FLA='FLAs'
SUB='SUB'
BCF='BCF'

PERC=30
function edit {
	echo switched to $1
	sed -i "s/const int defaultObfRate = 30/const int defaultObfRate = $1/g" /home/sip/offtree-o-llvm/passes/obfs/BogusControlFlow.cpp
	sed -i "s/const int defaultObfRate = 40/const int defaultObfRate = $1/g" /home/sip/offtree-o-llvm/passes/obfs/BogusControlFlow.cpp
	sed -i "s/const int defaultObfRate = 100/const int defaultObfRate = $1/g" /home/sip/offtree-o-llvm/passes/obfs/BogusControlFlow.cpp
	#edit bogus control flow $1
	#build obfuscation passes
	make -C /home/sip/offtree-o-llvm/passes/build
	PERC=$1
}
function generate {

  for ds in 'mibench-cov';
  #for ds in 'simple-cov';
  do
	for prot in 'OH' 'CFI' 'SC' ;
#
	do
		N=4
		(
		for combination in "$@";
		do
			#generator-prot-obf.sh OH FLAs-SUB-BCF coverage mibench-OH-FLAs-SUB-BCF
			#((i=i%N)); ((i++==0)) && wait
			echo generator-prot-obf.sh $prot $combination $ds "labeled-samples$PERC/$ds-$combination" 
			#bash generator-prot-obf.sh $prot $combination $ds "labeled-samples-$PERC/$ds-$combination" &
		done
		)
	done
  done

}
generate "NONE"
exit 1
edit 30
generate "$BCF" "$FLA-$BCF" "$BCF-$FLA" "$SUB-$BCF" "$BCF-$SUB" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$BCF-$FLA-$SUB" "$BCF-$SUB-$FLA" "$SUB-$FLA-$BCF" "$SUB-$BCF-$FLA" "$SUB" "$FLA" "$SUB-$FLA" "$FLA-$SUB" 'BCF-FLAs2' 'BCF-FLAs2-SUB2' 'BCF-SUB2-FLAs2' 
#edit bogus contrl flow to 40
edit 40
generate 'BCF' 'BCF-FLAs' 'BCF-FLAs-SUB' 'BCF-SUB' 'BCF-SUB-FLAs' 'FLAs-BCF' 'FLAs-BCF-SUB' 'FLAS-SUB-BCF' 'SUB-BCF' 'SUB-BCF-FLAs' 'SUB-FLAs-BCF'
edit 100
generate 'BCF' 'BCF-FLAs' 'BCF-FLAs-SUB' 'BCF-SUB' 'BCF-SUB-FLAs' 'FLAs-BCF' 'FLAs-BCF-SUB' 'FLAS-SUB-BCF' 'SUB-BCF' 'SUB-BCF-FLAs' 'SUB-FLAs-BCF'

