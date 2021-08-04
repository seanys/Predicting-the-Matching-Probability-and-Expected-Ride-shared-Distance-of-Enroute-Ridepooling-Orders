# Input Data

The only data needed is the information about how OD pairs are distributed over the grid network and the demand rates associated with different OD pairs. And all these data are displayed in the file with name `OD.txt`. In addition, the pattern of the data in this file is of the following form:

The coordination of the origin (the first two columns), the coordination of the destination (the next two columns), the Manhattan distance of the OD pair (the fifth column), the corresponding OD category that the OD pair belongs to (the sixth column). 

Note that the demand rates of OD pairs could be inferred from the sixth column, i.e., the OD category. More specifically, given demand scaler which is predetermined under each scenario, the actual demand rate of a specific OD pair is the product of demand scaler and the corresponding OD category that the OD belongs to.
