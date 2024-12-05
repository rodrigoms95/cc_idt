# Corrección de cuantiles empírica.

import os
import sys
import numpy as np
import pandas as pd

import xarray as xr

v = "Pcp"
dims = ["XTIME", "XLAT", "XLONG"]

scn = sys.argv[1]

path_d    = f"/home/rodr/temp/cc_idt/era5-land_total-precipitation_cdf.nc"
path_m    = f"/home/rodr/temp/cc_idt/WRF_regrid_ERA5_1985_2014_cdf.nc"
path_f    = f"/home/rodr//temp/cc_idt/WRF_regrid_ERA5_{scn}_cdf.nc"
path_res  = f"/home/rodr/temp/cc_idt/WRF_regrid_ERA5_1985_2014_map.nc"
path_map  = f"/home/rodr/temp/cc_idt/WRF_regrid_ERA5_1985_2014_qmap.nc"
path_fmap = f"/home/rodr/temp/cc_idt/WRF_regrid_ERA5_{scn}_qmap.nc"

sum = True

print("Realizando corrección de cuantiles")
with xr.open_dataset(path_d) as ds_d:
    with xr.open_dataset(path_m) as ds_m:
        with xr.open_dataset(path_f) as ds_f:

            ds_d = ds_d.sel( {
                 "XLAT": slice(ds_m["XLAT"].max(),   ds_m["XLAT"].min()),
                "XLONG": slice(ds_m["XLONG"].min(), ds_m["XLONG"].max()) } )

            df_d = ds_d.to_dataframe().reorder_levels(dims).sort_index()
            df_m = ds_m.to_dataframe().reorder_levels(dims).sort_index()
            df_f = ds_f.to_dataframe().reorder_levels(dims).sort_index()

            df_f["map"] = None
            df_m["map"] = None
            df_m["diff_sum"] = None

            latitude_d = df_d.index.get_level_values(dims[1]).unique()
            longitude_d = df_d.index.get_level_values(dims[2]).unique()
            latitude_m = df_m.index.get_level_values(dims[1]).unique()
            longitude_m = df_m.index.get_level_values(dims[2]).unique()
            latitude_f = df_f.index.get_level_values(dims[1]).unique()
            longitude_f = df_f.index.get_level_values(dims[2]).unique()


            for i in range(len(latitude_d)):
                print(f"{latitude_d[i]:.3f}°N")
                for j in range(len(longitude_d)):
                    df_xs_m = df_m.loc[ (slice(None), latitude_m[i],
                        longitude_m[j]), df_m.columns ].sort_values("q_model")
                    df_xs_d = df_d.loc[ (slice(None), latitude_d[i],
                        longitude_d[j]), df_d.columns ].sort_values("q_model")
                    df_xs_m["map"] = np.interp( df_xs_m["q_model"].values,
                        df_xs_d["q_model"].values, df_xs_d[v].values )
                    df_xs_m["map"] = df_xs_m["map"].where(df_xs_m["map"]>0, 0)
                    df_xs_m["diff_sum"] = df_xs_m["map"] - df_xs_m[v]
                    df_m.loc[ (slice(None), latitude_m[i],
                        longitude_m[j]), df_m.columns ] = df_xs_m

                    df_xs_f = df_f.loc[ (slice(None), latitude_f[i],
                        longitude_f[j]),  df_f.columns ].sort_values("q_model")
                    df_xs_f["map"] = np.interp( df_xs_f["q_model"].values,
                        df_xs_m["q_model"].values,
                        df_xs_m["diff_sum"].values )
                    df_xs_f["map"] = df_xs_f["map"] + df_xs_f[v]
                    df_xs_f["map"] = df_xs_f["map"].where(df_xs_f["map"]>0, 0)
                    df_f.loc[ (slice(None), latitude_f[i],
                        longitude_f[j]), df_f.columns ] = df_xs_f
                    
                    del df_xs_f; del df_xs_m; del df_xs_d;

            del df_d

            ds_map = df_m.to_xarray()
            del df_m
            ds_m["map"] = ( dims, ds_map["map"].values[:,::-1,:] )
            ds_m["diff_sum"] = ( dims, ds_map["diff_sum"].values[:,::-1,:] )
            if not os.path.exists(path_res):
                ds_m.to_netcdf( path_res )
            if not os.path.exists(path_map):
                ds_m[["map"]].rename( {"map": v} ).to_netcdf( path_map )

            ds_fmap = df_f.to_xarray()
            del df_f
            ds_f["map"] = ( dims, ds_fmap["map"].values[:,::-1,:] )
            if not os.path.exists(path_fmap):
                ds_f[["map"]].rename( {"map": v} ).to_netcdf( path_fmap )
print()
