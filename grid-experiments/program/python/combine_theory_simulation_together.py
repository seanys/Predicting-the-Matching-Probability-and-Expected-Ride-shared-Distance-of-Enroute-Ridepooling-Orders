# -*- coding: utf-8 -*-
#this document is used to combine theory and simulation result together to generate
#some new files which is easy to analyze
import pandas as pd

filename_base_theory = 'D:\\document\\matching probability\\data\\version2\\theory\\'
filename_base_simulation = 'D:\\document\\matching probability\\data\\version2\\simulation_result\\'
filename_base_combine_theory_simulation = 'D:\\document\\matching probability\\data\\version2\\combined_theory_simulation\\'
column_names = ['seeker_probability', 'taker_waiting_probability', 'taker_traveling_probability', 'whole_matching_probability',
                       'traveling_distance', 'shared_distance', 'save_distance']
name_prefixes = ['theory_', 'simulation_']

pick_up_waiting_time_list = [1,2,4,6,8,10]
maximum_matching_radius_list = [0,1,2,4,6,8,10]
maximum_detour_time_list = [0,1,2,4,6,8,10]
scale_list = [1,0.5,0.1,0.06,0.04,0.02,0.01,0.001]

def get_theory_result_for_one_scenario(pi, ri, di, si):
    filename_extra_term = str(pi) + '_' + str(ri) + '_' + str(di) + '_' + str(si) + '.txt'
    filename = filename_base_theory + filename_extra_term
    df = pd.read_csv(filename, sep = '\t', skiprows = 2, names = column_names)
    return df

def get_simulation_result_for_one_scenario(pi, ri, di, si):
    filename_extra_term = str(pi) + '_' + str(ri) + '_' + str(di) + '_' + str(si) + '.csv'
    filename = filename_base_simulation + filename_extra_term
    df = pd.read_csv(filename, sep = ',')
    return df

def combine_theory_simulation_for_one_scenario(pi, ri, di, si):
    filename_extra_term = str(pi) + '_' + str(ri) + '_' + str(di) + '_' + str(si) + '.csv'
    
    df_theory = get_theory_result_for_one_scenario(pi, ri, di, si)
    df_simulation = get_simulation_result_for_one_scenario(pi, ri, di, si)
    
    new_column_names = []
    for column_name in column_names:
        for name_prefix in name_prefixes:        
            new_column_names.append(name_prefix + column_name)
    df_combine = pd.DataFrame(columns = new_column_names)
    for column_name in column_names:
        df_combine['theory_' + column_name] = df_theory[column_name]
        df_combine['simulation_' + column_name] = df_simulation[column_name]
    filename_combine = filename_base_combine_theory_simulation + filename_extra_term
    df_combine.to_csv(filename_combine, sep = ',', index = False)
    return df_combine

def combine_theory_simulation_for_all_scenarios():
    for pi in range(len(pick_up_waiting_time_list)):
        for ri in range(len(maximum_matching_radius_list)):
            for di in range(len(maximum_detour_time_list)):
                for si in range(len(scale_list)):
                    combine_theory_simulation_for_one_scenario(pi, ri, di, si)

if __name__ == "__main__":
    combine_theory_simulation_for_all_scenarios()
    #combine_theory_simulation_for_one_scenario(0, 2, 3, 2)