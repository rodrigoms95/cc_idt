# Genera un NetCDF con todas las duraciones, tiempos de retornos
# y probabilidades de excedencia.
import sys
import xarray as xr

# Cargamos todos los años.
fname  = sys.argv[1]
type   = sys.argv[2]
period = sys.argv[3]
path = "temp/SAM/*nc"
ds = xr.open_mfdataset( path, parallel = True )

# Iteramos para todas las duraciones.
ds_i = []

# WRF
if type == "WRF":
    for i in ds["DURACION"].values:
        # Separamos por duración, reordenamos la intensidad
        # de precipitación de cada celda de mayor a menor.
        df = ds.sel( DURACION = [i] ).to_dataframe().sort_values(
            ["south_north", "west_east", "Pcp"],
            ascending = [True, True, False] )
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
        ["south_north", "west_east", "DURACION", "TIEMPO_RETORNO"]
        ).sort_index().rename( {"XLONG":"LONGITUD", "XLAT": "LATITUD",
        "Pcp": "INTENSIDAD"}, axis = 1 ).to_xarray(
        ).set_coords( ["LONGITUD", "LATITUD"] )
    ds["LONGITUD"] = ds["LONGITUD"].isel( {"DURACION": 0,
        "TIEMPO_RETORNO": 0, "south_north": 0} )
    ds["LATITUD"] = ds["LATITUD"].isel( {"DURACION": 1,
        "TIEMPO_RETORNO": 0, "west_east": 0} )

# CHIRPS
if type == "CHIRPS":
    for i in ds["DURACION"].values:
        # Separamos por duración, reordenamos la intensidad
        # de precipitación de cada celda de mayor a menor.
        df = ds.sel( DURACION = [i] ).to_dataframe().sort_values(
            ["latitude", "longitude", "precip"],
            ascending = [True, True, False] )
        # Calculamos el número de orden de mayor a menor.
        df["m"] = ( list( range(1, ds["AÑO"].count().values + 1 ) )
            * ( ds["longitude"].count().values + 0 )
            * ( ds["latitude"].count().values + 0 ) )
    
        # Calculamos el tiempo de retorno.
        df["TIEMPO_RETORNO"] = ( ds["AÑO"].count().values + 1 ) / df["m"]
        # Calculamos la probabilidad de excedencia.
        df["PROBABILIDAD"] = 1/ df["TIEMPO_RETORNO"]
        ds_i.append( df.drop("m", axis = 1).to_xarray() )

    ds = xr.concat( ds_i, dim = "DURACION" ).to_dataframe(
        ).reset_index("AÑO"
        ).set_index( "TIEMPO_RETORNO", append = True ).to_xarray(
        ).rename_vars( {"longitude": "LONGITUD", "latitude": "LATITUD",
        "precip": "INTENSIDAD"} ).set_coords( ["LONGITUD", "LATITUD"] )
    
    ds["LONGITUD"] = ds["LONGITUD"].isel( {"DURACION": 0,
        "TIEMPO_RETORNO": 0, "south_north": 0} )
    ds["LATITUD"]  = ds["LATITUD" ].isel( {"DURACION": 0,
        "TIEMPO_RETORNO": 0, "west_east": 0} )
    
ds.to_netcdf(fname)