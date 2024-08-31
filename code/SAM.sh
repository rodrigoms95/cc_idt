# Cálcula la precipitación media mensual, la serie de máximos anuales para varias duraciones, ajusta una distribución de valores extremos para cada duración, y calcula curvas IDF para diferentes tiempos de retorno.

# Parar al primer error.
set -e

# Tipo de archivo a procesar
p="horas"
#p="dias"
# Todos los datos de la corrida.
#w="Y"
w="N"

# Nombre del archivo a procesar.

# WRF
#name="prec_era5_hist_hist"
#name="prec_hist_comp_estaciones"
#name="prec_era5_hist_hist_days"
#name="prec_mroc_hist_hist"
#name="prec_mroc_h20a_hist"
#name="prec_mroc_hist_hist_days"
#name="prec_mroc_2040_2040"
#name="prec_mroc_2040_2040_coarsen_5"
#name="prec_mroc_h20a_hist_coarsen_10"
#name="WRF_regrid_CHIRPS_days_qmap"
#name="WRF_regrid_ERA5_1985_2014"
#name="WRF_regrid_ERA5_2040_2059"
#name="WRF_regrid_ERA5_1985_2014_qmap"
#name="WRF_regrid_ERA5_2040_2059_qmap"
name="era5-land_total-precipitation"

# CHIRPS
#name="CHIRPS_interp_WRF"
#name="CHIRPS_megalopolis"

# Ubicación del archivo a procesar.
path="../../temp/cc_idt/SAM/"
#input="../../temp/cc_idt/$name.nc"
input="../../Datos/era5-land/$name.nc"
#input="data/$name.nc"
yes | rm -rf $path"temp/"

# Creamos carpetas
mkdir -p $path${name%.*}
mkdir -p $path${name%.*}"/Mapas"
mkdir -p $path${name%.*}"/Mapas/QGZ"
mkdir -p $path${name%.*}"/Mapas/SHP"
mkdir -p $path${name%.*}"/Mapas/TIF"
mkdir -p $path${name%.*}"/Mapas/PDF"

# Archivos a crear
curva_masa=$path"temp/$name.nc"
output_1=$path${name%.*}"/"$name"_tretorno.nc"
output_2=$path${name%.*}"/"$name"_idf_parametros.nc"
output_3=$path${name%.*}"/"$name"_idf_valores.nc"
mean_1=$path"temp/$name""_stats"
mean_2=$path${name%.*}"/"$name"_stats.nc"

echo
echo "Cálculo de curvas IDF"
echo

# Estadísticas mensuales
echo "Calculando estadísticas de precipitación mensual..."
mkdir -p $path"temp/"
cdo -s monsum    $input $mean_1".nc"
cdo -s ymonmin   $mean_1".nc"   $mean_1"_1.nc"
cdo -s ymonmax   $mean_1".nc"   $mean_1"_2.nc"
cdo -s ymonmean  $mean_1".nc"   $mean_1"_3.nc"
cdo -s ymonstd   $mean_1".nc"   $mean_1"_4.nc"
yes | rm $mean_1".nc"
python code/mean.py $mean_2 $w $path"temp/"
yes | rm -r $path"temp/"
echo "Precipitación media mensual calculada."
echo

# Guardamos la lista de años a procesar
echo "Generando lista de años..."
years=( $(cdo -s showyear $input) )
echo "Lista de años generada."
echo

# Suma acumulada, curva masa
echo "Calculando curva masa..."
mkdir -p $path"temp/"
cdo -s timcumsum $input $curva_masa
echo "Curva masa generada."
echo

# Serie de máximos anuales, por año
# Repetimos para cada año
for i in ${years[@]}
do
    echo "Procesando año $i..."
    year_i=$path"temp/$name""_$i.nc"
    # Seleccionamos el año.
    cdo -s selyear,$i $curva_masa $year_i
    echo "Calculando serie de máximos anuales..."
    # Corremos el script que calcula la serie de máximos anuales para el año
    python code/SAM_anual.py $i ${curva_masa%.*} $p
    echo "Año $i procesado."
    echo
done

# Eliminamos la curva masa
echo "Eliminando curva masa..."
rm $curva_masa
echo "Curva masa eliminada."
echo

# Corremos el script para unir todos los datos, calcular los tiempos de retorno y las probabilidades de excedencia
echo "Uniendo todos los datos, calculando tiempos de retorno y probabilidades de excedencia..."
python code/SAM_total.py $output_1 $p $w $path"temp/"
yes | rm -r $path"temp/"
echo "Tiempo de retorno calculado."

# Calculamos las curvas IDF
echo
echo "Calculando curvas IDF..."
python code/IDF.py $output_1 $output_2 $output_3 $p
echo "Curvas IDF calculadas."

echo
echo "Procesamiento terminado."