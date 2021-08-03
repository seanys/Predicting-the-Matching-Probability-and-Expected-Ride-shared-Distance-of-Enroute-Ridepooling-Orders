'''Load the neighbor edges of a node'''
import pandas as pd
import json
from basis.setting import MAX_SEARCH_LAYERS

neighbor_df = pd.read_csv("haikou-experiments/network/neighbor_%s.csv" % MAX_SEARCH_LAYERS)
ALL_NEIGHBOR_EDGES = [json.loads(neighbor_df["neighbor_edges"][i]) for i in range(neighbor_df.shape[0])]

print("Load neighbor edges of node")
