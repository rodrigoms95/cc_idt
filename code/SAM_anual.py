# Calcula la serie de máximos anuales para varias duraciones de un año.
import sys
import xarray as xr

# Año a procesar
y = sys.argv[1]
# Dirección de la curva masa generada por CDO.
path = "temp/prec_miro_hist_hist_" + y + ".nc"

ds = xr.open_dataset(path)
ds_i = []

# Repetimos para cada duración
for i in range(1, 25):
    # Abrimos el año, lo recorremos la cantidad de pasos necesarios obtener
    # la precipitación acumulada para duración en cuestión, lo dividimos
    # entre la cantidad de pasos para calcular la intensidad de
    # precipitación, obtenemos el máximo de intensidad anual y agregamos
    # dimensiones de duración.
    ds_i.append( ( ( ds - ds.shift(XTIME=i) ) / i ).max( dim = "XTIME"
        ).assign_coords( coords = {"DURACION":i}
        ).expand_dims( dim = "DURACION" ) )

# Unimos todas las duraciones.
ds = xr.concat( ds_i, dim = "DURACION" )
# Agregamos la dimensión de año.
ds = ds.assign_coords( coords = {"AÑO":int(y)}
    ).expand_dims( dim = "AÑO" )
# Guardamos el archivo.
ds.to_netcdf(path)