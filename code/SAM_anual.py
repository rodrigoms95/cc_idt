# Calcula la serie de máximos anuales para varias duraciones de un año.
import sys
import xarray as xr

# Año a procesar
y = sys.argv[1]
# Dirección de la curva masa generada por CDO.
path   = sys.argv[2] + "_" + y + ".nc"
period = sys.argv[3]

ds = xr.open_dataset(path)
for v in ["XTIME_bnds", "time_bnds"]:
    if v in list(ds.keys()): ds = ds.drop_vars(v)
for v in ["Pcp", "precip", "var228"]:
    if v in list(ds.keys()): ds = ds.rename_vars({v: "PRECIPITACION"})
for v in ["XTIME"]:
    if v in ds["PRECIPITACION"].dims: ds = ds.rename({v: "time"})
for v in ["XLAT", "latitude", "lat"]:
    if v in ds["PRECIPITACION"].dims: ds = ds.rename({v: "LATITUD"})
for v in ["XLONG", "longitude", "lon"]:
    if v in ds["PRECIPITACION"].dims: ds = ds.rename({v: "LONGITUD"})

ds_i = []

# Repetimos para cada duración
if period == "horas":
    dur = [ int(x) for x in [ 1, 2, 3, 4, 5, 6, 8, 10, 12,
        16, 20, 1*24 ] ]
    #dur = [ int(x) for x in [ 
    #    1*24,  1.25*24, 1.5*24, 1.75*24, 2*24, 2.5*24,
    #    3*24, 3.5*24, 4*24, 4.5*24, 5*24, 6*24, 7*24, 8*24,
    #    9*24, 10*24, 15*24, 20*24, 30*24, 40*24, 50*24, 60*24 ] ]
    #dur = [ int(x) for x in [ 1, 2, 3, 4, 5, 6, 8, 10, 12,
    #    16, 20, 1*24,  1.25*24, 1.5*24, 1.75*24, 2*24, 2.5*24,
    #    3*24, 3.5*24, 4*24, 4.5*24, 5*24, 6*24, 7*24, 8*24,
    #    9*24, 10*24, 15*24, 20*24, 30*24, 40*24, 50*24, 60*24 ] ]
if period == "dias":
    dur = [ 1, 2, 3, 4, 5, 10, 15, 20, 30, 40, 50, 60 ]

for i in dur:
    ds_i.append( ( ( ds - ds.shift( {"time": i} ) ) / i ).max(
        dim = "time" ).assign_coords( coords = {"DURACION": i}
        ).expand_dims( dim = "DURACION" ) )
ds = xr.concat( ds_i, dim = "DURACION" )

# Agregamos la dimensión de año.
ds = ds.assign_coords( coords = {"AÑO":int(y)} ).expand_dims( dim = "AÑO" )

# Guardamos el archivo.
ds.to_netcdf(path)