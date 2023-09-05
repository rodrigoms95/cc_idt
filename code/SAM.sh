# Nombre del archivo a procesar.
name="prec_miro_hist_hist"

# Ubicación del archivo a procesar.
input="data/$name.nc"
output="results/$name""_tretorno.nc"

echo
echo "Cálculo del tiempo de retorno"

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
echo "Uniendo todos los datos, calculando tiempos de retorno y probabilidades de excedencia"
python code/SAM_total.py $output
#rm "temp/*"
echo
echo "Tiempo de retorno calculado."