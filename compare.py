import pandas as pd
import csv
import progressbar
from basis.setting import PERIODS_MINUTES
from basis.assistant import getID
from assistant import Schedule
import json
from scipy import stats
from datetime import datetime

class CompareResults(object):
    def __init__(self):
        self.OD_num = 10000
        self.min_sample = 15
        self.tendency = 1
        self.compareResult()

    def compareResult(self):
        '''比较预测结果'''
        period_index = 0
        prediction_df = pd.read_csv("results/PREDICTION_OD_%s_PERIOD_0_SAMPLE_15_TENDENCY_1.00.csv" % (self.OD_num))
        all_P_w,all_l_w,all_e_w = {},{},{}
        for i in range(prediction_df.shape[0]):
            combined_id = getID(prediction_df["start_ver"][i],prediction_df["end_ver"][i])
            all_P_w[combined_id] = prediction_df["P_w"][i]
            all_l_w[combined_id] = prediction_df["l_w"][i]
            all_e_w[combined_id] = prediction_df["e_w"][i]

        output_path = "results/COMPARISON_SAMPLE_%s_TENDENCY_%.2f.csv" % (self.min_sample,self.tendency)
        with open(output_path,"w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["start_ver","end_ver","distance","lambda","original_num","original_days","num","days","P_w","l_w","e_w","matching_probability","aver_final_distance", \
                "aver_shared_distance","P_w_err","l_w_err","e_w_err","P_w_err_ratio","l_w_err_ratio","e_w_err_ratio"])

        ODs_df = pd.read_csv("network/combined_%s.csv"%(period_index))
        all_lambda = {}
        for i in range(ODs_df.shape[0]):
            if i >= ODs_df.shape[0]: break
            if ODs_df["start_ver"][i] == ODs_df["end_ver"][i]: continue
            if ODs_df["num"][i] == 0: break
            combined_id = getID(ODs_df["start_ver"][i],ODs_df["end_ver"][i])
            all_lambda[combined_id] = ODs_df["num"][i]/(PERIODS_MINUTES[period_index]*40)

        simulation_df = pd.read_csv("results/SIMULATION_STATISTIC.csv")
        for i in range(simulation_df.shape[0]):
            new_key = getID(simulation_df["start_ver"][i],simulation_df["end_ver"][i])
            if new_key in all_P_w:
                with open(output_path,"a") as csvfile:
                    writer = csv.writer(csvfile)
                    distance = Schedule.distanceByHistory(simulation_df["start_ver"][i], simulation_df["end_ver"][i])
                    l_w_err_ratio = abs(simulation_df["aver_final_distance%s"%period_index][i]-all_l_w[new_key])/simulation_df["aver_final_distance%s"%period_index][i]
                    if simulation_df["matching_probability%s"%period_index][i] > 0:
                        P_w_err_ratio = abs(simulation_df["matching_probability%s"%period_index][i]-all_P_w[new_key])/simulation_df["matching_probability%s"%period_index][i]
                        e_w_err_ratio = abs(simulation_df["aver_shared_distance%s"%period_index][i]-all_e_w[new_key])/simulation_df["aver_shared_distance%s"%period_index][i]
                    else:
                        P_w_err_ratio,e_w_err_ratio = 0,0
                    writer.writerow([simulation_df["start_ver"][i], simulation_df["end_ver"][i], distance, all_lambda[new_key], \
                        simulation_df["original_num"][i], simulation_df["original_days"][i], \
                        simulation_df["num%s"%period_index][i], simulation_df["days%s"%period_index][i], all_P_w[new_key], \
                        all_l_w[new_key], all_e_w[new_key],simulation_df["matching_probability%s"%period_index][i],simulation_df["aver_final_distance%s"%period_index][i], \
                        simulation_df["aver_shared_distance%s"%period_index][i], abs(simulation_df["matching_probability%s"%period_index][i]-all_P_w[new_key]), \
                        abs(simulation_df["aver_final_distance%s"%period_index][i]-all_l_w[new_key]), abs(simulation_df["aver_shared_distance%s"%period_index][i]-all_e_w[new_key]), \
                        P_w_err_ratio,l_w_err_ratio,e_w_err_ratio])

if __name__ == "__main__":
    CompareResults()
