# Reordena el NetCDF con las estadísticas de precipitación.

import sys
import pandas as pd
import xarray as xr

path  = "temp/SAM/*.nc"
fname = sys.argv[1]
type  = sys.argv[2]
tot   = sys.argv[3]

# Preprocesamiento de cada archivo.

# WRF
if type == "WRF":
    def pre(ds):
        ds = ( ds.expand_dims( ESTADISTICA = 1
            ).rename( {"XTIME": "MES", "Pcp": "PRECIPITACION",
            "XLAT": "LATITUD", "XLONG": "LONGITUD"}
            ).drop_vars( ["XTIME_bnds"] ) )
        return ds

# CHIRPS
if type == "CHIRPS":
    def pre(ds):
        ds = ( ds.expand_dims( ESTADISTICA = 1
            ).drop( "time_bnds" ).rename( {
                "time":"MES", "latitude": "LATITUD",
                "longitude": "LONGITUD", "precip": "PRECIPITACION" } ) )
        return ds

# Abrimos todos los archivos.
ds = xr.open_mfdataset( path, combine = "nested", 
    concat_dim = "ESTADISTICA", parallel = True, preprocess = pre )

# Solo para la corrida completa de WRf.
if tot == "Y":
    ds["LATITUD" ] = ds["LATITUD" ].isel( {"west_east"  : 0} )
    ds["LONGITUD"] = ds["LONGITUD"].isel( {"south_north": 0} )
    ds = ds.swap_dims( {"south_north": "LATITUD", "west_east": "LONGITUD"} )

# Establecemos valores de variables
ds["MES"] = range(1, 13)
ds["ESTADISTICA"] = range(1, 5)

# Reordenamos.
ds = ds.to_dataframe().reorder_levels( ["LATITUD",
    "LONGITUD", "MES", "ESTADISTICA"] ).sort_index(
    ).to_xarray().set_coords( ["LONGITUD", "LATITUD"] )

ds.to_netcdf(fname)