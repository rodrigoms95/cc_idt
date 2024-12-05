# Ajusta la resolución a los datos de ERA5

import sys
import os
import xarray as xr
import xesmf as xe
import numpy as np

# Cargamos el archivo de WRF.
# Historico
scn = sys.argv[1]
alg = "conservative"
fname_in  = ( "/home/rodr/Datos/WRF/Miroc6/Rain/files/"
    + f"zzz_Pcp_WRF_MIROC6_{scn}_HoraZ.nc" )
fname_out = f"/home/rodr/temp/cc_idt/WRF_regrid_ERA5_{scn}.nc"
fname_grid = "/home/rodr/Datos/era5-land/era5-land_total-precipitation.nc"

print("Interpolando datos")
if not os.path.exists(fname_out):
    ds_1 = xr.open_dataset( fname_in )
    ds_1["XLONG"] = ds_1["XLONG"].isel(south_north = 0)
    ds_1["XLAT"] = ds_1["XLAT"].isel(west_east = 0)
    ds_1 = ds_1.swap_dims( {"west_east": "XLONG", "south_north": "XLAT"} )

    # Quitamos celdas de la orilla.
    k = 10
    ds_1 = ds_1.isel( { "XLAT": slice(k, -k), "XLONG": slice(k, -k) } )

    # Cargamos el archivo de CHIRPS.
    ds_2 = xr.open_dataset(fname_grid ).rename( {"time": "XTIME",
        "lon": "XLONG", "lat": "XLAT", "var228": "Pcp"} )
    ds_2 = ds_2.sel( { "XLAT": slice(ds_1["XLAT"].max(),   ds_1["XLAT"].min()),
            "XLONG": slice(ds_1["XLONG"].min(), ds_1["XLONG"].max()), } )

    # Cambiamos la resolución.
    regridder = xe.Regridder(ds_1, ds_2, alg)
    ds_out = regridder(ds_1, keep_attrs=True).astype(np.float32)

    # Guardamos el archivo.
    ds_out.to_netcdf(fname_out)