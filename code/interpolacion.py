# Aumenta la resolución espacial de CHIRPS.

import sys

import pandas as pd
import xarray as xr

path_d = sys.argv[1]
path_r = sys.argv[2]

# Cargar el archivo con mayor resolución.
ds_1 = xr.open_dataset("../temp/prec_hist_hist_1985.nc")
ds_1["XLONG"] = ds_1["XLONG"].isel(south_north = 0)
ds_1["XLAT"] = ds_1["XLAT"].isel(west_east = 0)
ds_1 = ds_1.swap_dims( {"west_east": "XLONG", "south_north": "XLAT"} )

# Interpolación
ds_2 = xr.open_dataset( path_d
    ).rename_dims( {"time": "XTIME", "longitude": "XLONG",
    "latitude": "XLAT"} ).rename_vars( {"time": "XTIME",
    "longitude": "XLONG", "latitude": "XLAT", "precip": "Pcp"} 
    ).interp( {"XLAT": ds_1["XLAT"], "XLONG": ds_1["XLONG"]},
    method = "cubic" ).rename_dims( {"XLAT": "south_north",
    "XLONG": "west_east"} ).to_netcdf( path_r )