# Obtiene la curva de distribución acumulada para el mapeo de cuantiles

# Importamos librerías
import sys
import os
import numpy as np
import pandas as pd
import xarray as xr

# Datos

# Variables
v = "Pcp"
dims = [ "XTIME", "XLAT", "XLONG" ]

# Archivos a cargar
# 0 observado CHIRPS
# 1 actual CHIRPS
# 2 futuro CHIRPS
# 3 observado ERA 5
model = sys.argv[1]
if model == "0":
    path_d = "../data/CHIRPS_megalopolis.nc"
    path_r = "../temp/CHIRPS_megalopolis_cdf.nc"
elif model == "1":
    path_d = "../temp/WRF_regrid_CHIRPS_days.nc"
    path_r = "../temp/WRF_regrid_CHIRPS_days_cdf.nc"
elif model == "2":
    path_d = "../temp/WRF_2040_regrid_CHIRPS_days.nc"
    path_r = "../temp/WRF_2040_regrid_CHIRPS_days_cdf.nc"
elif model == "3":
    path_d = "../../Datos/era5-land/era5-land_total-precipitation.nc"
    path_r = "../../temp/cc_idt/era5-land_total-precipitation_cdf.nc"

# Abrimos el archivo
with xr.open_dataset(path_d) as ds:
    # Homologamos nombres
    if model == "0":
        ds = ds.rename( {"time": "XTIME", "longitude": "XLONG", 
            "latitude": "XLAT", "precip": "Pcp"})
    elif model == "3": 
        ds = ds.rename_vars( { list(ds.keys())[0]: v,
            "time": dims[0], "lat": dims[1], "lon": dims[2] }
            ).swap_dims( { "time": dims[0], "lat": dims[1], "lon": dims[2] } )

    # Reordenamos variables
    ds = ds[dims + [v]]
    # Creamos un dataset sin la variable
    #ds_2 = ds.drop_vars( list(ds.keys()) ).copy()
    # Creamos un dataframe
    df = ds.to_dataframe()#.sort_index()

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
                [v, "q_model"] ].sort_values(v)
            # Asignamos los cuantiles
            df_c["q_model"] = np.linspace( 1/df_c.shape[0], 1, df_c.shape[0] )
            df.loc[ (slice(None), lat, lon), "q_model" ] = df_c["q_model"]

    # Covertimos a dataset
    ds["q_model"] = ( dims, df["q_model"].to_xarray().values )
    #ds_2["q_model"] = df["q_model"].to_xarray()
   # ds["q_model"] = ( dims, ds_2["q_model"].values )
    # Guardamos el archivo.
    ds.to_netcdf( path_r, mode = "w" )