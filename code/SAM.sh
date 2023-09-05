# Nombre del archivo a procesar.
name="prec_miro_hist_hist"
# Ubicación del archivo a procesar.
input="data/$name.nc"
# Guardamos la lista de años a procesar.
years=( $(cdo showyear $input) )
# Suma acumulada, curva masa.
curva_masa="temp/$name.nc"
cdo timcumsum $input $curva_masa
# Seleccionamos un año.
for i in years
do
    year_i="temp/$name""_${years[1]}.nc"
    cdo selyear,${years[1]} $curva_masa $year_i
done
# Número de pasos.
for i in $(seq 1 24)
do
    # Recorremos la cantidad de pasos.
    cdo shifttime,$i"hour" $year_i "${year_i%.*}""_$i.nc"
    cdo seltimestep,2/8760 $year_i "${year_i%.*}""_s.nc"
    cdo seltimestep,1/8759 "${year_i%.*}""_$i.nc" "${year_i%.*}""_$i""_s.nc"
    # Restamos el recorrido del original.
    cdo sub $year_i "${year_i%.*}""_$i.nc" "${year_i%.*}""_$i""_ss.nc"
    # Obtenemos la intensidad.
    cdo divc,$i "${year_i%.*}""_$i.nc" "${year_i%.*}""_$i.nc"
    # Obtenemos el máximo.
    cdo timmax "${year_i%.*}""_$i.nc" "${year_i%.*}""_$i.nc"
done


for i in $(seq 1)
do
    # Recorremos la cantidad de pasos.
    cdo shifttime,$i"hour" $year_i "${year_i%.*}""_$i.nc"
done