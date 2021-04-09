'''加载检索的邻边范围'''
import pandas as pd
import json
from basis.setting import MAX_SEARCH_LAYERS

neighbor_df = pd.read_csv("Simulation/data/neighbor/neighbor_%s.csv" % MAX_SEARCH_LAYERS)
ALL_NEIGHBOR_EDGES = [json.loads(neighbor_df["neighbor_edges"][i]) for i in range(neighbor_df.shape[0])]

print("加载全部的邻接情况")