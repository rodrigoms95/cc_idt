# Interpola la información de chirps para comparar con la de WRF.

# Parar al primer error.
set -e
yes | rm -f temp/SAM/*

# Ubicación del archivo a procesar.
name="CHIRPS_megalopolis"
input="data/$name.nc"
output="temo/CHIRPS_comp.nc"

echo
echo "Interpolación de CHIRPS"
echo

# Repetimos para cada año.
for i in {1985..2015}
do
    echo "Interpolando año $i..."
    cdo -s selyear,$i $input "temp/SAM/"$name"_"$y".nc"
    python interpolacion.py "temp/SAM/"$name"_"$y".nc" "temp/SAM/"$name"_"$y"_interp.nc"
    yes | rm "temp/SAM/"$name"_"$y".nc"
done

cdo -s mergetime temp/SAM/* $output
yes | rm temp/SAM/*

echo
echo "Procesamiento terminado."