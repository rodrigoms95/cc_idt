# Obtiene la curva de distribución acumulada para el mapeo de cuantiles

# Importamos librerías
import sys
import os
import numpy as np
import pandas as pd
import xarray as xr

# Datos

# Variables
var = "Pcp"
dims = [ "XTIME", "XLAT", "XLONG" ]

# Archivos a cargar
scn = sys.argv[1]
mult = 1
temp_dir = "/home/rodr/temp/cc_idt/"
if scn == "0":
    path_d = "../data/CHIRPS_megalopolis.nc"
    path_r = "../temp/CHIRPS_megalopolis_cdf.nc"
elif scn == "1":
    path_d = "../temp/WRF_regrid_CHIRPS_days.nc"
    path_r = "../temp/WRF_regrid_CHIRPS_days_cdf.nc"
elif scn == "2":
    path_d = "../temp/WRF_2040_regrid_CHIRPS_days.nc"
    path_r = "../temp/WRF_2040_regrid_CHIRPS_days_cdf.nc"
elif scn == "3":
    path_d = "../../Datos/era5-land/era5-land_total-precipitation.nc"
    path_r = f"{temp_dir}era5-land_total-precipitation_cdf.nc"
    mult = 1000
elif scn == "4":
    path_d = "../../Datos/era5-land/era5-land_total-precipitation_days.nc"
    path_r = f"{temp_dir}era5-land_total-precipitation_days_cdf.nc"
    mult = 1000
else:
    path_d = f"{temp_dir}WRF_regrid_ERA5_{scn}.nc"
    path_r = f"{temp_dir}WRF_regrid_ERA5_{scn}_cdf.nc"

# Abrimos el archivo
if not os.path.exists(path_r):
    print("Calculando curva de distribución acumulada")
    with xr.open_dataset(path_d) as ds:

        ds = ds.drop_dims("bnds", errors = "ignore")

        for v in ["precip", "var228"]:
            if v in list(ds.keys()): ds = ds.rename({v: var})
        for v in ["time"]:
            if v in ds[var].dims: ds = ds.rename({v: "XTIME"})
        for v in ["latitude", "lat"]:
            if v in ds[var].dims: ds = ds.rename({v: "XLAT"})
        for v in ["longitude", "lon"]:
            if v in ds[var].dims: ds = ds.rename({v: "XLONG"})
        ds[var] *= mult
        
        # Creamos un dataframe
        df = ds.to_dataframe().reorder_levels(dims)

        # Lista de coordenadas
        latitude = df.index.get_level_values(dims[1]).unique()
        longitude = df.index.get_level_values(dims[2]).unique()

        # Obtenemos la curva de distribución acumulada para cada celda
        df["q_model"] = 0.0
        for lat in latitude:
            print(f"Procesando coordenadas {lat}°N...")
            for lon in longitude:
                # Seleccionamos la coordenada
                df_c = df.loc[ (slice(None), lat, lon),
                    [var, "q_model"] ].sort_values(var)
                # Asignamos los cuantiles
                df_c["q_model"] = np.linspace(
                    1/df_c.shape[0], 1, df_c.shape[0])
                df.loc[ (slice(None), lat, lon), "q_model" ] = df_c["q_model"]

        # Guardamos el archivo.
        df.to_xarray().astype(np.float32).to_netcdf(path_r)
print()