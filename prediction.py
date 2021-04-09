'''
根据网络和需求的变量求解每个OD Pair的期望（拼车）距离、期望拼车概率，
然后与实际的统计结果进行比较
'''
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
# import numba as nb
import progressbar
import cProfile
from assistant import Schedule,getID
from basis.setting import MAX_SEARCH_LAYERS,DATA_PATH,PERIODS,PLATFORM
from basis.setting import WAITING_TIME,SPEED,MINUTE,PERIODS_MINUTES
from basis.setting import CRITERION
from basis.edges import ALL_EDGES
from basis.vertexes import ALL_VERTEXES
from basis.neighbor import ALL_NEIGHBOR_EDGES
from assistant import PreProcessData


ALL_SEGMENTS, ALL_NODES = {},{}
E = 2.718281828459045

class InteratedSolver(object):
    def __init__(self, tendency):
        '''处理预测模型'''
        self.HOUR_INDEX = 0
        self.MAX_ITERATE_TIMES = 10000
        self.max_OD_ID = 100
        self.min_samples = 15
        self.tendency = tendency
        self.export_by_period = -1
        self.loadODDic()
        self.loadODs()
        self.loadNodeSegment()

        self.initialVariables()
        self.interatedSolver()
        # self.exportVariables()
        # self.loadVariables()
        self.predictResults(final=True)
    
    def loadODs(self):
        '''加载全部的OD以及匹配情况'''
        lambda_df = pd.read_csv("Simulation/data/ods/combined_%s.csv" % self.HOUR_INDEX)
        # lambda_df = pd.read_csv("Simulation/data/ods/ODs_prestore.csv")
        ODs_df = pd.read_csv("%s/prestore/ODs_layers_3.csv" % DATA_PATH)
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

        print("#############预测模型配置##############")
        print("实验时间: %s 点 %s 分 - %s 点 %s 分" % (PERIODS[self.HOUR_INDEX][0],PERIODS[self.HOUR_INDEX][1],PERIODS[self.HOUR_INDEX+1][0],PERIODS[self.HOUR_INDEX+1][1]))
        print("最大检索层数: %s 层" % MAX_SEARCH_LAYERS)
        print("最大OD ID: %s" % self.max_OD_ID)
        print("可行OD数目: %s 个" % len(self.all_ODs))

    def loadNodeSegment(self):
        self.ALL_SEGMENTS = {}
        self.ALL_NODES = {}
        nodes_df = pd.read_csv("%s/prestore/nodes_layers_3.csv"%(DATA_PATH))
        segments_df = pd.read_csv("%s/prestore/segments_layers_3.csv"%(DATA_PATH))
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

        print("Segment数目: %s 个" % len(self.ALL_SEGMENTS))
        print("Node数目: %s 个" % len(self.ALL_NODES))

    def initialVariables(self):
        '''初始化全部变量'''
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
        print("lam_n_a,P_n_0的变量个数:",len(self.lam_n_a))
        print("lam_s,lam_s_d,P_s_1,P_s_e的变量个数:",len(self.lam_s))
        print("lam_s_n的变量个数:",self.num_lam_s_n)
        print("变量共计:",len(self.lam_n_a) + len(self.lam_s_d) + self.num_lam_s_n + len(self.lam_s) + len(self.P_s_1) + len(self.P_s_e) + len(self.P_n_0))

    def interatedSolver(self):
        '''迭代求解全部变量'''
        self.iterate_time = 0
        change = 99999
        starttime = datetime.datetime.now()
        # re_lam_s_d,re_lam_n_a,re_lam_s,re_P_s_1,re_P_s_e,re_P_n_0 = [],[],[],[],[],[]
        # ab_lam_s_d,ab_lam_n_a,ab_lam_s,ab_P_s_1,ab_P_s_e,ab_P_n_0 = [],[],[],[],[],[]
        # while self.iterate_time < MAX_ITERATE_TIMES and (change > 0.02 or self.iterate_time < 20):
        while self.iterate_time < self.MAX_ITERATE_TIMES and (change > 0.1 or self.iterate_time < 20):
            _cur,_last = 1 - self.iterate_time%2, self.iterate_time%2
            # print("第%s轮"%(self.iterate_time))
            self.obtainLamSDNA(_cur,_last)
            self.obtainLamSN(_cur,_last)
            self.obtainLamS(_cur,_last)
            self.obtainPS(_cur,_last)
            self.obtainPN(_cur,_last)
            
            all_change = [self.getRelativeChange(self.lam_s_d),self.getRelativeChange(self.lam_n_a),self.getRelativeChange(self.lam_s),self.getRelativeChange(self.P_s_1),self.getRelativeChange(self.P_s_e),self.getRelativeChange(self.P_n_0)]
            change = max(all_change)
            print("%s,%s,%s,%s,%s,%s,%s"%(self.iterate_time,all_change[0],all_change[1],all_change[2],all_change[3],all_change[4],all_change[5]))
            # re_lam_s_d.append(self.getRelativeChange(self.lam_s_d)),re_lam_n_a.append(self.getRelativeChange(self.lam_n_a)),re_lam_s.append(self.getRelativeChange(self.lam_s)),re_P_s_1.append(self.getRelativeChange(self.P_s_1)),re_P_s_e.append(self.getRelativeChange(self.P_s_e)),re_P_n_0.append(self.getRelativeChange(self.P_n_0))
            # ab_lam_s_d.append(self.getChange(self.lam_s_d)),ab_lam_n_a.append(self.getChange(self.lam_n_a)),ab_lam_s.append(self.getChange(self.lam_s)),ab_P_s_1.append(self.getChange(self.P_s_1)),ab_P_s_e.append(self.getChange(self.P_s_e)),ab_P_n_0.append(self.getChange(self.P_n_0))
            # print(("Change %s,lam_s_d:%s,lam_n_a:%s,lam_s:%s,P_s_1:%s,P_s_e:%s,P_n_0:%s")%(self.iterate_time,self.getChange(self.lam_s_d),self.getChange(self.lam_n_a),self.getChange(self.lam_s),self.getChange(self.P_s_1),self.getChange(self.P_s_e),self.getChange(self.P_n_0)))
            # print(("Relative %s,lam_s_d:%s,lam_n_a:%s,lam_s:%s,P_s_1:%s,P_s_e:%s,P_n_0:%s")%(self.iterate_time,self.getRelativeChange(self.lam_s_d),self.getRelativeChange(self.lam_n_a),self.getRelativeChange(self.lam_s),self.getRelativeChange(self.P_s_1),self.getRelativeChange(self.P_s_e),self.getRelativeChange(self.P_n_0)))
            # change = (self.getChange(self.lam_s_d) + self.getChange(self.lam_n_a) + self.getChange(self.lam_s) + self.getChange(self.P_s_1) + self.getChange(self.P_s_e) + self.getChange(self.P_n_0))/6
            # biggest_change = (self.getAverageChange(self.lam_s_d) + self.getAverageChange(self.lam_n_a) + self.getAverageChange(self.lam_s) + self.getAverageChange(self.P_s_1) + self.getAverageChange(self.P_s_e) + self.getAverageChange(self.P_n_0))/6
            self.iterate_time = self.iterate_time + 1
            # print("第%s轮 平均变化:%0.8f"%(self.iterate_time, change))
            if self.export_by_period > 0 and self.iterate_time%self.export_by_period == 0:
                self.predictResults(final=False)

            # print("耗时:%s\n"%((datetime.datetime.now() - starttime).seconds))
        
        # df = pd.DataFrame({"re_lam_s_d":re_lam_s_d,"ab_lam_s_d":ab_lam_s_d,"re_lam_s_d":re_lam_s_d,"ab_lam_s_d":ab_lam_s_d,"re_lam_n_a":re_lam_n_a,"ab_lam_n_a":ab_lam_n_a,"re_lam_s":re_lam_s,"ab_lam_s":ab_lam_s,"re_P_s_1":re_P_s_1,"ab_P_s_1":ab_P_s_1,"re_P_s_e":re_P_s_e,"ab_P_s_e":ab_P_s_e,"re_P_n_0":re_P_n_0,"ab_P_n_0":ab_P_n_0})
        # df.to_csv("Simulation/res/paper_record/iterations.csv")
        endtime = datetime.datetime.now()
        print("迭代次数: %s 次" % self.iterate_time)
        print("执行时间: %s 秒" % (endtime - starttime))

        fo = open("Simulation/res/new_paper_iteration_log.txt", "a+")
        fo.write("预测时间段: %s 点 %s 分 - %s 点 %s 分 \n" % (PERIODS[self.HOUR_INDEX][0],PERIODS[self.HOUR_INDEX][1],PERIODS[self.HOUR_INDEX+1][0],PERIODS[self.HOUR_INDEX+1][1]))
        fo.write("实验设备: %s \n" % PLATFORM)
        fo.write("实验时间: %s \n" % (time.asctime( time.localtime(time.time()))))
        fo.write("最大检索层数: %s 层\n" % MAX_SEARCH_LAYERS)
        fo.write("最大OD ID: %s 个\n" % self.max_OD_ID)
        fo.write("可行OD数目: %s 个\n" % len(self.all_ODs))
        fo.write("Node数目: %s 个\n" % len(self.ALL_NODES))
        fo.write("Segment数目: %s 个\n" % len(self.ALL_SEGMENTS))
        fo.write("变量共计: %s 个\n" % (len(self.lam_n_a) + len(self.lam_s_d) + self.num_lam_s_n + len(self.lam_s) + len(self.P_s_1) + len(self.P_s_e) + len(self.P_n_0)))
        fo.write("")
        fo.write("迭代次数: %s 次\n" % self.iterate_time)
        fo.write("最终变化: %s\n" % change)
        fo.write("执行时间: %s 秒\n\n" % (endtime - starttime))
        # average = int((endtime - starttime).seconds)/self.iterate_time
        # fo.write("单轮时间: %s 秒\n\n" % average)
        fo.close()

        # fo = open("Simulation/res/average_time/%s.txt"%self.max_OD_ID, "a+")
        # average = int((endtime - starttime).seconds)/self.iterate_time
        # fo.write("单轮时间: %s 秒\n\n" % average)
        # fo.close()

    def obtainLamSDNA(self,_cur,_last):
        '''公式1-2计算'''
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
        '''获得lambdaSN'''
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
        '''公式4计算'''
        for i in self.all_segment_keys:
            self.lam_s[i][_cur] = 0
            for j in self.ALL_SEGMENTS[i]["matching_nodes"]:
                self.lam_s[i][_cur] = self.lam_s[i][_cur] + self.lam_s_n[i][j][_cur]

    def obtainPS(self,_cur,_last):
        '''公式6-9计算'''
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
        '''公式10'''
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

    def getChange(self,all_dic):
        '''获得差值'''
        overall_change = [abs(all_dic[i][0] - all_dic[i][1]) for i in  all_dic.keys()]
        return max(overall_change)

    def getRelativeChange(self,all_dic):
        '''获得差值'''
        last_index = self.iterate_time%2
        overall_change = []
        for i in all_dic.keys():
            if all_dic[i][0] < 1e-4 and all_dic[i][1] == 1e-4: continue
            if all_dic[i][0] == 0 or all_dic[i][1] == 0: continue
            overall_change.append(abs(all_dic[i][0] - all_dic[i][1])/all_dic[i][last_index])
        return max(overall_change)

    def getAverageChange(self,all_dic):
        '''获得差值'''
        overall_change = [abs(all_dic[i][0] - all_dic[i][1]) for i in  all_dic.keys()]
        return max(overall_change)/len(overall_change)

    def exportOne(self,file_path,file_name,all_items):
        '''导出一个参数的结果'''
        with open("%s/%s.csv"%(file_path,file_name),"w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["key","value"])
            for key in all_items.keys():
                if file_name == "lam_s_n":
                    input_item = []
                    for sub_key in all_items[key].keys():
                        input_item.append([sub_key,all_items[key][sub_key][self.iterate_time%2]])
                    writer.writerow([key,input_item])
                else:
                    writer.writerow([key,all_items[key][self.iterate_time%2]])

    def exportVariables(self):
        '''将所有的变量存储便于计算预测值'''
        file_path = "%s/variable/REAL_%s_PERIOD_%s_%.2f"%(DATA_PATH,self.max_OD_ID,self.HOUR_INDEX,self.tendency)
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        all_file_names = ["lam_n_a","lam_s_d","lam_s_n","lam_s","P_s_1","P_s_e","P_n_0"]
        all_items_list = [self.lam_n_a,self.lam_s_d,self.lam_s_n,self.lam_s,self.P_s_1,self.P_s_e,self.P_n_0]
        # all_file_names = ["lam_n_a","lam_s_d","lam_s","P_s_1","P_s_e","P_n_0"]
        # all_items_list = [self.lam_n_a,self.lam_s_d,self.lam_s,self.P_s_1,self.P_s_e,self.P_n_0]
        for i in range(len(all_file_names)):
            self.exportOne(file_path,all_file_names[i],all_items_list[i])

    def loadVariables(self):
        print("加载变量")
        self.iterate_time = 0
        file_path = "%s/variable/REAL_%s_PERIOD_%s_%.2f"%(DATA_PATH,self.max_OD_ID,self.HOUR_INDEX,self.tendency)
        self.lam_n_a,self.lam_s_d,self.lam_s_n,self.lam_s,self.P_s_1,self.P_s_e,self.P_n_0 = {},{},{},{},{},{},{}
        all_file_names = ["lam_n_a","lam_s_d","lam_s_n","lam_s","P_s_1","P_s_e","P_n_0"]
        all_items_list = [self.lam_n_a,self.lam_s_d,self.lam_s_n,self.lam_s,self.P_s_1,self.P_s_e,self.P_n_0]
        for i in range(len(all_file_names)):
            df = pd.read_csv("%s/%s.csv" % (file_path,all_file_names[i]))
            bar = progressbar.ProgressBar(widgets=[ '%s: '%all_file_names[i], progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
            for j in bar(range(df.shape[0])):
                if all_file_names[i] == "lam_s_n":
                    sub_items = json.loads(df["value"][j])
                    all_items_list[i][df["key"][j]] = {}
                    if sub_items == []: continue
                    for sub_item in sub_items:
                        all_items_list[i][df["key"][j]][sub_item[0]] = [sub_item[1],sub_item[1]]
                else:
                    all_items_list[i][df["key"][j]] = [df["value"][j],df["value"][j]]

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
        print("求解执行时间: %s 秒" % (endtime - starttime))

        fo = open("Simulation/res/new_paper_iteration_log.txt", "a+")
        fo.write("求解执行时间: %s 秒\n\n" % (endtime - starttime))
        fo.close()

        if final == False:
            file_path = "Simulation/res/iteration_times/OD_%s_PERIOD_%s_PRE_PERIOD_%.2f.csv"%(self.max_OD_ID,self.HOUR_INDEX,self.tendency)
            if self.iterate_time == self.export_by_period:
                with open(file_path,"w") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["OD_id", "start_ver", "end_ver", "num"])
                    for i in self.all_ODs.keys():
                        writer.writerow([self.all_ODs[i]["OD_id"], self.all_ODs[i]["start_ver"], self.all_ODs[i]["end_ver"],  self.all_ODs[i]["num"]])
            arr_P_w,arr_l_w,arr_e_w = [],[],[]
            for key in self.all_ODs.keys():
                arr_P_w.append(all_P_w[key]),arr_l_w.append(all_l_w[key]),arr_e_w.append(all_e_w[key])
            cur_index = int(self.iterate_time/self.export_by_period)
            res_df = pd.read_csv(file_path)
            res_df["P_w_%s"%cur_index],res_df["l_w_%s"%cur_index],res_df["e_w_%s"%cur_index] = arr_P_w,arr_l_w,arr_e_w
            if cur_index > 1:
                res_df["P_w_ch_%s"%cur_index],res_df["l_w_ch_%s"%cur_index],res_df["e_w_ch_%s"%cur_index] = \
                    abs(res_df["P_w_%s"%cur_index]-res_df["P_w_%s"%(cur_index-1)]),abs(res_df["l_w_%s"%cur_index]-res_df["l_w_%s"%(cur_index-1)]),abs(res_df["e_w_%s"%cur_index]-res_df["e_w_%s"%(cur_index-1)])
            res_df.to_csv(file_path,index=False)
        else:
            with open("Simulation/res/prediction/OD_%s_PERIOD_%s_SAMPLE_%s_PRE_%.2f.csv"%(self.max_OD_ID,self.HOUR_INDEX,self.min_samples,self.tendency),"w") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["OD_id", "start_ver", "end_ver", "num", "P_w", "l_w", "e_w"])
                for i in self.all_ODs.keys():
                    writer.writerow([self.all_ODs[i]["OD_id"], self.all_ODs[i]["start_ver"], self.all_ODs[i]["end_ver"],  self.all_ODs[i]["num"], all_P_w[i], all_l_w[i], all_e_w[i]])

    def predictSegmentDistance(self):
        '''计算预测结果'''
        matching_probability = {}
        G_n,all_P_w = {},{}
        bar = progressbar.ProgressBar(widgets=[ 'Probability: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(self.all_ODs.keys()):
            start_node = self.all_ODs[i]["nodes_keys"][0]
            start_segment = self.ALL_NODES[start_node]["sub_segment_key"]
            G_n[start_node] = 1
            last_node_key = start_node
            last_segment_key = self.ALL_NODES[last_node_key]["sub_segment_key"]
            for j in self.all_ODs[i]["nodes_keys"][1:]:
                G_n[j] = G_n[last_node_key] * (1 - self.P_n_0[last_node_key]) * (1 - self.P_s_1[last_segment_key])
                last_node_key,last_segment_key = j,self.ALL_NODES[j]["sub_segment_key"]

        # 预测拼车距离和共享距离
        all_l_w, all_e_w = {},{}
        bar = progressbar.ProgressBar(widgets=[ 'Distance: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(self.all_ODs.keys()):
            l_w_0 = Schedule.distanceByHistory(self.all_ODs[i]["start_ver"],self.all_ODs[i]["end_ver"])
            all_l_n_0, all_e_n_0 = [], []
            for node in self.all_ODs[i]["nodes_keys"]:
                if self.ALL_NODES[node]["matching_segments"] != []:
                    l_n_s, e_n_s = [],[]
                    for matching_seg in self.ALL_NODES[node]["matching_segments"]:
                        another_OD = self.ALL_SEGMENTS[matching_seg]["OD_id"]
                        if self.ALL_SEGMENTS[matching_seg]["type"] == 0:
                            res = Schedule.judgeMatching(ALL_EDGES[self.ALL_SEGMENTS[matching_seg]["edge_id"][0]]["tail_ver"],self.all_ODs[another_OD]["end_ver"],self.all_ODs[i]["start_ver"],self.all_ODs[i]["end_ver"])
                        else:
                            res = Schedule.judgeMatching(self.all_ODs[another_OD]["start_ver"],self.all_ODs[another_OD]["end_ver"],self.all_ODs[i]["start_ver"],self.all_ODs[i]["end_ver"])
                        if res == {}:
                            l_n_s.append(l_w_0), e_n_s.append(0)
                        else:
                            l_n_s.append(l_w_0 + res["detour2"]), e_n_s.append(res["shared_distance"])

                    overall_denominator = 0
                    for matching_seg in self.ALL_NODES[node]["matching_segments"]:
                        overall_denominator = overall_denominator + self.lam_s_n[matching_seg][node] * self.P_s_e[matching_seg]

                    l_n_0, e_n_0 = 0,0
                    for j, matching_seg in enumerate(self.ALL_NODES[node]["matching_segments"]):
                        l_n_0 = l_n_0 + self.lam_s_n[matching_seg][node] * self.P_s_e[matching_seg] * l_n_s[j]/overall_denominator
                        e_n_0 = e_n_0 + self.lam_s_n[matching_seg][node] * self.P_s_e[matching_seg] * e_n_s[j]/overall_denominator
                    all_l_n_0.append(l_n_0), all_e_n_0.append(e_n_0)
                else:
                    all_l_n_0.append(l_w_0), all_e_n_0.append(0)
            # print(all_l_n_0)
            # print(all_e_n_0)

            # 路段中的距离计算
            all_l_s_1, all_e_s_1 = [], []
            for seg in self.all_ODs[i]["segments_keys"]:
                l_s_1, e_s_1 = [],[]
                if self.ALL_SEGMENTS[seg]["matching_nodes"] != []:
                    l_n_s, e_n_s = [], []
                    for matching_node in self.ALL_SEGMENTS[seg]["matching_nodes"]:
                        another_OD = self.ALL_NODES[matching_node]["OD_id"]
                        if self.ALL_SEGMENTS[seg]["type"] == 0:
                            res = Schedule.judgeMatching(ALL_EDGES[self.ALL_SEGMENTS[seg]["edge_id"][0]]["tail_ver"],self.all_ODs[i]["end_ver"],self.all_ODs[another_OD]["start_ver"],self.all_ODs[another_OD]["end_ver"])
                        else:
                            res = Schedule.judgeMatching(self.all_ODs[i]["start_ver"],self.all_ODs[i]["end_ver"],self.all_ODs[another_OD]["start_ver"],self.all_ODs[another_OD]["end_ver"])
                        if res == {}:
                            l_n_s.append(l_w_0), e_n_s.append(0)
                        else:
                            l_n_s.append(l_w_0 + res["detour1"]), e_n_s.append(res["shared_distance"])

                    # print("l_n_s:",l_n_s)
                    l_s_1, e_s_1 = 0,0
                    for j,matching_node in enumerate(self.ALL_SEGMENTS[seg]["matching_nodes"]):
                        l_s_1 = l_s_1 + self.lam_s_n[seg][matching_node] * l_n_s[j]/self.lam_s[seg]
                        e_s_1 = e_s_1 + self.lam_s_n[seg][matching_node] * e_n_s[j]/self.lam_s[seg]
                    all_l_s_1.append(l_s_1), all_e_s_1.append(e_s_1)
                else:
                    all_l_s_1.append(l_w_0), all_e_s_1.append(0)

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
        '''加载OD的列的情况'''
        df = pd.read_csv("%s/prestore/ODs_layers_3.csv"%DATA_PATH)
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

    def updateOrdersNum(self):
        '''更新订单的数目'''
        prediction_df = pd.read_csv("Simulation/res/prediction/OD_%s_PERIOD_%s_SAMPLE_%s_PRE.csv"%(self.max_OD_ID,self.HOUR_INDEX,self.min_samples))
        lambda_df = pd.read_csv("Simulation/data/ods/ODs_prestore.csv")
        all_num = []
        for i in range(prediction_df.shape[0]):
            all_num.append(lambda_df["num"][i])
        prediction_df["num"] = all_num
        prediction_df.to_csv("Simulation/res/prediction/OD_%s_PERIOD_%s_SAMPLE_%s_PRE.csv"%(self.max_OD_ID,self.HOUR_INDEX,self.min_samples),index=False)

class AjustPrediction(object):
    def __init__(self,hour,max_OD_ID):
        self.HOUR_INDEX = hour
        self.max_OD_ID = max_OD_ID
        self.min_sample = 15
        # self.checkPairs()
        self.initialData()
        self.getAllPrediction()

    def initialData(self):
        '''加载全部的OD Dictionary'''
        pre_df = pd.read_csv("Simulation/res/prediction/OD_%s_PERIOD_%s_SAMPLE_%s_PRE.csv"%(self.max_OD_ID,self.HOUR_INDEX,self.min_sample))
        self.pre_dic = {}
        bar = progressbar.ProgressBar(widgets=[ 'Load Prediction: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(range(pre_df.shape[0])):
            start_ver,end_ver = pre_df["start_ver"][i],pre_df["end_ver"][i]
            self.pre_dic[getID(start_ver,end_ver)] = {
                "OD_id" : pre_df["OD_id"][i],
                "start_ver" : start_ver,
                "end_ver" : end_ver,
                "P_w" : pre_df["P_w"][i],
                "l_w" : pre_df["l_w"][i],
                "e_w" : pre_df["e_w"][i]
            }
        pairs_df = pd.read_csv("Simulation/data/pairs.csv")
        self.pairs_dic = {}
        bar = progressbar.ProgressBar(widgets=[ 'Load Pairs: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(range(pairs_df.shape[0])):
            self.pairs_dic[pairs_df["original"][i]] = pairs_df["final"][i]

    def getAllPrediction(self):
        '''获得全部的预测结果'''
        with open("Simulation/res/prediction/OD_20000_PERIOD_%s_SAMPLE_%s_PRE_ORIGINAL.csv"%(self.HOUR_INDEX,self.min_sample),"w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["new_OD_id", "original_OD_id", "num", "start_ver", "end_ver", "P_w", "l_w", "e_w"])
        ODs_df = pd.read_csv("Simulation/data/ods/original_%s.csv" % self.HOUR_INDEX)
        bar = progressbar.ProgressBar(widgets=[ 'Adjust ODs: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(range(ODs_df.shape[0])):
            start_ver,end_ver = ODs_df["start_ver"][i],ODs_df["end_ver"][i]
            res = self.getResult(start_ver,end_ver)
            if res != {}:
                with open("Simulation/res/prediction/OD_20000_PERIOD_%s_SAMPLE_%s_PRE_ORIGINAL.csv"%(self.HOUR_INDEX,self.min_sample),"a+") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([i, res["OD_id"], ODs_df["num"][i], start_ver, end_ver, res["P_w"], res["l_w"], res["e_w"]])

    def getResult(self,start_ver,end_ver):
        '''获得调整后的结果'''
        final_start_ver = start_ver
        if start_ver in self.pairs_dic:
            final_start_ver = self.pairs_dic[start_ver]
        final_end_ver = end_ver
        if end_ver in self.pairs_dic:
            final_end_ver = self.pairs_dic[end_ver]
        combined_id = getID(final_start_ver,final_end_ver)
        if combined_id not in self.pre_dic:
            # print("OD不存在")
            return {}
        # print(start_ver,end_ver,final_start_ver,final_end_ver)
        res = deepcopy(self.pre_dic[combined_id])
        res["start_ver"],res["start_ver"] = start_ver,end_ver
        detour = Schedule.distanceByHistory(start_ver,end_ver) - Schedule.distanceByHistory(final_start_ver,final_end_ver)
        res["l_w"] = res["l_w"] + detour
        # res["e_w"] = res["e_w"] + detour * self.P_n_0[self.all_ODs[combined_id]["start_node"]]
        return res

    def loadVariables(self):
        '''加载变量'''
        file_path = "%s/variable/REAL_%s_PERIOD_%s"%(DATA_PATH,self.max_OD_ID,self.HOUR_INDEX)
        self.P_n_0 = {}
        all_file_names = ["P_n_0"]
        all_items_list = [self.P_n_0]
        for i in range(len(all_file_names)):
            df = pd.read_csv("%s/%s.csv" % (file_path,all_file_names[i]))
            bar = progressbar.ProgressBar(widgets=[ '%s: '%all_file_names[i], progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
            bar = progressbar.ProgressBar(widgets=["Varibles Loading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])        
            for j in bar(range(df.shape[0])):
                all_items_list[i][df["key"][j]] = df["value"][j]

    def loadODs(self):
        '''加载全部的OD以及匹配情况'''
        lambda_df = pd.read_csv("Simulation/data/ods/combined_%s.csv" % self.HOUR_INDEX)
        ODs_df = pd.read_csv("%s/prestore/ODs_layers_3.csv" % DATA_PATH)
        self.all_ODs = {}
        bar = progressbar.ProgressBar(widgets=["ODs Loading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])        
        for j in bar(range(self.max_OD_ID)):
            if lambda_df["days"][j] < 17: break
            combined_id = getID(lambda_df["start_ver"][j],lambda_df["end_ver"][j])
            i = self.OD_dic[combined_id]["line_id"]
            segments_keys = json.loads(ODs_df["segments_keys"][i])
            nodes_keys = json.loads(ODs_df["nodes_keys"][i])
            self.all_ODs[combined_id] = {
                "OD_id": ODs_df["id"][i],
                "start_ver": ODs_df["start_ver"][i],
                "end_ver": ODs_df["end_ver"][i],
                "start_segment": segments_keys[0],
                "start_node": nodes_keys[0],
                "lam_w": lambda_df["num"][j]/(PERIODS_MINUTES[self.HOUR_INDEX]*44)
            }

    def loadODDic(self):
        '''加载OD的列的情况'''
        df = pd.read_csv("%s/prestore/ODs_layers_3.csv"%DATA_PATH)
        self.OD_dic = {}
        bar = progressbar.ProgressBar(widgets=["OD Dic Loading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])        
        for i in range(df.shape[0]):
            combined_id = getID(df["start_ver"][i],df["end_ver"][i])
            self.OD_dic[combined_id] = {
                "line_id": i,
                "start_ver": df["start_ver"][i],
                "end_ver": df["end_ver"][i]
            }

    def checkPairs(self):
        '''检查调整模型是否有问题'''
        pairs_df = pd.read_csv("Simulation/data/pairs.csv")
        self.pairs_dic = {}
        bar = progressbar.ProgressBar(widgets=[ 'Load Pairs: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(range(pairs_df.shape[0])):
            self.pairs_dic[pairs_df["original"][i]] = pairs_df["final"][i]
        combined_ODs_df = pd.read_csv("Simulation/data/ODs_combined.csv")
        combined_ODs = []
        for i in range(combined_ODs_df.shape[0]):
            combined_ODs.append(getID(combined_ODs_df["start_ver"][i],combined_ODs_df["end_ver"][i]))
        original_ODs_df = pd.read_csv("Simulation/data/ODs_original.csv")
        wrong_num = 0
        bar = progressbar.ProgressBar(widgets=[ 'Check Pairs: ', progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        for i in bar(range(original_ODs_df.shape[0])):
            final_start_ver = original_ODs_df["start_ver"][i]
            if original_ODs_df["start_ver"][i] in self.pairs_dic:
                final_start_ver = self.pairs_dic[original_ODs_df["start_ver"][i]]
            final_end_ver = original_ODs_df["end_ver"][i]
            if original_ODs_df["end_ver"][i] in self.pairs_dic:
                final_end_ver = self.pairs_dic[original_ODs_df["end_ver"][i]]
            if final_end_ver == final_start_ver: continue
            combined_id = getID(final_end_ver,final_start_ver)
            if combined_id not in combined_ODs:
                wrong_num = wrong_num + 1
        print("无对应OD的个数:",wrong_num)
            


if __name__ == "__main__":
    # PreProcessData()
    # InteratedSolver(0.25)
    # InteratedSolver(0.5)
    # InteratedSolver(0.75)
    InteratedSolver(1)

