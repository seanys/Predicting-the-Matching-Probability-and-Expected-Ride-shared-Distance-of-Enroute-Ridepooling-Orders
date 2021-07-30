# -*- coding: utf-8 -*-
#this document is used to obtain the absolute and relative error of each key performance
#indicators corresponding to a specific od, and get some key performance indicators of the
#whole model
import pandas as pd
import math

filename_base_route = 'D:\\document\\matching probability\\data\\version2\\route\\'
filename_base_route_error = 'D:\\document\\matching probability\\data\\version2\\route_error\\'
filename_base_result = 'D:\\document\\matching probability\\data\\version2\\result\\'

column_names = ['seeker_probability', 'taker_waiting_probability', 'taker_traveling_probability', 'whole_matching_probability',
                       'traveling_distance', 'shared_distance', 'save_distance']
name_prefixes = ['theory_', 'simulation_']
error_prefixes = ['absolute_', 'relative_']

#obtain absolute and relative error for each od
def get_absolute_and_relative_error_for_each_od(od_index):
    filename = filename_base_route + str(od_index) + '.csv'
    df_od = pd.read_csv(filename, sep = ',')
    
    for column_name in column_names:
        df_od['temp'] = df_od['theory_' + column_name] - df_od['simulation_' + column_name]
        df_od['absolute_' + column_name] = df_od['temp'].map(lambda x : abs(x))
    
        df_od['relative_' + column_name] = df_od['absolute_' + column_name]/df_od['simulation_' + column_name]
        df_od['relative_' + column_name] = df_od['relative_' + column_name].map(lambda x : 0 if x > 10000 else x)
    
    filename_error = filename_base_route_error + str(od_index) + '.csv'
    df_od.to_csv(filename_error, sep = ',', index = False)
    return df_od

#obtain the key performance indicators for each od
def get_key_performance_indicators_for_each_od(df, od_index):
    column_names_method = ['whole_matching_probability', 'shared_distance', 'save_distance', 'traveling_distance']
    df_od = get_absolute_and_relative_error_for_each_od(od_index)
    #filename_error = filename_base_route_error + str(od_index) + '.csv'
    #df_od = pd.read_csv(filename_error, sep = ',')
    convergent_senario_number = len(df_od)
    for column_name_temp in column_names_method:
        df_od['temp'] = df_od['absolute_' + column_name_temp].map(lambda x : x * x)
        sum_temp = sum(df_od['temp'].values.tolist())
        df.loc[od_index, 'rmse_' + column_name_temp] = math.sqrt(sum_temp/convergent_senario_number)
        
        sum_temp_mape = sum(df_od['relative_' + column_name_temp].values.tolist())
        df.loc[od_index, 'mape_' + column_name_temp] = 100 * sum_temp_mape/convergent_senario_number
    return df

def get_key_performance_indicators_for_all_ods():
    extra_term = 'rmse_mape.csv'
    column_names_method = ['whole_matching_probability', 'shared_distance', 'save_distance', 'traveling_distance']
    prefixes = ['rmse_', 'mape_']
    columns = []
    for column_name in column_names_method:
        for prefix in prefixes:
            columns.append(prefix + column_name)
    df_result = pd.DataFrame(columns = columns)
    for od_index in range(300):
        df_result = get_key_performance_indicators_for_each_od(df_result, od_index)
    filename = filename_base_result + extra_term
    df_result.to_csv(filename, sep = ',', index = False)

if __name__ == "__main__":
    get_key_performance_indicators_for_all_ods()
    