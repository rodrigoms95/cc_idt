mlon1=-100.4751
mlon2=-97.3249
mlat1=18.1249
mlat2=20.6751

for filename in *.nc; do
    echo "Procesando ${filename##*/}"
    # Evita errores en la wildcard.
    # Escoge el nombre del nuevo archivo.
    # ${filename##*/} quita todo el directorio.
    moutfile="megalopolis_${filename##*/}"
    # Recorta al tamaño de México.
    cdo sellonlatbox,$mlon1,$mlon2,$mlat1,$mlat2 $filename $moutfile
    echo "${filename##*/} procesado"
    echo ""
done

