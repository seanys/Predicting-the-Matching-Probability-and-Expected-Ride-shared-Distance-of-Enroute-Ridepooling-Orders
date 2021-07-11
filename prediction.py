'''Check the data for prediction'''
import os
from basis.file import downloadMatchingRelationship
existing_datasets = os.path.exists("matching_relationship")
if existing_datasets == False:
    print("Downloading datasets...")
    print("If failed, you can download them from https://drive.google.com/file/d/1_6QaIi7Ot1aIne-_aXoutvmTkZjVouaI/view?usp=sharing")
    downloadDatasets()

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
from assistant import Schedule,getID
from basis.setting import MAX_SEARCH_LAYERS,PERIODS,PLATFORM
from basis.setting import WAITING_TIME,SPEED,MINUTE,PERIODS_MINUTES
from basis.setting import CRITERION
from basis.edges import ALL_EDGES
from basis.vertexes import ALL_VERTEXES
from basis.neighbor import ALL_NEIGHBOR_EDGES


ALL_SEGMENTS, ALL_NODES = {},{}
E = 2.718281828459045

class InteratedSolver(object):
    def __init__(self, tendency):
        self.HOUR_INDEX = 0
        self.MAX_ITERATE_TIMES = 10000
        self.max_OD_ID = 100
        self.min_samples = 15
        self.tendency = tendency
        self.loadODDic()
        self.loadODs()
        self.loadNodeSegment()

        self.initialVariables()
        self.interatedSolver()
        self.predictResults(final=True)
    
    def loadODs(self):
        lambda_df = pd.read_csv("network/combined_0.csv")
        ODs_df = pd.read_csv("matching_relationship/ODs_layers_3.csv")
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
                "segments_keys": json.loads(ODs_df["segments_keys"][i]),
                "nodes_keys": json.loads(ODs_df["nodes_keys"][i]),
                "lam_w": lambda_df["num"][j]*self.tendency/(PERIODS_MINUTES[self.HOUR_INDEX]*40)
            }

        print("#############Experiments Setting##############")
        print("Experiments Period: %02s:%02s  - %02s:%02s" % (PERIODS[self.HOUR_INDEX][0],PERIODS[self.HOUR_INDEX][1],PERIODS[self.HOUR_INDEX+1][0],PERIODS[self.HOUR_INDEX+1][1]))
        print("Search Distance: %s " % MAX_SEARCH_LAYERS*500)
        print("MAX OD ID: %s" % self.max_OD_ID)
        print("Feasible OD: %s" % len(self.all_ODs))

    def loadNodeSegment(self):
        self.ALL_SEGMENTS = {}
        self.ALL_NODES = {}
        nodes_df = pd.read_csv("matching_relationship/nodes_layers_3.csv")
        segments_df = pd.read_csv("matching_relationship/segments_layers_3.csv")
        bar = progressbar.ProgressBar(widgets=["Node Loading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])        
        self.all_node_keys = []
        for i in bar(range(nodes_df.shape[0])):
            if nodes_df["OD_id"][i] not in self.all_ODs: continue
            self.ALL_NODES[i] = {
                "node_id" : nodes_df["node_id"][i],
                "vertex_id" : nodes_df["vertex_id"][i],
                "OD_id" : nodes_df["OD_id"][i],
                "type" : nodes_df["type"][i],
                "sub_segment_key" : nodes_df["sub_segment_key"][i],
            }
            self.all_node_keys.append(i)
        self.all_node_num = len(self.all_node_keys)
        bar = progressbar.ProgressBar(widgets=["Segment Loading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])        
        self.all_segment_keys = []
        for i in bar(range(segments_df.shape[0])):
            if segments_df["OD_id"][i] not in self.all_ODs: continue
            original_matching_nodes = json.loads(segments_df["matching_nodes"][i])
            original_shared_distance = json.loads(segments_df["shared_distance"][i])
            original_detour = json.loads(segments_df["detour"][i])
            matching_nodes, all_shared_distance,all_detour = self.getFeasibleNodes(original_matching_nodes,original_shared_distance,original_detour)
            self.ALL_SEGMENTS[i] = {
                "segment_id" : segments_df["segment_id"][i],
                "edge_id" : json.loads(segments_df["edge_id"][i]),
                "OD_id" : segments_df["OD_id"][i],
                "type" : segments_df["type"][i],
                "length" : segments_df["length"][i],
                "matching_nodes" : matching_nodes,
                "all_shared_distance" : all_shared_distance,
                "all_detour" : all_detour,
            }
            self.all_segment_keys.append(i)
        self.all_segment_num = len(self.all_segment_keys)
        for i in self.ALL_NODES.keys():
            matching_segments, all_shared_distance, all_detour = self.getFeasibleSegments(json.loads(nodes_df["matching_segments"][i]),\
                json.loads(nodes_df["shared_distance"][i]),json.loads(nodes_df["detour"][i]))
            self.ALL_NODES[i]["matching_segments"] = matching_segments
            self.ALL_NODES[i]["all_shared_distance"] = all_shared_distance
            self.ALL_NODES[i]["all_detour"] = all_detour

        print("Number of Segments: %s " % len(self.ALL_SEGMENTS))
        print("Number of Node: %s" % len(self.ALL_NODES))

    def initialVariables(self):
        self.lam_n_a, self.P_n_0 = {},{}
        for key in self.ALL_NODES.keys():
            self.lam_n_a[key] = [random.random()/5,0] # 到达点的状态（所有的顶点）
            self.P_n_0[key] = [random.random()/5,0] # 在点的匹配概率（所有顶点）

        self.lam_s_d, self.lam_s, self.lam_s_n = {},{},{}
        self.P_s_1, self.P_s_e = {},{}
        for key in self.ALL_SEGMENTS.keys():
            self.lam_s_d[key] = [random.random()/5,0] # n的点进入路段的为匹配比率（所有的路段/顶点下一条边）
            self.lam_s[key] = [random.random()/5,0] # 边上匹配机会的期望到达率（合并）
            self.lam_s_n[key] = {}
            macthing_num = len(self.ALL_SEGMENTS[key]["matching_nodes"])
            for node_key in self.ALL_SEGMENTS[key]["matching_nodes"]:
                self.lam_s_n[key][node_key] = [random.random()/(macthing_num*5),random.random()/(macthing_num*5)] # 边上匹配机会的期望到达率（所有的点拆分）
            self.P_s_1[key] = [random.random()/5,0] # 在路段上t时间的匹配概率（所有路段）
            self.P_s_e[key] = [random.random()/5,0] # 乘客在路段上未匹配概率（所有路段）

        self.num_lam_s_n = self.getNumberLamSN()

    def interatedSolver(self):
        '''迭代求解全部变量'''
        self.iterate_time = 0
        change = 99999
        starttime = datetime.datetime.now()
        while self.iterate_time < self.MAX_ITERATE_TIMES and (change > 0.1 or self.iterate_time < 20):
            _cur,_last = 1 - self.iterate_time%2, self.iterate_time%2
            self.obtainLamSDNA(_cur,_last)
            self.obtainLamSN(_cur,_last)
            self.obtainLamS(_cur,_last)
            self.obtainPS(_cur,_last)
            self.obtainPN(_cur,_last)
            
            all_change = [self.getRelativeChange(self.lam_s_d),self.getRelativeChange(self.lam_n_a),self.getRelativeChange(self.lam_s),self.getRelativeChange(self.P_s_1),self.getRelativeChange(self.P_s_e),self.getRelativeChange(self.P_n_0)]
            change = max(all_change)
            print("%s,%s,%s,%s,%s,%s,%s"%(self.iterate_time,all_change[0],all_change[1],all_change[2],all_change[3],all_change[4],all_change[5]))
            self.iterate_time = self.iterate_time + 1

        endtime = datetime.datetime.now()
        print("Iteration Times: %s" % self.iterate_time)
        print("Execution Time: %s second" % (endtime - starttime))

        fo = open("results/experiments_log.txt", "a+")
        fo.write("Study Period: %s 点 %s 分 - %s 点 %s 分 \n" % (PERIODS[self.HOUR_INDEX][0],PERIODS[self.HOUR_INDEX][1],PERIODS[self.HOUR_INDEX+1][0],PERIODS[self.HOUR_INDEX+1][1]))
        fo.write("Platform: %s \n" % PLATFORM)
        fo.write("Current Time: %s \n" % (time.asctime( time.localtime(time.time()))))
        fo.write("Search Distance: %s m\n" % MAX_SEARCH_LAYERS*500)
        fo.write("Num of OD: %s 个\n" % self.max_OD_ID)
        fo.write("可行OD数目: %s 个\n" % len(self.all_ODs))
        fo.write("Node: %s \n" % len(self.ALL_NODES))
        fo.write("Segment: %s \n" % len(self.ALL_SEGMENTS))
        fo.write("Number of Variables: %s\n" % (len(self.lam_n_a) + len(self.lam_s_d) + self.num_lam_s_n + len(self.lam_s) + len(self.P_s_1) + len(self.P_s_e) + len(self.P_n_0)))
        fo.write("")
        fo.write("Ieration Times: %s\n" % self.iterate_time)
        fo.write("Execution Time: %s second\n\n" % (endtime - starttime))
        fo.close()

    def obtainLamSDNA(self,_cur,_last):
        for i in range(len(self.all_node_keys)):
            node_key = self.all_node_keys[i]
            OD_id = self.ALL_NODES[node_key]["OD_id"]
            if self.ALL_NODES[node_key]["type"] == 1:
                self.lam_n_a[node_key][_cur] = self.all_ODs[OD_id]["lam_w"]
            else:
                last_node_key = self.all_node_keys[i-1]
                sub_segment_key = self.ALL_NODES[last_node_key]["sub_segment_key"]
                self.lam_s_d[sub_segment_key][_cur] = self.lam_n_a[last_node_key][_cur] * (1 - self.P_n_0[last_node_key][_last])
                self.lam_n_a[node_key][_cur] =self.lam_s_d[sub_segment_key][_cur] * (1 - self.P_s_1[sub_segment_key][_last])

    def obtainLamSN(self,_cur,_last):
        for i in self.all_node_keys:
            if self.ALL_NODES[i]["matching_segments"] == []: continue
            first_segment = self.ALL_NODES[i]["matching_segments"][0]
            s_n = {first_segment : self.lam_n_a[i][_last]}
            self.lam_s_n[first_segment][i][_cur] = self.lam_n_a[i][_last]
            for j in range(len(self.ALL_NODES[i]["matching_segments"])-1):
                last_segment_key = self.ALL_NODES[i]["matching_segments"][j]
                current_segment_key = self.ALL_NODES[i]["matching_segments"][j+1]
                s_n[current_segment_key] = s_n[last_segment_key] * (1 - self.P_s_e[last_segment_key][_last])
                self.lam_s_n[current_segment_key][i][_cur] = s_n[current_segment_key]

    def obtainLamS(self,_cur,_last):
        for i in self.all_segment_keys:
            self.lam_s[i][_cur] = 0
            for j in self.ALL_SEGMENTS[i]["matching_nodes"]:
                self.lam_s[i][_cur] = self.lam_s[i][_cur] + self.lam_s_n[i][j][_cur]

    def obtainPS(self,_cur,_last):
        for i in self.all_segment_keys:
            t_s = WAITING_TIME
            if self.ALL_SEGMENTS[i]["type"] != 1:
                t_s = self.ALL_SEGMENTS[i]["length"]/SPEED + 0.5
            self.P_s_1[i][_cur] = 1 - math.pow(E, -self.lam_s[i][_last] * t_s)
            if self.lam_s[i][_last] == 0:
                self.P_s_e[i][_cur] = t_s * self.lam_s_d[i][_last]
            else:
                self.P_s_e[i][_cur] = (1 - math.pow(E, -self.lam_s[i][_last] * t_s)) * self.lam_s_d[i][_last]/self.lam_s[i][_last]

    def obtainPN(self,_cur,_last):
        for i in self.all_node_keys:
            product = 1
            for segment_id in self.ALL_NODES[i]["matching_segments"]:
                product = product * (1 - self.P_s_e[segment_id][_last])
            self.P_n_0[i][_cur] = 1 - product

    def getNumberLamSN(self):
        '''获得某个变量的个数'''
        overall_num = 0
        for key in self.all_segment_keys:
            overall_num = overall_num + len(self.lam_s_n[key])
        return overall_num

    def getRelativeChange(self,all_dic):
        '''获得差值'''
        last_index = self.iterate_time%2
        overall_change = []
        for i in all_dic.keys():
            if all_dic[i][0] < 1e-4 and all_dic[i][1] == 1e-4: continue
            if all_dic[i][0] == 0 or all_dic[i][1] == 0: continue
            overall_change.append(abs(all_dic[i][0] - all_dic[i][1])/all_dic[i][last_index])
        return max(overall_change)

    def predictResults(self,final):
        '''计算预测结果'''
        index = self.iterate_time%2
        starttime = datetime.datetime.now()
        matching_probability = {}
        G_n,all_P_w = {},{}
        bar = progressbar.ProgressBar(widgets=[ 'Probability: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(self.all_ODs.keys()):
            start_node = self.all_ODs[i]["nodes_keys"][0]
            start_segment = self.ALL_NODES[start_node]["sub_segment_key"]
            P_A_w = self.P_n_0[start_node][index]
            P_B_w = (1 - self.P_n_0[start_node][index]) * self.P_s_1[start_segment][index]

            G_n[start_node] = 1
            last_node_key = start_node
            last_segment_key = self.ALL_NODES[last_node_key]["sub_segment_key"]
            for j in self.all_ODs[i]["nodes_keys"][1:]:
                G_n[j] = G_n[last_node_key] * (1 - self.P_n_0[last_node_key][index]) * (1 - self.P_s_1[last_segment_key][index])
                last_node_key,last_segment_key = j,self.ALL_NODES[j]["sub_segment_key"]
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
            for node in self.all_ODs[i]["nodes_keys"]:
                if self.ALL_NODES[node]["matching_segments"] != []:
                    l_n_0, e_n_0 = 0,0
                    overall_denominator = 0
                    for j in range(len(self.ALL_NODES[node]["matching_segments"])):
                        matching_seg = self.ALL_NODES[node]["matching_segments"][j]
                        detour = self.ALL_NODES[node]["all_detour"][j]
                        shared_distance = self.ALL_NODES[node]["all_shared_distance"][j]
                        l_n_s,e_n_s= l_w_0 + detour,shared_distance
                        
                        multiplier = self.lam_s_n[matching_seg][node][index] * self.P_s_e[matching_seg][index]
                        overall_denominator = overall_denominator + multiplier
                        l_n_0, e_n_0 = l_n_0 + multiplier * l_n_s, e_n_0 + multiplier * e_n_s

                    all_l_n_0.append(l_n_0/overall_denominator), all_e_n_0.append(e_n_0/overall_denominator)
                else:
                    all_l_n_0.append(l_w_0), all_e_n_0.append(0)

            # 路段中的距离计算
            all_l_s_1, all_e_s_1 = [], []
            for seg in self.all_ODs[i]["segments_keys"]:
                l_s_1, e_s_1 = [],[]
                if self.ALL_SEGMENTS[seg]["matching_nodes"] != []:
                    l_s_1, e_s_1 = 0,0
                    for j in range(len(self.ALL_SEGMENTS[seg]["matching_nodes"])):
                        matching_node = self.ALL_SEGMENTS[seg]["matching_nodes"][j]
                        detour = self.ALL_SEGMENTS[seg]["all_detour"][j]
                        shared_distance = self.ALL_SEGMENTS[seg]["all_shared_distance"][j]
                        l_n_s, e_n_s = l_w_0 + detour, shared_distance
                        l_s_1 = l_s_1 + self.lam_s_n[seg][matching_node][index] * l_n_s
                        e_s_1 = e_s_1 + self.lam_s_n[seg][matching_node][index] * e_n_s
                    all_l_s_1.append(l_s_1/self.lam_s[seg][index]), all_e_s_1.append(e_s_1/self.lam_s[seg][index])
                else:
                    all_l_s_1.append(l_w_0), all_e_s_1.append(0)

            # 综合的期望值计算
            l_w = l_w_0 * (1 - all_P_w[i])
            e_w = 0
            for j in range(len(self.all_ODs[i]["nodes_keys"]) - 1):
                node_key = self.all_ODs[i]["nodes_keys"][j]
                segment_key = self.ALL_NODES[node_key]["sub_segment_key"]
                l_w = l_w + all_l_n_0[j]*G_n[node_key]*self.P_n_0[node_key][index] + all_l_s_1[j]*G_n[node_key]*(1-self.P_n_0[node_key][index])*self.P_s_1[segment_key][index]
                e_w = e_w + all_e_n_0[j]*G_n[node_key]*self.P_n_0[node_key][index] + all_e_s_1[j]*G_n[node_key]*(1-self.P_n_0[node_key][index])*self.P_s_1[segment_key][index]
            all_l_w[i] = l_w
            all_e_w[i] = e_w
        endtime = datetime.datetime.now()
        print("Execution Time: %s second" % (endtime - starttime))

        fo = open("results/experiments_log.txt", "a+")
        fo.write("Execution Time: %s second\n\n" % (endtime - starttime))
        fo.close()

        with open("results/OD_%s_PERIOD_%s_SAMPLE_%s_PRE_%.2f.csv"%(self.max_OD_ID,self.HOUR_INDEX,self.min_samples,self.tendency),"w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["OD_id", "start_ver", "end_ver", "num", "P_w", "l_w", "e_w"])
            for i in self.all_ODs.keys():
                writer.writerow([self.all_ODs[i]["OD_id"], self.all_ODs[i]["start_ver"], self.all_ODs[i]["end_ver"],  self.all_ODs[i]["num"], all_P_w[i], all_l_w[i], all_e_w[i]])

    def getFeasibleNodes(self,nodes,all_shared_distance,all_detour):
        new_nodes,new_shared_distance,new_detour = [],[],[]
        for i in range(len(nodes)):
            node,shared_distance,detour = nodes[i],all_shared_distance[i],all_detour[i]
            if node in self.ALL_NODES:
                new_nodes.append(node)
                new_shared_distance.append(shared_distance)
                new_detour.append(detour)
        return new_nodes,new_shared_distance,new_detour

    def getFeasibleSegments(self,segments,all_shared_distance,all_detour):
        new_segments,new_shared_distance,new_detour = [],[],[]
        for i in range(len(segments)):
            segment,shared_distance,detour = segments[i],all_shared_distance[i],all_detour[i]
            if segment in self.ALL_SEGMENTS:
                new_segments.append(segment)
                new_shared_distance.append(shared_distance)
                new_detour.append(detour)
        return new_segments,new_shared_distance,new_detour

    def loadODDic(self):
        df = pd.read_csv("matching_relationship/ODs_layers_3.csv")
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
    InteratedSolver(1)

