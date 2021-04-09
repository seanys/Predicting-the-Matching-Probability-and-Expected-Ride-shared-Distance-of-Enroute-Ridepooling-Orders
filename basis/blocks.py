'''
区块：区块及其衔接情况
'''
import json
import pandas as pd
from shapely.geometry import Polygon

data = pd.read_csv("HaiKou/network/blocks.csv")
ALL_BLOCKS = {}
for i in range(data.shape[0]):
    ALL_BLOCKS[data["id"][i]] = {"neighbor":json.loads(data["neighbor"][i]), "vertexes":json.loads(data["vertexes"][i]),
        "primary_edge_ids":json.loads(data["primary_edge_ids"][i]), "polyline":json.loads(data["polyline"][i]), 
            "block_item":Polygon(json.loads(data["polyline"][i])) }
print("区块加载成功")
