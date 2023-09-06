# Hace un ajuste a la distribución generalizada de valores extremos
# para derivar parámetros para el cálculo de las curvas IDF.
import sys
import xarray as xr
from scipy import stats

path_d = sys.argv[1]
path_g = sys.argv[2]
path_v = sys.argv[3]
df = xr.open_dataset( path_d ).to_dataframe()

# Quitamos la intensidad, año, probabilidad, tiempo de retorno, y agregamos
# columnas para los parámetros de la distribución.
df_2 = df.copy().drop( ["PROBABILIDAD", "AÑO"], axis = 1 
    ).reset_index( "TIEMPO_RETORNO" )
#df_2 = df_2.reset_index( "DURACION" )
df_3 = df_2.copy().drop( ["INTENSIDAD", "TIEMPO_RETORNO"], axis = 1).groupby(
    ["south_north", "west_east", "DURACION"] ).mean()
cols = ["GEV_C", "GEV_LOC", "GEV_SCALE", "KTEST_P"]
df_3[ cols ] = None

# Ajustamos las duraciones y tiempos de retorno a calcular.
# Por el momento no se ajusta la duración ya que el método GEV solo permite
# calcular para las duraciones que se tienen parámetros, un método empírico
# como el de Aparicio, Chen, o Chow permiten interpolar fácilmente las
# duraciones.
#d = ( [ 5/60, 10/60, 15/60, 20/60, 30/60, 40/60, 1, 1.5, 2, 2.5,
#    3, 3.5, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24 ]
#    * df_2.index.get_level_values("west_east").unique()
#    * df_2.index.get_level_values("south_north").unique()
#    * df_2.index.get_level_values("TIEMPO_RETORNO"").unique() ) )
t = ( ( [5, 10, 25, 50, 100, 200, 500, 1000] + [None] * 23 )
    * df_2.index.get_level_values("west_east").unique().shape[0]
    * df_2.index.get_level_values("south_north").unique().shape[0]
    * df_2.index.get_level_values("DURACION").unique().shape[0] )
#df_2["DURACION"] = d
df_2["TIEMPO_RETORNO"] = t
df_2 = df_2.dropna()
#df_2 = df_2.set_index("DURACION", append = True).sort_values(
#    ["south_north", "west_east", "DURACION", "TIEMPO_RETORNO"] )

# Iteramos para cada celda y duración.
for i in df_3.index.get_level_values("west_east").unique():
    print("Calculando coordenada x #{i}...")
    for j in df_3.index.get_level_values("west_east").unique():
        for k in df_3.index.get_level_values("DURACION").unique():
            # ajustamos la distribución de valores extremos.
            params = stats.genextreme.fit( df.loc[ (i, j, k), "INTENSIDAD"] )
            # Hacemos la prueba Kolmogorov Smirnoff.
            pvalue = stats.kstest( df.loc[ (i, j, k), "INTENSIDAD"],
                stats.genextreme(*params).cdf ).pvalue
            df_3.loc[ (i, j, k), cols ] = [*params] + [pvalue]
            # Calculamos las intensidades de acuerdo con la distribución.
            df_2.loc[(i, j, k), "INTENSIDAD"] = stats.genextreme(
                *df_3.loc[(i, j, k), cols[:-1]] ).isf(
                1 / df_2.loc[(i, j, k), "TIEMPO_RETORNO"].values )

# Guardamos los valores de intensidad de las curvas IDF.
df_2.to_xarray().set_coords( ["LONGITUD", "LATITUD"] ).to_netcdf(path_v)
# Guardamos los parámetros de la distribución GEV para las curvas IDF.
df_3.to_xarray().set_coords( ["LONGITUD", "LATITUD"] ).to_netcdf(path_g)