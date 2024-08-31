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
# 0 observado CHIRPS
# 1 actual CHIRPS
# 2 futuro CHIRPS
# 3 observado ERA 5
# 4 actual ERA 5
# 5 futuro ERA 5
model = sys.argv[1]
if model == "0":
    path_d = "../data/CHIRPS_megalopolis.nc"
    path_r = "../temp/CHIRPS_megalopolis_cdf.nc"
    mult = 1
elif model == "1":
    path_d = "../temp/WRF_regrid_CHIRPS_days.nc"
    path_r = "../temp/WRF_regrid_CHIRPS_days_cdf.nc"
    mult = 1
elif model == "2":
    path_d = "../temp/WRF_2040_regrid_CHIRPS_days.nc"
    path_r = "../temp/WRF_2040_regrid_CHIRPS_days_cdf.nc"
    mult = 1
elif model == "3":
    path_d = "../../Datos/era5-land/era5-land_total-precipitation.nc"
    path_r = "../../temp/cc_idt/era5-land_total-precipitation_cdf.nc"
    mult = 1000
elif model == "4":
    path_d = "../../temp/cc_idt/WRF_regrid_ERA5_1985_2014.nc"
    path_r = "../../temp/cc_idt/WRF_regrid_ERA5_1985_2014_cdf.nc"
    mult = 1
elif model == "5":
    path_d = "../../temp/cc_idt/WRF_regrid_ERA5_2040_2059.nc"
    path_r = "../../temp/cc_idt/WRF_regrid_ERA5_2040_2059_cdf.nc"
    mult = 1

# Abrimos el archivo
with xr.open_dataset(path_d) as ds:

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
            df_c["q_model"] = np.linspace( 1/df_c.shape[0], 1, df_c.shape[0] )
            df.loc[ (slice(None), lat, lon), "q_model" ] = df_c["q_model"]

    # Guardamos el archivo.
    df.to_xarray().to_netcdf( path_r, mode = "w" )