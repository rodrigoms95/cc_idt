# Calcula el hietograma a partir de la curva masa diaria
import xarray as xr
data = "/home/rodr/Datos/era5-land/"
in_name = "era5-land_total-precipitation_cum.nc"
out_name = "era5-land_total-precipitation.nc"

ds = xr.open_dataset(data + in_name)
ds_i=[]
for i in range(int((ds["time"].shape[0]+1)/24)):
    ds_i.append(ds.isel(time=slice(24*i, 24*(i+1)))
        -ds.isel(time=slice(24*i, 24*(i+1))).shift({"time":1}).fillna(0))
xr.concat(ds_i, dim="time").clip(min=0).to_netcdf(data + out_name)