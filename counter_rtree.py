from shapely.geometry import Point
from shapely.wkt import loads
import pandas as pd
from collections import Counter
from rtree import index
from tqdm import tqdm
import logging

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
    logger = generate_logger()
    if isinstance(df_geom['geom'].iloc[0], str):
        df_geom['geom'] = df_geom['geom'].apply(loads)
    tipos = df_polos['tipo'].unique()
    pois_index = index.Index(intervealed=True)
    logger.info("Indexando os pontos de interesse")
    for row_poles in df_polos.itertuples():
        pt_poles = Point(row_poles.longitude, row_poles.latitude)
        pois_index.insert(row_poles.Index, pt_poles.bounds,
                            obj=(pt_poles, row_poles.tipo))
    dict_counter = {}
    index_counter = 0
    for row_geom in tqdm(df_geom.itertuples(), total=df_geom.shape[0]):
        dict_geom = {}
        list_objs = list(pois_index.intersection(row_geom.geom.bounds,
                                         objects=True))
        tipos_concorrentes_geom = \
            [o.object[1] for o in list_objs if row_geom.geom.
             contains(o.object[0])]       
        if tipos_concorrentes_geom:
            counter_tipos = Counter(tipos_concorrentes_geom)
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