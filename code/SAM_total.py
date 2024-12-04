# Genera un NetCDF con todas las duraciones, tiempos de retornos
# y probabilidades de excedencia.
import sys
import xarray as xr

# Cargamos todos los años.
fname  = sys.argv[1]
period = sys.argv[2]
format = sys.argv[3]
path   = f"{sys.argv[4]}*.nc"
ds = xr.open_mfdataset( path, parallel = True )

# Tenemos el archivo completo de WRF que hay que ajustar.
if format == "Y":
    ds["LONGITUD"] = ds["LONGITUD"].isel(south_north = 0)
    ds["LATITUD"] = ds["LATITUD"].isel(west_east = 0)
    ds = ds.swap_dims( {"west_east": "LONGITUD", "south_north": "LATITUD"} )

# Iteramos para todas las duraciones.
ds_i = []

for i in ds["DURACION"].values:
    # Separamos por duración, reordenamos la intensidad
    # de precipitación de cada celda de mayor a menor.
    df = ds.sel( DURACION = [i] ).to_dataframe().sort_values(
        ["LONGITUD", "LATITUD", "PRECIPITACION"],
        ascending = [True, True, False] )

    # Calculamos el número de orden de mayor a menor.
    df["m"] = ( list( range(1, ds["AÑO"].count().values + 1 ) )
        * ( ds["LONGITUD"].count().values + 0 )
        * ( ds["LATITUD" ].count().values + 0 ) )

    # Calculamos el tiempo de retorno.
    df["TIEMPO_RETORNO"] = ( ds["AÑO"].count().values + 1 ) / df["m"]
    # Calculamos la probabilidad de excedencia.
    df["PROBABILIDAD"] = 1/ df["TIEMPO_RETORNO"]
    ds_i.append( df.drop("m", axis = 1).to_xarray() )

# Unimos todos los archivos, reordenamos y renombramos variables.
ds = xr.concat( ds_i, dim = "DURACION" ).to_dataframe().reset_index("AÑO"
    ).set_index( "TIEMPO_RETORNO", append = True ).reorder_levels(
    ["LONGITUD", "LATITUD", "DURACION", "TIEMPO_RETORNO"]
    ).sort_index().rename( {"PRECIPITACION": "INTENSIDAD"}, axis = 1
    ).to_xarray().set_coords( ["LONGITUD", "LATITUD"] )

#ds["INTENSIDAD"] *= 1000

ds.to_netcdf(fname)