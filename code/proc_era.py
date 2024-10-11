# Calcula el hietograma a partir de la curva masa diaria
import xarray as xr
data = "/home/rodr/Datos/era5-land/"
in_name = "era5-land_total-precipitation.nc"
ds = xr.open_dataset(data + in_name)
ds.shift({"time": -1}).groupby(ds["time"].dt.dayofyear).apply(
    lambda x: x - x.shift({"time": 1}).where(
    x.shift({"time": 1}).notnull(), 0)).to_netcdf(data + in_name)