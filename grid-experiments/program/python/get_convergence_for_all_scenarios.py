# -*- coding: utf-8 -*-
#this document is used to get all the convergent scenarios
import pandas as pd

filename_base_theory = 'D:\\document\\matching probability\\data\\version2\\theory\\'
filename_base_result = 'D:\\document\\matching probability\\data\\version2\\result\\'

pick_up_waiting_time = [1,2,4,6,8,10]
maximum_matching_radius = [0,1,2,4,6,8,10]
maximum_detour_time = [0,1,2,4,6,8,10]
scales = [1,0.5,0.1,0.06,0.04,0.02,0.01,0.001]

def get_convergence_result_for_one_scenario(pi, ri, di, si):
    extra_term = str(pi) + '_' + str(ri) + '_' + str(di) + '_' + str(si) + '.txt'
    filename = filename_base_theory + extra_term
    with open(filename) as f:
        first_line = f.readline()
        line_array = first_line.split('\t')
        flag_convergence = line_array[0]
        running_time = line_array[1]
        iteration_number = line_array[2]
    return flag_convergence, running_time, iteration_number

def get_convergence_result_for_all_scenarios():
    filename_out = filename_base_result + 'convergent_result.csv'
    convergent_scenario_number = 0
    column_names = ['pi', 'ri', 'di', 'si', 'flag_convergence', 'running_time', 'iteration_number']
    df_convergence = pd.DataFrame(columns = column_names)
    senario_index = 1
    for pi in range(len(pick_up_waiting_time)):
        for ri in range(len(maximum_matching_radius)):
            for di in range(len(maximum_detour_time)):
                for si in range(len(scales)):
                    flag_convergence, running_time, iteration_number = get_convergence_result_for_one_scenario(pi, ri, di, si)
                    
                    df_convergence.loc[senario_index, 'pi'] = pi
                    df_convergence.loc[senario_index, 'ri'] = ri
                    df_convergence.loc[senario_index, 'di'] = di
                    df_convergence.loc[senario_index, 'si'] = si
                    df_convergence.loc[senario_index, 'flag_convergence'] = flag_convergence
                    df_convergence.loc[senario_index, 'running_time'] = running_time
                    df_convergence.loc[senario_index, 'iteration_number'] = iteration_number
                    senario_index = senario_index + 1
                    if flag_convergence == 'true':
                        convergent_scenario_number = convergent_scenario_number + 1
    df_convergence.to_csv(filename_out, sep = ',', index = False)                 
    return df_convergence, convergent_scenario_number
                    
if __name__ == "__main__":
    df_convergence, convergent_scenario_number = get_convergence_result_for_all_scenarios()
    convergence_rate = convergent_scenario_number/len(df_convergence)
    print('whole case number: ' + str(len(df_convergence)))
    print('convergent case number: ' + str(convergent_scenario_number))
    print('convergence rate: ' + str(convergence_rate))