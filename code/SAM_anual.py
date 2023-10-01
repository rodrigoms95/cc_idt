# Calcula la serie de máximos anuales para varias duraciones de un año.
import sys
import xarray as xr

# Año a procesar
y = sys.argv[1]
# Dirección de la curva masa generada por CDO.
path   = sys.argv[2] + "_" + y + ".nc"
type   = sys.argv[3]
period = sys.argv[4]

ds = xr.open_dataset(path)
ds_i = []

# Repetimos para cada duración
if period == "horas":
    dur = [ 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24,
        30, 36, 42, 48, 60, 72, 84, 96, 108, 120 ]
if period == "dias":
    dur = [ 1, 2, 3, 4, 5 ]

# WRF
if type == "WRF":
    for i in dur:
        # Abrimos el año, lo recorremos la cantidad de pasos necesarios
        # obtener la precipitación acumulada para duración en cuestión, lo
        # dividimos entre la cantidad de pasos para calcular la intensidad de
        # precipitación, obtenemos el máximo de intensidad anual y agregamos
        # dimensiones de duración.
        ds_i.append( ( 
            ( ds - ds.shift( XTIME = i ) )
            #/ i
            ).max( dim = "XTIME"
            ).assign_coords( coords = {"DURACION": i}
            ).expand_dims( dim = "DURACION" ) )

    # Unimos todas las duraciones.
    ds = xr.concat( ds_i, dim = "DURACION"
        ).rename( { "XLAT": "LATITUD", "XLONG": "LONGITUD" } 
        ).drop_vars("XTIME_bnds"
        )

# CHIRPS
if type == "CHIRPS":
    for i in dur:
        # Abrimos el año, lo recorremos la cantidad de pasos necesarios
        # obtener la precipitación acumulada para duración en cuestión, lo
        # dividimos entre la cantidad de pasos para calcular la intensidad de
        # precipitación, obtenemos el máximo de intensidad anual y agregamos
        # dimensiones de duración.
        ds_i.append( ( 
            ( ds - ds.shift( time = i ) )
            #/ i
            ).max( dim = "time"
            ).assign_coords( coords = {"DURACION": i}
            ).expand_dims( dim = "DURACION" ) )
    
    # Unimos todas las duraciones.
    ds = xr.concat( ds_i, dim = "DURACION" ).rename( {
        "latitude": "LATITUD", "longitude": "LONGITUD"} )
        
# Agregamos la dimensión de año.
ds = ds.assign_coords( coords = {"AÑO":int(y)}
    ).expand_dims( dim = "AÑO" )

# Guardamos el archivo.
ds.to_netcdf(path)