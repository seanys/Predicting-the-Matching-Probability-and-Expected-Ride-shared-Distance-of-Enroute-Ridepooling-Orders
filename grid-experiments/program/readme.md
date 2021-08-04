# Program

The code, strictly following the ideas illustrated in this paper, and programmed in JAVA, is mainly divided into two folders, named version2_theory and version2_simulation, respectively. As the names indicate, the first folder contains source of code for the purpose to implement the procedure of obtaining the prediction value of the matching probability and ride/shared distance for each OD pair under different scenarios. In order to validate the accuracy of estimation results, corresponding simulation experiments are conducted with code contained in the latter folder.

Note that the version of the JDK installed in my computer is 1.8.0_v112. And absolute path names are adopted in the code provided. Before compiling, make sure all path names are properly corrected and programing environment properly deployed, please. For convenience of adoption of the code, all directory names needed to be changed are collected in one file for each JAVA project. That is, Thread_simulation.java for version2_simulation, and MyThread.java for version2_theory, respectively. One can easily find the code to be rectified according to the structure of your own file system.

Since the codes provided above only produce primitive results, a lot of procedure should be gone through before obtaining the key performance indicators which measure the accuracy of the prediction results compared to the simulation one. Because of the advantages of Python over JAVA in processing data, these procedures are programmed in Python collected in the folder named python. One can easily recognize, from the name, the purpose of each file which is explained in detail below:

Get_simulation_result_from_original_data: this file is created to get matching probabilities, ride/shared distance for each OD pair from simulation results produced by the project in version2_simulation. 

Combine_theory_simulation_together: this combines the prediction and simulation results together for each scenario in order to calculate the errors related.

Get_convergence_for_all_scenarios: this file checks whether the prediction results gained converge finally when the corresponding experiment terminates for each scenario.

Get_route_data_include_theory_and_simulation: this code collects all data with convergent prediction results, including prediction and simulation results, corresponding to a specific OD pair into one file for each OD pair

Get_key_performance_indicators: this file is used to calculate the key performance indicators, including RMSE and MAPE, for each OD pair

Plot_rmse_mape_boxplot: this file, as implied by the name, is used to present the key performance indicators by graphs. 

Note that as mentioned earlier, directory names presented by using absolute path should be corrected before running it. And make sure all required files have already existed before proceeding to the next step. And finally, the order along which these Python files should be conducted is suggested by the order as listed above.