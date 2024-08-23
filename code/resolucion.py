import xarray as xr
import xesmf as xe

# Cargamos el archivo de WRF.
# Historico
hist = False
if hist:
    fname_in  = ( "../../Datos/WRF/Miroc6/Rain/files/"
        + "zzz_Pcp_WRF_MIROC6_198501-201412_HoraZ.nc" )
    fname_out = "../../temp/cc_idt/WRF_regrid_ERA5_1985_2014.nc"
else:
    fname_in  = ( "../../Datos/WRF/Miroc6/Rain/files/"
        + "zzz_Pcp_WRF_MIROC6_204001-205912_HoraZ.nc" )
    fname_out = "../../temp/cc_idt/WRF_regrid_ERA5_2040_2059.nc"
fname_grid = "../../Datos/era5-land/era5-land_total-precipitation.nc"
ds_1 = xr.open_dataset( fname_in )
ds_1["XLONG"] = ds_1["XLONG"].isel(south_north = 0)
ds_1["XLAT"] = ds_1["XLAT"].isel(west_east = 0)
ds_1 = ds_1.swap_dims( {"west_east": "XLONG", "south_north": "XLAT"} )

# Quitamos celdas de la orilla.
k = 1
ds_1 = ds_1.isel( { "XLAT": slice(k, -k), "XLONG": slice(k, -k) } )

# Cargamos el archivo de CHIRPS.
ds_2 = xr.open_dataset(fname_grid ).rename( {"time": "XTIME",
    "lon": "XLONG", "lat": "XLAT", "var228": "Pcp"} )

# Cambiamos la resolución.
regridder = xe.Regridder(ds_1, ds_2, "conservative")
ds_out = regridder(ds_1, keep_attrs=True)

# Guardamos el archivo.
ds_out.to_netcdf( fname_out )

ds_out