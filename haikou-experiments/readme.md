`prediction.py` : Predict the matching probability and expected ride/shared distance based on the demand rate `network/combined_0.csv` and network `network/all_edges.csv` `network/all_vertexes.csv`. The progam will download the matching relationship at first. If you just want to run a simple network, you can set the  max_OD_ID a small number.

```
if __name__ == "__main__":
    max_OD_ID = 10000
    InteratedSolver(max_OD_ID)
```

`simulation.py` : Simulate the carpooling system based on the order provided by DIDI Chuxing. 

`compare.py` : Analyse the simulation results and compare with the prediction results.