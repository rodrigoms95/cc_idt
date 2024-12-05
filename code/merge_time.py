
# Une todos los meses y años

import os
import sys
import xarray as xr

# Cargamos datos.
scn   = sys.argv[1]
dir_o = "/home/rodr/buffalo/rodr/WRF/"
dir_d = f"{dir_o}{scn}/Rain/"
dir_r = "/home/rodr/Datos/WRF/Miroc6/Rain/files/"
if not os.path.exists(dir_r): os.mkdir(dir_r)
files = os.listdir(dir_d)
files.sort
files_d = [f"{dir_d}{x}" for x in files]

file_r = f"{dir_r}zzz_Pcp_WRF_MIROC6_{scn}_HoraZ.nc"
print("Uniendo datos temporales")
if not os.path.exists(file_r): xr.open_mfdataset(files_d).to_netcdf(file_r)
print()