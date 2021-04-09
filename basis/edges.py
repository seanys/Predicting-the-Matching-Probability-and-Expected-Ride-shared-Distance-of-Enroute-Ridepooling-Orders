'''
所有的边加载
'''
import json
import pandas as pd
from basis.assistant import getID

ALL_EDGES, ALL_EDGES_DIC = {},{}

data = pd.read_csv("HaiKou/network/all_edges.csv")
for i in range(data.shape[0]):
    ALL_EDGES[data["id"][i]] = { "block":json.loads(data["block"][i]), "length":data["length"][i], 
        "class":data["class"][i], "head_ver":data["head_ver"][i], "tail_ver":data["tail_ver"][i], 
            "polyline":json.loads(data["polyline"][i]) }
    # 用于字典检索，直接采用两个
    combined_id = getID(data["head_ver"][i],data["tail_ver"][i])
    ALL_EDGES_DIC[combined_id] = { "id": data["id"][i], "block":json.loads(data["block"][i]), "length":data["length"][i], 
        "class":data["class"][i], "head_ver":data["head_ver"][i], "tail_ver":data["tail_ver"][i] }
print("加载全部的边")
