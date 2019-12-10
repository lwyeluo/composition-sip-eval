for ds in 'simple-cov' 'mibench-cov';
#for ds in 'simple-cov';
do
	for prot in 'OH'; #'SC' 'OH' 'CFI';
	do
		N=4
		(
		for combination in 'NONE' 'FLAs' 'SUB' 'BCF' 'FLAs-BCF' 'FLAs-SUB' 'BCF-FLAs' 'SUB-FLAs' 'SUB-BCF' 'BCF-SUB' 'FLAs-BCF-SUB' 'FLAs-SUB-BCF' 'BCF-FLAs-SUB' 'BCF-SUB-FLAs' 'SUB-FLAs-BCF' 'SUB-BCF-FLAs';
		do
			#generator-prot-obf.sh OH FLAs-SUB-BCF coverage mibench-OH-FLAs-SUB-BCF
			((i=i%N)); ((i++==0)) && wait
			bash generator-prot-obf.sh $prot $combination $ds "labeled-samples-with-exit/$ds-$combination" &
		done
		)
	done
done
