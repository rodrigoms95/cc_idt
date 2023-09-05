# Nombre del archivo a procesar.
name="prec_miro_hist_hist"

# Ubicación del archivo a procesar.
input="data/$name.nc"
output_1="results/$name""_tretorno.nc"
output_2="results/$name""_idf_gumbel.nc"
output_3="results/$name""_idf_valores.nc"

echo
echo "Cálculo de curvas IDF"

# Guardamos la lista de años a procesar.
echo
echo "Generando lista de años..."
years=( $(cdo -s showyear $input) )
echo "Lista de años generada."
echo

# Suma acumulada, curva masa.
curva_masa="temp/$name.nc"
echo "Calculando curva masa..."
cdo -s timcumsum $input $curva_masa
echo "Curva masa generada."
echo

# Repetimos para cada año.
for i in ${years[@]}
do
    echo "Procesando año $i..."
    year_i="temp/$name""_$i.nc"
    # Seleccionamos el año.
    cdo -s selyear,$i $curva_masa $year_i
    echo "Calculando serie de máximos anuales..."
    # Corremos el script que calcula la serie de máximos anuales para el año.
    python code/SAM_anual.py $i
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
python code/SAM_total.py $output_1
rm "temp/*"
echo "Tiempo de retorno calculado."

echo
echo "Calculando curvas IDF..."
python code/IDF.py $output_1 $output_2 $output_3
echo "Curvas IDF calculadas."

echo
echo "Procesamiento terminado."