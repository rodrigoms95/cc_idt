# Hace un ajuste a la distribución generalizada de valores extremos
# para derivar parámetros para el cálculo de las curvas IDF.
import sys
import warnings
import itertools
import numpy as np
import pandas as pd
import xarray as xr
from scipy import optimize

warnings.filterwarnings( "ignore", category = RuntimeWarning )
warnings.filterwarnings( "ignore", category = pd.errors.PerformanceWarning )

path_d = sys.argv[1]
path_g = sys.argv[2]
path_v = sys.argv[3]
period = sys.argv[4]
df = xr.open_dataset( path_d ).to_dataframe()

# Quitamos la intensidad, año, probabilidad, tiempo de retorno, y agregamos
# columnas para los parámetros de la distribución.
df = df.reorder_levels( ["LONGITUD", "LATITUD", "DURACION", "TIEMPO_RETORNO"] )
df_2 = df.copy().drop( ["PROBABILIDAD", "AÑO"], axis = 1 
    ).reset_index( "TIEMPO_RETORNO" )
df_2 = df_2.reset_index( "DURACION" )
df_3 = df_2.copy().drop( ["INTENSIDAD", "TIEMPO_RETORNO", "DURACION"],
    axis = 1 ).groupby( ["LONGITUD", "LATITUD"] ).mean()
cols = ["k", "m", "n", "c", "error"]
df_3[ cols ] = None

# Creamos la tabla a predecir.
d_l = [ 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 8, 10, 12, 15, 24 ]
t_l = [ 1, 2, 5, 10, 25, 50, 100, 200, 500, 1000, 10000 ]

# Repetimos para cada duración
#if period == "horas":
#    d_l = [ int(x) for x in [ 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6,
#        8, 10, 12, 16, 20, 1*24,  1.25*24, 1.5*24, 1.75*24, 2*24,
#        2.5*24, 3*24, 3.5*24, 4*24, 4.5*24, 5*24, 6*24, 7*24, 8*24,
#        9*24, 10*24, 15*24, 20*24, 30*24, 40*24, 50*24, 60*24 ] ]
#if period == "dias":
#    d_l = [ 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 2.5, 4, 4.5,
#         5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50, 60 ]
#t_l = [ 2, 3, 4, 5, 10, 15, 20, 25, 50, 75,
#     100, 150, 200, 250, 500, 750, 1000 ]

df_2 = pd.DataFrame( np.array( list( itertools.product(
    df_2.index.get_level_values("LONGITUD").unique(),
    df_2.index.get_level_values("LATITUD").unique(), d_l, t_l) ) ),
    columns = ["LONGITUD", "LATITUD", "DURACION", "TIEMPO_RETORNO"] )
df_2["INTENSIDAD"] = None
df_2 = df_2.set_index( ["LONGITUD", "LATITUD", "DURACION", "TIEMPO_RETORNO"] )

# Función que nos genera una curva idT.
def idT(X, k, m, n, c):
    return ( k * X[0] ** m ) / ( X[1] + c ) ** n

# Iteramos para cada celda y duración.
for i in df_3.index.get_level_values("LONGITUD").unique():
    print(f"Calculando coordenada {i:.3f}°W...")
    for j in df_3.index.get_level_values("LATITUD").unique():
        print(f"{j:.3f}°N {i:.3f}°W")
        # Método de Wenzel con mínimos cuadrados no lineales.

        # Mínimos cuadrados no lineales.
        df_4 = df.loc[ (i, j), "INTENSIDAD" ].reset_index()
        # Predictando.
        Y = df_4["INTENSIDAD"].values
        # Predictores.
        X = np.swapaxes( df_4[ ["TIEMPO_RETORNO", "DURACION"] ].values, 0, 1 )
        # Cálculo de parámetros.
        fit = optimize.curve_fit( f = idT, xdata = X, ydata = Y,
            full_output = True, maxfev = 10000 )

        # Coeficientes de las curvas idT.
        df_3.loc[ (i, j), cols[:-1] ] = fit[0]
        # Error.
        df_3.loc[ (i, j), cols[-1] ] = ( fit[2]["fvec"] ** 2 ).sum()

        # Calculamos las intensidades.
        X = np.swapaxes( df_2.loc[ (i, j) ].reset_index()[
            ["TIEMPO_RETORNO", "DURACION"] ].values, 0, 1 )
        df_2.loc[ (i, j), "INTENSIDAD"] = idT(
            X, *df_3.loc[ (i, j) ].iloc[0:4] )

# Guardamos los valores de intensidad de las curvas IDF.
ds = df_2.reorder_levels( ["LONGITUD", "LATITUD", "DURACION",
    "TIEMPO_RETORNO"] ).to_xarray().set_coords( ["LONGITUD", "LATITUD"] )
ds.to_netcdf(path_v)

# Guardamos los parámetros de la distribución GEV para las curvas IDF.
ds = df_3.to_xarray().set_coords( ["LONGITUD", "LATITUD"] )
ds.to_netcdf(path_g)