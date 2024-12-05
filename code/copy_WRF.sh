# Parar al primer error
set -e

printf "\nCalculando precipitaciónn\n"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Escenario a calcular
#for scn in "2040_2060" "2080_2089" "2040_2060_100PorcUrbano" "2080_2089_100PorcUrbano"; do
for scn in "2080_2089" "2040_2060_100PorcUrbano" "2080_2089_100PorcUrbano"; do
    dr=/home/rodr/buffalo/rodr/WRF/$scn/$scn
    printf "\nCalculando generación fotovoltaica para $scn\n"
    # Copiamos los archivos
    printf "Copiando archivos\n"
    mkdir -p $dr
    for zmegalo in /home/rodr/buffalo/SalidasWRF/$scn/*/ ; do
        dd=$zmegalo/Dominio02/variables_2Dimension
        cd $dd
        for j in zSalidaIRainWRF_*.nc; do
            printf "$j                  \r"
            if [ ! -d "/home/rodr/buffalo/rodr/WRF/$scn/Rain/" ] && [ ! -f "$dr/$j" ]; then
            cp $dd/$j $dr/$j
            fi
       done
    done
    cd
    printf "\n\n"

    # Sacamos las variables de interés
    python $SCRIPT_DIR/WRF_extract.py $scn
    # Unimos datos temporales
    python $SCRIPT_DIR/merge_time.py $scn
    # Interpolamos
    python $SCRIPT_DIR/resolucion.py $scn
    echo
    # Calculamos cuantiles
    python $SCRIPT_DIR/CDF_calc.py $scn
    # Hacemos corrección de cuantiles
    python $SCRIPT_DIR/quantile_calc.py $scn

done

printf "\nPrecipitación calculada\n\n"