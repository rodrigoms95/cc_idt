# Reordena el NetCDF con las estadísticas de precipitación.

import sys
import pandas as pd
import xarray as xr

fname = sys.argv[1]
tot   = sys.argv[2]
path  = f"{sys.argv[3]}*.nc"

# Preprocesamiento de cada archivo.
def pre(ds):
    ds = ds.expand_dims( ESTADISTICA = 1 )
    return ds

# Abrimos todos los archivos.
ds = xr.open_mfdataset( path, combine = "nested", 
    concat_dim = "ESTADISTICA", parallel = True, preprocess = pre )
for v in ["XTIME_bnds", "time_bnds"]:
    if v in list(ds.keys()): ds = ds.drop_vars(v)
for v in ["Pcp", "precip", "var228"]:
    if v in list(ds.keys()): ds = ds.rename_vars({v: "PRECIPITACION"})
for v in ["XTIME", "time"]:
    if v in ds["PRECIPITACION"].dims: ds = ds.rename({v: "MES"})
for v in ["XLAT", "latitude", "lat"]:
    if v in ds["PRECIPITACION"].dims: ds = ds.rename({v: "LATITUD"})
for v in ["XLONG", "longitude", "lon"]:
    if v in ds["PRECIPITACION"].dims: ds = ds.rename({v: "LONGITUD"})

# Solo para la corrida completa de WRF.
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