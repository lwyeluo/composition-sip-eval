FLA='FLAs2'
SUB='SUB2'
BCF='BCF'
for ds in 'simple-cov' 'mibench-cov';
#for ds in 'simple-cov';
do
	for prot in 'SC' 'OH' 'CFI';
	do
		N=4
		(
		for combination in "NONE" "$FLA" "$SUB" "$BCF" "$FLA-$BCF" "$FLA-$SUB" "$BCF-$FLA" "$SUB-$FLA" "$SUB-$BCF" "$BCF-$SUB" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$BCF-$FLA-$SUB" "$BCF-$SUB-$FLA" "$SUB-$FLA-$BCF" "$SUB-$BCF-$FLA";
		do
			#generator-prot-obf.sh OH FLAs-SUB-BCF coverage mibench-OH-FLAs-SUB-BCF
			((i=i%N)); ((i++==0)) && wait
			bash generator-prot-obf.sh $prot $combination $ds "labeled-samples/$ds-$combination" &
		done
		)
	done
done
