# Extrae variables de WRF

import os
import sys
import numpy as np
import xarray as xr

# Cargamos datos.
scn   = sys.argv[1]
dir_o = "/home/rodr/buffalo/rodr/WRF/"
dir_d = f"{dir_o}{scn}/{scn}/"
dir_r = f"{dir_o}{scn}/Rain/"
if not os.path.exists(dir_r): os.mkdir(dir_r)
files = os.listdir(dir_d)
files.sort

print("Extrayendo variables")
for f in files:
    print(f"{f}               ", end = "\r")
    if not os.path.exists(dir_r + "_".join(f.split("_")[1:])):
        ds = xr.open_dataset(dir_d + f)[["RAINNC"]
            ].rename_vars({"RAINNC": "Pcp"})
        ds["Pcp"] =  (ds["Pcp"] - ds["Pcp"].shift({"XTIME": 1}).where(
            ds["Pcp"].shift({"XTIME": 1}), 0))
        ds["Pcp"] =  ds["Pcp"].where(ds["Pcp"]>0,0)
        ds.to_netcdf(dir_r + f[16:])
print()
print()