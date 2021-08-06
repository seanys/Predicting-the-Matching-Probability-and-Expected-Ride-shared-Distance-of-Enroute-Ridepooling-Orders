`prediction.py` : Predict the matching probability and expected ride/shared distance based on the demand rate `network/combined_0.csv` and network `network/all_edges.csv` `network/all_vertexes.csv`. The progam will download the matching relationship at first. If you just want to run a simple network, you can set the  max_OD_ID a small number.

```
if __name__ == "__main__":
    max_OD_ID = 10000
    InteratedSolver(max_OD_ID)
```

`simulation.py` : Simulate the occurrence, movements, and state transition of each order based on the datasets provided by DIDI Chuxing. 

> Please install the needed packages by pip: `pandas`, `csv`, `progressbar`, `scipy`, `json`, `numpy`, `simpy`

`compare.py` : Analyze the simulation results and compare with the prediction results.

`network/`: The Haikou road network.

`results/`: This simulation and prediction results of `prediction.py` and `simulation.py` are output to this folder.  

`paper_res/`: The results of this paper. 

`datasets/`: This folder contains the datasets provided by Didi Chuxing. It will be download from the Google Driver when running the  `simulation.py`. 

`matching_relationship/`: This folder contains all taker states, seeker states, and OD pairs in Haikou Road network processed in advance. The set of matching taker states of a seeker state, the set of matching seeker states of a taker state, and the taker/seeker states contained by an OD pair are respectively stored in `seekers.csv`, `takers.csv`, and `ODs.csv`. It will be download from the Google Driver when running the  `prediction.py`. 

