from shapely.geometry import Point
from shapely.wkt import loads
import pandas as pd
from collections import Counter
from tqdm import tqdm

def count_poles(df_polos, df_geom):
    '''
    Realiza a contagem dos polos (e seu tipo) para cada geometria passada.

    Parametros
    ----------
    df_polos: Pandas DataFrame -
        float latitude
        float longitude
        string tipo -> indica o tipo do estabelecimento (ex: restaurante,
                farmacia etc)

    df_geom: Pandas DataFrame -
        Shapely Polygon geom -> objeto Shapely contendo a geometria desejada
                para se realizar a contagem dos polos (ex: setor censitario,
                bairro etc)
        int unique_cod -> codigo unico para cada geometria

    Retorno
    -------

    Pandas DataFrame - (campos: ...)
    '''
    print("Transformando str em Polygon")
    if isinstance(df_geom['geom'].iloc[0], str):
        df_geom['geom'] = df_geom['geom'].apply(loads)
    tipos = df_polos['tipo'].unique()
    dict_counter = {}
    index_counter = 0
    print("Vai transformar lat-lng em Point")
    df_polos['point'] = df_polos.apply(lambda x: Point(x['longitude'], x['latitude']), axis=1)
    print("Vai fazer a contagem")
    for row_geom in tqdm(df_geom.itertuples(), total=df_geom.shape[0]): 
        dict_geom = {}
        '''
        min_lng, min_lat, max_lng, max_lat = row_geom.geom.bounds
        mask = (df_polos.latitude.between(min_lat, max_lat) &
                df_polos.longitude.between(min_lng, max_lng))
        '''
        pts_contidos = [row_poles.tipo for row_poles in df_polos.itertuples() \
                            if row_geom.geom.contains(row_poles.point)] 
        if pts_contidos: 
            counter_tipos = Counter(pts_contidos) 
            for tipo in tipos: 
                dict_geom[tipo] = counter_tipos[tipo]
        else:
            for tipo in tipos:
                dict_geom[tipo] = 0

        dict_geom['geom'] = row_geom.geom
        dict_geom['cod_sc'] = row_geom.unique_cod
        dict_counter[index_counter] = dict_geom
        index_counter += 1
    return pd.DataFrame.from_dict(dict_counter, orient='index')
