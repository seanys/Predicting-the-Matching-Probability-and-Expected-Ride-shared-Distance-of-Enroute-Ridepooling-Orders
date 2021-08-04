# -*- coding: utf-8 -*-
#this document is used to get the statistical data from the original simulation
#data

import pandas as pd

#parameter
filename_base = 'D:\\document\\matching probability\\data\\version2\\simulation\\'
output_filename_base = 'D:\\document\\matching probability\\data\\version2\\simulation_result\\'

total_iteration = 5

pick_up_time_list = [1,2,4,6,8,10]
maximum_matching_radius_list = [0,1,2,4,6,8,10]
maximum_detour_time_list = [0,1,2,4,6,8,10]
scale_list = [1,0.5,0.1,0.06,0.04,0.02,0.01,0.001]

column_names = ['total_num', 'seeker_num', 'taker_waiting_num', 'taker_traveling_num', 'leave_num', 'total_matched_num',
                    'traveling_distance',  'shared_distance', 'save_distance']

result_column_names = ['seeker_probability', 'taker_waiting_probability', 'taker_traveling_probability', 'whole_matching_probability',
                       'traveling_distance', 'shared_distance', 'save_distance']

#get simulation result of an iteration under one senario
def get_simulation_result_one_iteration_one_scenario(pi, ri, di, si, iteration):
    extra_name = str(pi) + '_' + str(ri) + '_' + str(di) + '_' + str(si) + '_' + str(iteration) + '.txt'
    filename = filename_base + extra_name
    df = pd.read_csv(filename, sep = '\t', skiprows = 1, names = column_names)
    return df

#get simulation result of one senario
def get_simulation_result_one_scenario(pi, ri, di, si):
    extra_name = str(pi) + '_' + str(ri) + '_' + str(di) + '_' + str(si) + '.csv'
    dfs = []
    for iteration in range(total_iteration):
        dfi = get_simulation_result_one_iteration_one_scenario(pi, ri, di, si, iteration)
        dfs.append(dfi)
    df = dfs[0]
    
    for iteration in range(1, total_iteration):
        dfi = dfs[iteration]
        for column_name in column_names:
            df[column_name] = df[column_name] + dfi[column_name]
    
    df['seeker_probability'] = df['seeker_num']/df['total_num']
    df['taker_waiting_probability'] = df['taker_waiting_num']/df['total_num']
    df['taker_traveling_probability'] = df['taker_traveling_num']/df['total_num']
    df['no_matching_probability'] = df['leave_num']/df['total_num']
    df['whole_matching_probability'] = 1 - df['no_matching_probability']
    df['traveling_distance'] = df['traveling_distance']/df['total_num']
    df['shared_distance'] = df['shared_distance']/df['total_num']
    df['save_distance'] = df['save_distance']/df['total_num']
    
    df_result = df[result_column_names]
    df_result.to_csv(output_filename_base + extra_name, sep = ',', index = False)
    
#get simulation result for all scenarios
def get_simulation_result_for_all_scenarios():
    for pi in range(len(pick_up_time_list)):
        for ri in range(len(maximum_matching_radius_list)):
            for di in range(len(maximum_detour_time_list)):
                for si in range(len(scale_list)):
                    get_simulation_result_one_scenario(pi, ri, di, si)

if __name__ == "__main__":
    get_simulation_result_for_all_scenarios()
    #get_simulation_result_one_scenario(0, 2, 3, 2)
    