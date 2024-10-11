basedir="/home/rodr/buffalo/SalidasWRF/"
scn="2040_2060"
#scn="2060_2060_100PorcUrbano"
#scn="2080_2089"
#scn="2080_2089_100PorcUrbano"
#subdirs=("" "01" "02" "03")
sd=""
indir="$basedir$scn/zMegalo$sd/Dominio02/variables_2Dimension/"
outdir="/home/rodr/temp/cc_idt/WRF/$scn/"
mkdir -p $outdir
var_or="RAINNC"
var_n="Pcp"

for file in $indir*; do
    if [ "${file: -2}" == "nc" ]; then
        #cdo -chname,$var_or,$var_n -selname,$var_or $file $outdir${file##*/}
        cdo select,name=$var_or $file $outdir"a.nc"
    fi
done