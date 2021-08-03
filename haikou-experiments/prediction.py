'''Check the data for prediction'''
import os
from basis.file import downloadMatchingRelationship
existing_datasets = os.path.exists("haikou-experiments/matching_relationship")
if existing_datasets == False:
    print("Downloading datasets...")
    print("If failed, you can download them from https://drive.google.com/file/d/1_6QaIi7Ot1aIne-_aXoutvmTkZjVouaI/view?usp=sharing")
    downloadMatchingRelationship()

'''import neccessary dependency'''
import scipy
import pandas as pd
import json
import time
import random
import math
import os
import datetime
import csv
from copy import deepcopy
import progressbar
from basis.schedule import Schedule
from basis.assistant import getID
from basis.setting import MAX_SEARCH_LAYERS,PERIODS,PLATFORM
from basis.setting import WAITING_TIME,SPEED,MINUTE,PERIODS_MINUTES
from basis.setting import CRITERION
from basis.edges import ALL_EDGES
from basis.vertexes import ALL_VERTEXES
from basis.neighbor import ALL_NEIGHBOR_EDGES


ALL_TAKERS, ALL_SEEKERS = {},{}
E = 2.718281828459045

class InteratedSolver(object):
    def __init__(self, max_OD_ID):
        self.HOUR_INDEX = 0 # study period
        self.MAX_ITERATE_TIMES = 10000
        self.max_OD_ID = max_OD_ID
        self.min_samples = 15 # ODs have less than 15 samples during the study period will be excluded
        self.tendency = 1 # proportion of passengers choose carpooling
        self.loadODDic()
        self.loadODs()
        self.loadSeekerTaker()

        self.initialVariables()
        self.interatedSolver()
        self.predictResults(final=True)
    
    def loadODs(self):
        lambda_df = pd.read_csv("haikou-experiments/network/combined_0.csv") # demand rates
        ODs_df = pd.read_csv("haikou-experiments/matching_relationship/ODs.csv") # OD
        self.all_ODs = {}
        bar = progressbar.ProgressBar(widgets=["ODs Loading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])        
        for j in bar(range(self.max_OD_ID)):
            if j >= lambda_df.shape[0]: break
            if lambda_df["days"][j] <= self.min_samples: break
            combined_id = getID(lambda_df["start_ver"][j],lambda_df["end_ver"][j])
            i = self.OD_dic[combined_id]["line_id"]
            self.all_ODs[ODs_df["id"][i]] = {
                "OD_id": ODs_df["id"][i],
                "start_ver": ODs_df["start_ver"][i],
                "end_ver": ODs_df["end_ver"][i],
                "num": lambda_df["num"][j],
                "taker_keys": json.loads(ODs_df["taker_keys"][i]),
                "seeker_keys": json.loads(ODs_df["seeker_keys"][i]),
                "lam_w": lambda_df["num"][j]*self.tendency/(PERIODS_MINUTES[self.HOUR_INDEX]*40)
            }

        print("#############Experiments Setting##############")
        print("Experiments Period: %02s:%02s  - %02s:%02s" % (PERIODS[self.HOUR_INDEX][0],PERIODS[self.HOUR_INDEX][1],PERIODS[self.HOUR_INDEX+1][0],PERIODS[self.HOUR_INDEX+1][1]))
        print("Search Distance: %s " % (MAX_SEARCH_LAYERS*500))
        print("MAX OD ID: %s" % self.max_OD_ID)
        print("Feasible OD: %s" % len(self.all_ODs))

    def loadSeekerTaker(self):
        self.ALL_SEEKERS = {}
        self.ALL_TAKERS = {}
        seekers_df = pd.read_csv("haikou-experiments/matching_relationship/seekers.csv")
        takers_df = pd.read_csv("haikou-experiments/matching_relationship/takers.csv")

        bar = progressbar.ProgressBar(widgets=["Seeker Loading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])        
        self.all_seeker_keys = []
        for i in bar(range(seekers_df.shape[0])):
            if seekers_df["OD_id"][i] not in self.all_ODs: continue
            self.ALL_SEEKERS[i] = {
                "seeker_id" : seekers_df["seeker_id"][i],
                "vertex_id" : seekers_df["vertex_id"][i],
                "OD_id" : seekers_df["OD_id"][i],
                "type" : seekers_df["type"][i],
                "sub_taker_key" : seekers_df["sub_taker_key"][i],
            }
            self.all_seeker_keys.append(i)
        self.all_seeker_num = len(self.all_seeker_keys)

        bar = progressbar.ProgressBar(widgets=["Taker Loading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])        
        self.all_taker_keys = []
        for i in bar(range(takers_df.shape[0])):
            if takers_df["OD_id"][i] not in self.all_ODs: continue
            original_matching_seekers = json.loads(takers_df["matching_seekers"][i])
            original_shared_distance = json.loads(takers_df["shared_distance"][i])
            original_detour = json.loads(takers_df["detour"][i])
            matching_seekers, all_shared_distance,all_detour = self.getFeasibleSeekers(original_matching_seekers,original_shared_distance,original_detour)
            self.ALL_TAKERS[i] = {
                "taker_id" : takers_df["taker_id"][i],
                "edge_id" : json.loads(takers_df["edge_id"][i]),
                "OD_id" : takers_df["OD_id"][i],
                "type" : takers_df["type"][i],
                "length" : takers_df["length"][i],
                "matching_seekers" : matching_seekers,
                "all_shared_distance" : all_shared_distance,
                "all_detour" : all_detour,
            }
            self.all_taker_keys.append(i)
        self.all_taker_num = len(self.all_taker_keys)
        for i in self.ALL_SEEKERS.keys():
            matching_takers, all_shared_distance, all_detour = self.getFeasibleTakers(json.loads(seekers_df["matching_takers"][i]),\
                json.loads(seekers_df["shared_distance"][i]),json.loads(seekers_df["detour"][i]))
            self.ALL_SEEKERS[i]["matching_takers"] = matching_takers
            self.ALL_SEEKERS[i]["all_shared_distance"] = all_shared_distance
            self.ALL_SEEKERS[i]["all_detour"] = all_detour

        print("Number of Takers: %s " % len(self.ALL_TAKERS))
        print("Number of Seekers: %s" % len(self.ALL_SEEKERS))

    def initialVariables(self):
        self.lam_seeker, self.P_seeker = {},{}
        for key in self.ALL_SEEKERS.keys():
            self.lam_seeker[key] = [random.random()/5,0] # demand rates of seekers
            self.P_seeker[key] = [random.random()/5,0] # matching probability of seekers

        self.lam_taker_arrive, self.eta_taker, self.eta_taker_seeker = {},{},{}
        self.P_taker, self.rho_taker = {},{}
        for key in self.ALL_TAKERS.keys():
            self.lam_taker_arrive[key] = [random.random()/5,0] # arrival rates of takers
            self.eta_taker[key] = [random.random()/5,0] # aggregate arrival rate of matching opportunities for takers 
            self.eta_taker_seeker[key] = {} # mean arrival rate of matching opportunities 
            macthing_num = len(self.ALL_TAKERS[key]["matching_seekers"])
            for seeker_key in self.ALL_TAKERS[key]["matching_seekers"]:
                self.eta_taker_seeker[key][seeker_key] = [random.random()/(macthing_num*5),random.random()/(macthing_num*5)] # 边上匹配机会的期望到达率（所有的点拆分）
            self.P_taker[key] = [random.random()/5,0] # matching probability of taker
            self.rho_taker[key] = [random.random()/5,0] # The probability of having at least one taker in state taker

        self.num_eta_st = self.getNumberEtaST()

    def interatedSolver(self):
        '''迭代求解全部变量'''
        self.iterate_time = 0
        change = 99999
        starttime = datetime.datetime.now()
        while self.iterate_time < self.MAX_ITERATE_TIMES and (change > 0.1 or self.iterate_time < 20):
            _cur,_last = 1 - self.iterate_time%2, self.iterate_time%2
            self.obtainLamST(_cur,_last)
            self.obtainEtaST(_cur,_last)
            self.obtainEtaTaker(_cur,_last)
            self.obtainPTaker(_cur,_last)
            self.obtainPSeeker(_cur,_last)
            
            all_change = [self.getRelativeChange(self.lam_taker_arrive),self.getRelativeChange(self.lam_seeker),self.getRelativeChange(self.eta_taker),self.getRelativeChange(self.P_taker),self.getRelativeChange(self.rho_taker),self.getRelativeChange(self.P_seeker)]
            change = max(all_change)
            print("iteration%s,%s,%s,%s,%s,%s,%s"%(self.iterate_time,all_change[0],all_change[1],all_change[2],all_change[3],all_change[4],all_change[5]))
            self.iterate_time = self.iterate_time + 1

        endtime = datetime.datetime.now()
        print("Iteration Times: %s" % self.iterate_time)
        print("Execution Time: %s second" % (endtime - starttime))

        fo = open("haikou-experiments/results/experiments_log.txt", "a+")
        fo.write("Study Period: %02s : %02s - %02s : %02s \n" % (PERIODS[self.HOUR_INDEX][0],PERIODS[self.HOUR_INDEX][1],PERIODS[self.HOUR_INDEX+1][0],PERIODS[self.HOUR_INDEX+1][1]))
        fo.write("Platform: %s \n" % PLATFORM)
        fo.write("Current Time: %s \n" % (time.asctime( time.localtime(time.time()))))
        fo.write("Search Distance: %s m\n" % (MAX_SEARCH_LAYERS*500))
        fo.write("Number of OD: %s 个\n" % len(self.all_ODs))
        fo.write("Node: %s \n" % len(self.ALL_SEEKERS))
        fo.write("Segment: %s \n" % len(self.ALL_TAKERS))
        fo.write("Number of Variables: %s\n" % (len(self.lam_seeker) + len(self.lam_taker_arrive) + self.num_eta_st + len(self.eta_taker) + len(self.P_taker) + len(self.rho_taker) + len(self.P_seeker)))
        fo.write("")
        fo.write("Ieration Times: %s\n" % self.iterate_time)
        fo.write("Ieration Time: %s second\n\n" % (endtime - starttime))
        fo.close()

    def obtainLamST(self,_cur,_last):
        '''Get the arrival rates of seeker/taker'''
        for i in range(len(self.all_seeker_keys)):
            seeker_key = self.all_seeker_keys[i]
            OD_id = self.ALL_SEEKERS[seeker_key]["OD_id"]
            if self.ALL_SEEKERS[seeker_key]["type"] == 1:
                self.lam_seeker[seeker_key][_cur] = self.all_ODs[OD_id]["lam_w"]
            else:
                last_seeker_key = self.all_seeker_keys[i-1]
                sub_taker_key = self.ALL_SEEKERS[last_seeker_key]["sub_taker_key"]
                self.lam_taker_arrive[sub_taker_key][_cur] = self.lam_seeker[last_seeker_key][_cur] * (1 - self.P_seeker[last_seeker_key][_last])
                self.lam_seeker[seeker_key][_cur] =self.lam_taker_arrive[sub_taker_key][_cur] * (1 - self.P_taker[sub_taker_key][_last])

    def obtainEtaST(self,_cur,_last):
        '''Get the arrival rate of matching opportunities'''
        for i in self.all_seeker_keys:
            if self.ALL_SEEKERS[i]["matching_takers"] == []: continue
            first_segment = self.ALL_SEEKERS[i]["matching_takers"][0]
            s_n = {first_segment : self.lam_seeker[i][_last]}
            self.eta_taker_seeker[first_segment][i][_cur] = self.lam_seeker[i][_last]
            for j in range(len(self.ALL_SEEKERS[i]["matching_takers"])-1):
                last_segment_key = self.ALL_SEEKERS[i]["matching_takers"][j]
                current_segment_key = self.ALL_SEEKERS[i]["matching_takers"][j+1]
                s_n[current_segment_key] = s_n[last_segment_key] * (1 - self.rho_taker[last_segment_key][_last])
                self.eta_taker_seeker[current_segment_key][i][_cur] = s_n[current_segment_key]

    def obtainEtaTaker(self,_cur,_last):
        '''Get the aggregate arrival rate of matching opportunities'''
        for i in self.all_taker_keys:
            self.eta_taker[i][_cur] = 0
            for j in self.ALL_TAKERS[i]["matching_seekers"]:
                self.eta_taker[i][_cur] = self.eta_taker[i][_cur] + self.eta_taker_seeker[i][j][_cur]

    def getNumberEtaST(self):
        '''获得某个变量的个数'''
        overall_num = 0
        for key in self.all_taker_keys:
            overall_num = overall_num + len(self.eta_taker_seeker[key])
        return overall_num

    def obtainPTaker(self,_cur,_last):
        '''Get the matching probability of taker and the probability of having at least one taker in state taker'''
        for i in self.all_taker_keys:
            t_s = WAITING_TIME
            if self.ALL_TAKERS[i]["type"] != 1:
                t_s = self.ALL_TAKERS[i]["length"]/SPEED + 0.5
            self.P_taker[i][_cur] = 1 - math.pow(E, -self.eta_taker[i][_last] * t_s)
            if self.eta_taker[i][_last] == 0:
                self.rho_taker[i][_cur] = t_s * self.lam_taker_arrive[i][_last]
            else:
                self.rho_taker[i][_cur] = (1 - math.pow(E, -self.eta_taker[i][_last] * t_s)) * self.lam_taker_arrive[i][_last]/self.eta_taker[i][_last]

    def obtainPSeeker(self,_cur,_last):
        '''Get the matching probability of seeker'''
        for i in self.all_seeker_keys:
            product = 1
            for taker_id in self.ALL_SEEKERS[i]["matching_takers"]:
                product = product * (1 - self.rho_taker[taker_id][_last])
            self.P_seeker[i][_cur] = 1 - product

    def getRelativeChange(self,all_dic):
        last_index = self.iterate_time%2
        overall_change = []
        for i in all_dic.keys():
            if all_dic[i][0] < 1e-4 and all_dic[i][1] == 1e-4: continue
            if all_dic[i][0] == 0 or all_dic[i][1] == 0: continue
            overall_change.append(abs(all_dic[i][0] - all_dic[i][1])/all_dic[i][last_index])
        return max(overall_change)

    def predictResults(self,final):
        index = self.iterate_time%2
        starttime = datetime.datetime.now()
        matching_probability = {}
        G_n,all_P_w = {},{}
        bar = progressbar.ProgressBar(widgets=[ 'Probability: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(self.all_ODs.keys()):
            start_seeker = self.all_ODs[i]["seeker_keys"][0]
            start_taker = self.ALL_SEEKERS[start_seeker]["sub_taker_key"]
            P_A_w = self.P_seeker[start_seeker][index]
            P_B_w = (1 - self.P_seeker[start_seeker][index]) * self.P_taker[start_taker][index]

            G_n[start_seeker] = 1
            last_seeker_key = start_seeker
            last_segment_key = self.ALL_SEEKERS[last_seeker_key]["sub_taker_key"]
            for j in self.all_ODs[i]["seeker_keys"][1:]:
                G_n[j] = G_n[last_seeker_key] * (1 - self.P_seeker[last_seeker_key][index]) * (1 - self.P_taker[last_segment_key][index])
                last_seeker_key,last_segment_key = j,self.ALL_SEEKERS[j]["sub_taker_key"]
            P_w = 1 - G_n[j]
            P_C_w = P_w - P_A_w - P_B_w
            matching_probability[i] = [P_w, P_A_w, P_B_w, P_C_w]
            all_P_w[i] = P_w

        # 预测拼车距离和共享距离
        all_l_w, all_e_w = {},{}
        bar = progressbar.ProgressBar(widgets=[ 'Distance: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(self.all_ODs.keys()):
            l_w_0 = Schedule.distanceByHistory(self.all_ODs[i]["start_ver"],self.all_ODs[i]["end_ver"])
            all_l_n_0, all_e_n_0 = [], []
            for seeker in self.all_ODs[i]["seeker_keys"]:
                if self.ALL_SEEKERS[seeker]["matching_takers"] != []:
                    l_n_0, e_n_0 = 0,0
                    overall_denominator = 0
                    for j in range(len(self.ALL_SEEKERS[seeker]["matching_takers"])):
                        matching_takers = self.ALL_SEEKERS[seeker]["matching_takers"][j]
                        detour = self.ALL_SEEKERS[seeker]["all_detour"][j]
                        shared_distance = self.ALL_SEEKERS[seeker]["all_shared_distance"][j]
                        l_n_s,e_n_s= l_w_0 + detour,shared_distance
                        
                        multiplier = self.eta_taker_seeker[matching_takers][seeker][index] * self.rho_taker[matching_takers][index]
                        overall_denominator = overall_denominator + multiplier
                        l_n_0, e_n_0 = l_n_0 + multiplier * l_n_s, e_n_0 + multiplier * e_n_s

                    all_l_n_0.append(l_n_0/overall_denominator), all_e_n_0.append(e_n_0/overall_denominator)
                else:
                    all_l_n_0.append(l_w_0), all_e_n_0.append(0)

            # 路段中的距离计算
            all_l_s_1, all_e_s_1 = [], []
            for taker in self.all_ODs[i]["taker_keys"]:
                l_s_1, e_s_1 = [],[]
                if self.ALL_TAKERS[taker]["matching_seekers"] != []:
                    l_s_1, e_s_1 = 0,0
                    for j in range(len(self.ALL_TAKERS[taker]["matching_seekers"])):
                        matching_seekers = self.ALL_TAKERS[taker]["matching_seekers"][j]
                        detour = self.ALL_TAKERS[taker]["all_detour"][j]
                        shared_distance = self.ALL_TAKERS[taker]["all_shared_distance"][j]
                        l_n_s, e_n_s = l_w_0 + detour, shared_distance
                        l_s_1 = l_s_1 + self.eta_taker_seeker[taker][matching_seekers][index] * l_n_s
                        e_s_1 = e_s_1 + self.eta_taker_seeker[taker][matching_seekers][index] * e_n_s
                    all_l_s_1.append(l_s_1/self.eta_taker[taker][index]), all_e_s_1.append(e_s_1/self.eta_taker[taker][index])
                else:
                    all_l_s_1.append(l_w_0), all_e_s_1.append(0)

            # 综合的期望值计算
            l_w = l_w_0 * (1 - all_P_w[i])
            e_w = 0
            for j in range(len(self.all_ODs[i]["seeker_keys"]) - 1):
                seeker_key = self.all_ODs[i]["seeker_keys"][j]
                segment_key = self.ALL_SEEKERS[seeker_key]["sub_taker_key"]
                l_w = l_w + all_l_n_0[j]*G_n[seeker_key]*self.P_seeker[seeker_key][index] + all_l_s_1[j]*G_n[seeker_key]*(1-self.P_seeker[seeker_key][index])*self.P_taker[segment_key][index]
                e_w = e_w + all_e_n_0[j]*G_n[seeker_key]*self.P_seeker[seeker_key][index] + all_e_s_1[j]*G_n[seeker_key]*(1-self.P_seeker[seeker_key][index])*self.P_taker[segment_key][index]
            all_l_w[i] = l_w
            all_e_w[i] = e_w
        endtime = datetime.datetime.now()
        print("Execution Time: %s second" % (endtime - starttime))

        fo = open("haikou-experiments/results/experiments_log.txt", "a+")
        fo.write("Execution Time: %s second\n\n" % (endtime - starttime))
        fo.close()

        with open("haikou-experiments/results/PREDICTION_OD_%s_PERIOD_%s_SAMPLE_%s_TENDENCY_%.2f.csv"%(self.max_OD_ID,self.HOUR_INDEX,self.min_samples,self.tendency),"w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["OD_id", "start_ver", "end_ver", "num", "P_w", "l_w", "e_w"])
            for i in self.all_ODs.keys():
                writer.writerow([self.all_ODs[i]["OD_id"], self.all_ODs[i]["start_ver"], self.all_ODs[i]["end_ver"],  self.all_ODs[i]["num"], all_P_w[i], all_l_w[i], all_e_w[i]])

    def getFeasibleSeekers(self,seekers,all_shared_distance,all_detour):
        new_seekers,new_shared_distance,new_detour = [],[],[]
        for i in range(len(seekers)):
            seeker,shared_distance,detour = seekers[i],all_shared_distance[i],all_detour[i]
            if seeker in self.ALL_SEEKERS:
                new_seekers.append(seeker)
                new_shared_distance.append(shared_distance)
                new_detour.append(detour)
        return new_seekers,new_shared_distance,new_detour

    def getFeasibleTakers(self,takers,all_shared_distance,all_detour):
        new_takers,new_shared_distance,new_detour = [],[],[]
        for i in range(len(takers)):
            taker,shared_distance,detour = takers[i],all_shared_distance[i],all_detour[i]
            if taker in self.ALL_TAKERS:
                new_takers.append(taker)
                new_shared_distance.append(shared_distance)
                new_detour.append(detour)
        return new_takers,new_shared_distance,new_detour

    def loadODDic(self):
        df = pd.read_csv("haikou-experiments/matching_relationship/ODs.csv")
        self.OD_dic = {}
        bar = progressbar.ProgressBar(widgets=["OD Dic Loading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])        
        for i in range(df.shape[0]):
            if i > self.max_OD_ID: break
            combined_id = getID(df["start_ver"][i],df["end_ver"][i])
            self.OD_dic[combined_id] = {
                "line_id": i,
                "start_ver": df["start_ver"][i],
                "end_ver": df["end_ver"][i]
            }

if __name__ == "__main__":
    max_OD_ID = 10000
    InteratedSolver(max_OD_ID)

