# Some Key Results

Constrained by the limited storage space, only key results are performed here. 

`convergent_result.csv`: this file makes a display of the information about the convergency for the prediction procedure under each scenario. And the file is organized in the following pattern:

the parameters that specify a scenario (the first four columns), the convergency of the prediction procedure under the specified scenario (the fifth column), the running time of the estimation procedure measured in milliseconds (the sixth column), the number of whole iterations conducted by the estimation process (the last column).

`rmse_mape.csv`: this file shows the RMSE and MAPE of the matching probability, ride/shared distance for each OD pair. And the meaning of each column is well explained by the corresponding name of that column. Therefore, no further words are provided for more illustration.

`rmse_mape_normal_distribution.csv`: this file also shows the RMSE and MAPE of the matching probability, ride/shared distance for each OD pair. But this is for the variant version with the waiting time following normal distribution instead of a constant for each OD pair.