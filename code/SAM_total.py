# Genera un NetCDF con todas las duraciones, tiempos de retornos
# y probabilidades de excedencia.
import sys
import xarray as xr

# Cargamos todos los años.
fname = sys.argv[1]
path = "temp/*nc"
ds = xr.open_mfdataset( path, parallel = True )

# Iteramos para todas las duraciones.
ds_i = []
for i in ds["DURACION"].values:
    # Separamos por duración, reordenamos la intensidad
    # de precipitación de cada celda de mayor a menor.
    df = ds.sel( DURACION = [i] ).to_dataframe().sort_values(
        ["south_north", "west_east", "Pcp"], ascending = [True, True, False] )
    # Calculamos el número de orden de mayor a menor.
    df["m"] = ( list( range(1, ds["AÑO"].count().values + 1 ) )
        * ( ds["west_east"].max().values + 1 )
        * ( ds["south_north"].max().values + 1 ) )
    # Calculamos el tiempo de retorno.
    df["TIEMPO_RETORNO"] = ( ds["AÑO"].count().values + 1 ) / df["m"]
    # Calculamos la probabilidad de excedencia.
    df["PROBABILIDAD"] = 1/ df["TIEMPO_RETORNO"]
    ds_i.append( df.drop("m", axis = 1).to_xarray() )

# Unimos todos los archivos, reordenamos y renombramos variables.
ds = xr.concat( ds_i, dim = "DURACION" ).to_dataframe().reset_index("AÑO"
    ).set_index( "TIEMPO_RETORNO", append = True ).reorder_levels(
    ["south_north", "west_east", "DURACION", "TIEMPO_RETORNO"] ).sort_index(
    ).rename( {"XLONG":"LONGITUD", "XLAT": "LATITUD", "Pcp":"INTENSIDAD"},
    axis = 1 ).to_xarray().set_coords( ["LONGITUD", "LATITUD"] )
ds["LONGITUD"] = ds["LONGITUD"].isel( {"DURACION": 1, "TIEMPO_RETORNO": 1}
    ).drop( ["DURACION", "TIEMPO_RETORNO"] )
ds["LATITUD"] = ds["LATITUD"].isel( {"DURACION": 1, "TIEMPO_RETORNO": 1}
    ).drop( ["DURACION", "TIEMPO_RETORNO"] )

ds.to_netcdf(fname)