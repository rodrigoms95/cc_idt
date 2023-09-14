# Cálcula la precipitación media mensual, la serie de máximos anuales para varias duraciones, ajusta una distribución de valores extremos para cada duración, y calcula curvas IDF para diferentes tiempos de retorno.

# Parar al primer error.
set -e
yes | rm -f temp/SAM/*

# Tipo de archivo a procesar
#p="horas"
p="dias"

# Nombre del archivo a procesar.

# WRF
#t="WRF"
#name="prec_hist_hist"
#name="prec_hist_comp_estaciones"
#name="prec_hist_comp_CHIRPS"

# CHIRPS
t="CHIRPS"
name="CHIRPS_comp"
#name="CHIRPS_megalopolis"

# Ubicación del archivo a procesar.
input="temp/$name.nc"
#input="data/$name.nc"

mkdir -p "results/"${name%.*}
curva_masa="temp/SAM/$name.nc"
output_1="results/"${name%.*}"/$name""_tretorno.nc"
output_2="results/"${name%.*}"/$name""_idf_gumbel.nc"
output_3="results/"${name%.*}"/$name""_idf_valores.nc"
mean_1="temp/SAM/$name""_stats"
mean_2="results/"${name%.*}"/$name""_stats.nc"

echo
echo "Cálculo de curvas IDF"
echo

echo "Calculando estadísticas de precipitación mensual..."
cdo -s monsum    $input $mean_1".nc"
cdo -s ymonmin   $mean_1".nc"   $mean_1"_1.nc"
cdo -s ymonmax   $mean_1".nc"   $mean_1"_2.nc"
cdo -s ymonmean  $mean_1".nc"   $mean_1"_3.nc"
cdo -s ymonstd   $mean_1".nc"   $mean_1"_4.nc"
yes | rm $mean_1".nc"
python code/mean.py $mean_2 $t
yes | rm temp/SAM/*
echo "Precipitación media mensual calculada."
echo

# Guardamos la lista de años a procesar.
echo "Generando lista de años..."
years=( $(cdo -s showyear $input) )
echo "Lista de años generada."
echo

# Suma acumulada, curva masa.
echo "Calculando curva masa..."
cdo -s timcumsum $input $curva_masa
echo "Curva masa generada."
echo

# Repetimos para cada año.
for i in ${years[@]}
do
    echo "Procesando año $i..."
    year_i="temp/SAM/$name""_$i.nc"
    # Seleccionamos el año.
    cdo -s selyear,$i $curva_masa $year_i
    echo "Calculando serie de máximos anuales..."
    # Corremos el script que calcula la serie de máximos anuales para el año.
    python code/SAM_anual.py $i ${curva_masa%.*} $t $p
    echo "Año $i procesado."
    echo
done

# Eliminamos la curva masa.
echo "Eliminando curva masa..."
rm $curva_masa
echo "Curva masa eliminada."
echo

# Corremos el script para unir todos los datos, calcular los tiempos de retorno y las probabilidades de excedencia.
echo "Uniendo todos los datos, calculando tiempos de retorno y probabilidades de excedencia..."
python code/SAM_total.py $output_1 $t $p
yes | rm temp/SAM/*
echo "Tiempo de retorno calculado."

echo
echo "Calculando curvas IDF..."
python code/IDF.py $output_1 $output_2 $output_3
echo "Curvas IDF calculadas."

echo
echo "Procesamiento terminado."