# Reordena el NetCDF con las estadísticas de precipitación.

import sys
import pandas as pd
import xarray as xr

path = "temp/*.nc"
fname = sys.argv[1]

# Preprocesamiento de cada archivo.
def pre(ds):
    ds = ( ds.expand_dims( ESTADISTICA = 1
        ).rename_dims( { "XTIME":"MES" } 
        ).rename_vars( { "XLAT": "LATITUD", "XLONG": "LONGITUD",
        "XTIME": "MES", "Pcp": "PRECIPITACION" }
        ).drop_vars( ["XTIME_bnds"] )
        )
    return ds

# Abrimos todos los archivos.
ds = xr.open_mfdataset( path, combine = "nested", 
    concat_dim = "ESTADISTICA", parallel = True, preprocess = pre )

# Establecemos valores de variables
ds["MES"] = range(1, 13)
ds["ESTADISTICA"] = range(1, 5)

# Reordenamos.
ds.to_dataframe().reorder_levels( ["south_north",
    "west_east", "MES", "ESTADISTICA"] ).sort_index(
    ).to_xarray().set_coords( ["LONGITUD", "LATITUD"] )

ds.to_netcdf(fname)