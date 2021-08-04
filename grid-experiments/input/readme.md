#Input Data

The only data needed is the information about how OD pairs are distributed and the demand rates associated with different OD pairs. And all these data are displayed in the file with name OD.txt. In addition, the pattern of the data in this file is of the following form:

The coordination of the origin (the first two columns), the coordination of the destination (the next two columns), the Manhattan distance of the OD pair (the fifth column), the corresponding OD category that the OD pair belongs to (the sixth column), the type of the OD pair (the last column). 

Note that only OD pairs of type 1 are considered in the experiments conducted here. The reason why some redundant information is preserved is to keep consistency between data and code, originally designed to cope with different variants.
