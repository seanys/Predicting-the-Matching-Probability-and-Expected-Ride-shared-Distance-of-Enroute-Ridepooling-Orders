import json
import pandas as pd

ALL_VERTEXES = {}
data = pd.read_csv("HaiKou/network/all_vertexes.csv")
for i in range(data.shape[0]):
    ALL_VERTEXES[data["id"][i]] = { "block":json.loads(data["block"][i]), "front_arc":json.loads(data["front_arc"][i]),
        "front_ver":json.loads(data["front_ver"][i]), "sub_arc":json.loads(data["sub_arc"][i]), 
            "sub_ver":json.loads(data["sub_ver"][i]), "pair_id":json.loads(data["pair_id"][i]) }
print("Load all vertexes")
