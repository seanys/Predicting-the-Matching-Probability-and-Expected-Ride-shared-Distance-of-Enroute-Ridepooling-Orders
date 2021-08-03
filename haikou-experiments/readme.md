`prediction.py` : Predict the matching probability and expected ride/shared distance based on the demand rate `network/combined_0.csv` and network `network/all_edges.csv` `network/all_vertexes.csv`. The progam will download the matching relationship at first. If you just want to run a simple network, you can set the  max_OD_ID a small number.

```
if __name__ == "__main__":
    max_OD_ID = 10000
    InteratedSolver(max_OD_ID)
```

`simulation.py` : Simulate the occurrence, movements, and state transition of each order based on the datasets provided by DIDI Chuxing. 

`compare.py` : Analyse the simulation results and compare with the prediction results.

`network/`: The haikou road network.

`results/`: This simulation and prediction results of `prediction.py` and `simulation.py` are output to this folder.  

`paper_res/`: The results of this paper. 

`datasets/`: This folder contains the datasets provided by Didi Chuxing. It will be download from the Google Driver when running the  `simulation.py`. 

`matching_relationship/`: This folder contains all taker states, seeker states, and matching pairs in Haikou Road network processed in advance. It will be download from the Google Driver when running the  `prediction.py`. 
