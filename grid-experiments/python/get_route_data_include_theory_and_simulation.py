# -*- coding: utf-8 -*-
#this document is used to collect all data belong to one single route, and put
#the information into one file
import pandas as pd
pick_up_waiting_time = [1,2,4,6,8,10]
maximum_matching_radius = [0,1,2,4,6,8,10]
maximum_detour_time = [0,1,2,4,6,8,10]
scales = [1,0.5,0.1,0.06,0.04,0.02,0.01,0.001]

filename_base_combine_theory_simulation = 'D:\\document\\matching probability\\data\\version2\\combined_theory_simulation\\'
filename_convergent_result = 'D:\\document\\matching probability\\data\\version2\\result\\convergent_result.csv'
filename_base_route = 'D:\\document\\matching probability\\data\\version2\\route\\'

def get_route_information_from_one_scenario(df, pi, ri, di, si, od_index):
    filename_extra_term = str(pi) + '_' + str(ri) + '_' + str(di) + '_' + str(si) + '.csv'
    filename = filename_base_combine_theory_simulation + filename_extra_term
    df_senario = pd.read_csv(filename, sep = ',')
    column_names = df.columns
    df_len = len(df)
    for column_name in column_names:
        df.loc[df_len, column_name] = df_senario.loc[od_index, column_name]
    return df

def get_column_names():
    filename_extra_term = '0_0_0_0.csv'
    filename = filename_base_combine_theory_simulation + filename_extra_term
    df_0 = pd.read_csv(filename, sep = ',')
    column_names = df_0.columns
    return column_names

def get_convergence_dataframe():
    df_convergent = pd.read_csv(filename_convergent_result)
    return df_convergent

def get_route_information_from_all_scenarios(od_index):
    column_names = get_column_names()
    df_od = pd.DataFrame(columns = column_names)
    
    df_convergent = get_convergence_dataframe()    
    for pi in range(len(pick_up_waiting_time)):
        for ri in range(len(maximum_matching_radius)):
            for di in range(len(maximum_detour_time)):
                for si in range(len(scales)):    
                    df_temp = df_convergent.loc[(df_convergent['pi'] == pi) & 
                                                (df_convergent['ri'] == ri) & 
                                                (df_convergent['di'] == di) & 
                                                (df_convergent['si'] == si)]
                    flag_convergence = df_temp['flag_convergence'].tolist()[0]
                    if flag_convergence == True:
                        df_od = get_route_information_from_one_scenario(df_od, pi, ri, di, si, od_index)
    filename = filename_base_route + str(od_index) + '.csv'
    df_od.to_csv(filename, sep = ',', index = False)
    return

if __name__ == "__main__":
    for od_index in range(300):
        get_route_information_from_all_scenarios(od_index)
    
    