# Experiments in a Grid Network

These folders in this page are built to provide readers with access to the input data, code and some key results related to the experiments couducted across a grid network. For more detailed description about the setting of these experiments, please refer to the paper named predicting the matching probability and ride/shared distance for each dynamic ridepooling order: A mathematical modeling approach. As indicated by the names of these folders, the input data, code and results are organized in different folders with name input, program and output, respectively. For the purpose of clear exposition, more words attached to each floder are put inside each floder.


 

## Data

The only data needed is the information about how OD pairs are distributed and the demand rates associated with different OD pairs. And all these data are displayed in the file with name OD.txt. In addition, the pattern of the data in this file is of the following form:

The coordination of the origin (the first two columns), the coordination of the destination (the next two columns), the Manhattan distance of the OD pair (the fifth column), the corresponding OD category that the OD pair belongs to (the sixth column), the type of the OD pair (the last column). 

Note that only OD pairs of type 1 are considered in the experiments conducted here. The reason why some redundant information is preserved is to keep consistency between data and code, originally designed to cope with different variants.

 

## Code

The code, strictly following the ideas illustrated in this paper, and programmed in JAVA, is divided into two folders, named version2_theory and version2_simulation, respectively. As the name indicates, the first folder contains source of code for the purpose to implement the procedure of obtaining the prediction value of the matching probability and ride/shared distance for each OD pair. In order to validate the accuracy of estimation results, corresponding simulation experiments are conducted with code contained in the latter folder.

Since the codes provided above only produce primitive results, a lot of procedure should be gone through to obtain the key performance indicators which measure the accuracy of the prediction results compared to the simulation one. Because of the advantages of Python over JAVA in processing data, these procedures are programmed in Python collected in the folder named python. One can easily recognize, from the name, the purpose of each file which is explained in detail below:

Get_simulation_result_from_original_data: this file is created to get matching probabilities, ride/shared distance for each OD pair from simulation results produced by project in version2_simulation. 

Combine_theory_simulation_together: this combines the theory and simulation results together for each scenario in order to calculate the errors between them.

Get_convergence_for_all_scenarios: this file checks whether the prediction results gained converge when the corresponding experiment terminates for each scenario.

Get_route_data_include_theory_and_simulation: this code collects all data with convergent prediction results, including prediction and simulation results, corresponding to a specific OD pair into one file for each OD pair

Get_key_performance_indicators: this file is used to calculate the key performance indicators, including RMSE and MAPE, for each OD pair

Plot_rmse_mape_boxplot: this file, as implied by the name, is used to present the key performance indicators by graphs. 

 

## Result

Constrained by the limited storage space, only key results are performed here. 

Convergent_result: this file makes a display of the information about the convergency for each scenario.

Rmse_mape: this file shows the RMSE and MAPE of the matching probability, ride/shared distance for each OD pair

Rmse_mape_normal_distribution: this file also shows the RMSE and MAPE of the matching probability, ride/shared distance for each OD pair. But this is for the variant version with the waiting time following normal distribution instead of a constant for each OD pair.

  
