path=$1
rm -r seg-datasets-mibench
for combination in '-NONE' '-FLAs' '-SUB' '-BCF' '-FLAs-BCF' '-BCF-FLAs' '-FLAs-SUB' '-SUB-FLAs' '-BCF-SUB' '-SUB-BCF' '-FLAs-BCF-SUB' '-FLAs-SUB-BCF' '-BCF-FLAs-SUB' '-BCF-SUB-FLAs' '-SUB-FLAs-BCF' '-SUB-BCF-FLAs'; do
  comb_dir="${combination/FLAs/FLA}"
  comb_dir="${combination/-NONE/}"
  #mkdir -p seg-datasets-simple/sbb$comb_dir && cp $path/simple-cov$combination/*.bc seg-datasets-simple/sbb$comb_dir/
  mkdir -p seg-datasets-mibench/sbb$comb_dir && cp $path/mibench-cov$combination/*.bc seg-datasets-mibench/sbb$comb_dir/
 # mkdir -p seg-datasets-combined/sbb$comb_dir && cp $path/mibench-cov$combination/*.bc $path/simple-cov$combination/*.bc seg-datasets-combined/sbb$comb_dir/
done
#tar -zcvf seg-datasets-simple.tar.gz seg-datasets-simple
tar -zcvf seg-datasets-mibench.tar.gz seg-datasets-mibench
#tar -zcvf seg-datasets-combined.tar.gz seg-datasets-combined
