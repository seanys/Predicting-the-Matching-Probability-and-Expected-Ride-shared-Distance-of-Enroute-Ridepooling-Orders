'''
拼车仿真按照新网络调整
车辆：初始化足够的车辆，按照随机路径运行，或者按照规划路径
车辆：初始化所有的车辆，如果有运行
乘客：按照OD Pairs每个进行按照指数分布的时间生成乘客，生成后寻找附近
时间分析：基础时间为1min，车辆过十字路口时间为2分钟，过路段的时间计为10min（模拟）
'''
from copy import deepcopy
from interval import Interval
from operator import itemgetter,attrgetter
import random
import simpy
import json
import time
import numpy as np
import pandas as pd
import datetime
import csv
import progressbar
from assistant import Schedule
from basis.setting import MAX_SEARCH_LAYERS,MAX_DETOUR_LENGTH
from basis.setting import WAITING_TIME,DATA_PATH,PERIODS_MINUTES,getSpeed,SPEED
from basis.edges import ALL_EDGES,ALL_EDGES_DIC
from basis.vertexes import ALL_VERTEXES
from basis.neighbor import ALL_NEIGHBOR_EDGES
from basis.assistant import getID


ALL_PASSENGERS = {} # 乘客的信息
EDGES_TO_CUSTOMERS = [[] for _ in range(len(ALL_EDGES))] # 边与乘客的信息
RANDOM_SEED = 30 # 随机种子


class CarpoolSimulation(object):
    def __init__(self, env, max_time, source = "lambda"):
        self.begin_time = time.strftime("%m-%d %H:%M:%S", time.localtime()) 
        self.overall_success = 0
        self.schedule_by_history = True
        self.env = env
        self.max_time = max_time
        self.all_OD = False
        source = "lambda"
        if source == "lambda":
            '''会选择部分OD仿真'''
            self.COMBINED_OD = True
            self.HOUR_INDEX = 0
            self.max_OD_ID = 100
            print("第%s阶段实验" % self.HOUR_INDEX)
            if self.COMBINED_OD == False:
                self.csv_path = "%s/experiment/OD_ALL_PERIOD_%s_ORIGINAL.csv"%(DATA_PATH,self.HOUR_INDEX)
            else:
                self.csv_path = "%s/experiment/OD_ALL_PERIOD_%s_COMBINED.csv"%(DATA_PATH,self.HOUR_INDEX)
            if self.all_OD == False:
                self.csv_path = "%s/experiment/OD_%s_PERIOD_%s.csv"%(DATA_PATH,self.max_OD_ID,self.HOUR_INDEX)
            self.writeHead()
            self.generateByLam()
            self.env.process(self.clockFunc())
        else:
            '''会直接根据某一个月的数据直接全部仿真'''
            self.COMBINED_OD = True
            self.tendency = 1
            self.possibleOD()
            self.env.process(self.generateByHistory())

    def writeHead(self):
        '''输入CSV文件的头部'''
        with open(self.csv_path,"w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["passenger_id", "real_start_date", "real_start_time", "start_time", "end_time", "OD_id", 
                "start_ver", "end_ver","orginal_start_ver", "orginal_end_ver", "original_distance",  "final_distance", 
                    "matching_or", "shared_distance", "detour", "gap", "matching_id", "matching_type", "matching_ver",""])

    def clockFunc(self):
        '''进行时间记录'''
        count_num = 0
        while True:
            yield self.env.timeout(1000)
            count_num += 1
            progress = (count_num*1000/self.max_time)*100
            print("实验进度 %.2f" % progress)
            # print("实验进度 %.2f%" % progress)

    def possibleOD(self):
        '''获得可能的OD'''
        if self.COMBINED_OD == True:
            ODs_df = pd.read_csv("Simulation/data/ODs_combined.csv")
        else:
            ODs_df = pd.read_csv("Simulation/data/ODs_original.csv")
        self.possible_ODs = {}
        for i in range(ODs_df.shape[0]):
            self.possible_ODs[getID(ODs_df["start_ver"][i],ODs_df["end_ver"][i])] = i
        print("获得全部可行OD")

    def generateByHistory(self):
        '''根据历史的数据生成乘客'''
        self.csv_path = "%s/experiment/ALL_COMBINED_%s_%.2f.csv"%(DATA_PATH,self.COMBINED_OD,self.tendency)
        self.writeHead()
        history_df = pd.read_csv("%s/orders/all_orders.csv"%(DATA_PATH))
        history_df["depature_time"] = pd.to_datetime(history_df['depature_time'])
        cur_line = 1
        while True:
            while history_df["depature_time"][cur_line].minute == history_df["depature_time"][cur_line-1].minute:
                self.env.process(self.generateLine(cur_line,history_df))
                cur_line = cur_line + 1
                if cur_line >= history_df.shape[0]: break
            if cur_line >= history_df.shape[0]: break
            yield self.env.timeout(1)
            self.env.process(self.generateLine(cur_line,history_df))
            cur_line = cur_line + 1
            if cur_line >= history_df.shape[0]: break
    
    def generateLine(self,cur_line,history_df):
        '''生成一列数据实验结果'''
        original_start_ver,original_end_ver = history_df["depature_ver"][cur_line],history_df["arrive_ver"][cur_line]
        start_ver,end_ver = history_df["combined_depature_ver"][cur_line],history_df["combined_arrive_ver"][cur_line]
        if self.COMBINED_OD == True:
            combined_id = getID(start_ver,end_ver)
        else:
            combined_id = getID(original_start_ver,original_end_ver)
        if random.random() > self.tendency or (start_ver == end_ver and self.COMBINED_OD == True) or (original_start_ver == original_end_ver and self.COMBINED_OD == False) or combined_id not in self.possible_ODs:
            yield self.env.timeout(0.0000000000001)
        else:
            real_start_time = history_df["depature_time"][cur_line]
            self.env.process(self.passenger([start_ver,end_ver,original_start_ver,original_end_ver,real_start_time],self.possible_ODs[combined_id]))

    def generateByLam(self):
        '''选择部分OD赋值初始的lam计算'''
        # print("开始生成乘客")
        ODs_df = pd.read_csv("Simulation/data/ods/combined_%s.csv" % self.HOUR_INDEX)
        max_num = ODs_df.shape[0]
        if self.all_OD == False:
            max_num = self.max_OD_ID
        for i in range(max_num):
            if ODs_df["start_ver"][i] == ODs_df["end_ver"][i] or ODs_df["num"][i] == 0: continue
            self.env.process(self.passengerGenerateOD(ODs_df["start_ver"][i],ODs_df["end_ver"][i],ODs_df["num"][i]/(PERIODS_MINUTES[self.HOUR_INDEX]*44),i))

    def passengerGenerateOD(self,i,j,lam,OD_id):
        '''每个OD Pair生成乘客（按照随机生成）'''
        while True:
            if lam == 0: break
            yield env.timeout(random.expovariate(lam))
            self.env.process(self.passenger([i,j,i,j,datetime.datetime(2020, 12, 12)],OD_id))

    def passenger(self, OD_detail, OD_id):
        '''乘客行为模拟：首先在一定时间内检索拼车，为寻找到则寻找空车'''
        if self.COMBINED_OD == True:
            start_ver,end_ver = OD_detail[0],OD_detail[1]
        else:
            start_ver,end_ver = OD_detail[2],OD_detail[3]
        if start_ver == end_ver: return
        passenger_id = len(ALL_PASSENGERS.keys())
        real_time = "2017-%02d-%02d %02d:%02d" % (OD_detail[4].month,OD_detail[4].day,OD_detail[4].hour,OD_detail[4].minute)
        real_date = "2017-%02d-%02d" % (OD_detail[4].month,OD_detail[4].day)
        ALL_PASSENGERS[passenger_id] = { "OD_id" : OD_id, "real_start_time": real_time, "start_time" : "%.1f"%self.env.now, "start_ver" : OD_detail[0], 
            "end_ver" : OD_detail[1], "original_start_ver" : OD_detail[2], "original_end_ver" : OD_detail[3], "total_distance": 0, 
                "trajectory": [], "final_route": [], "finish": False, "real_date":real_date}

        # 顶点处检索是否存在
        neighbor_edges = ALL_NEIGHBOR_EDGES[start_ver]
        for edge_id in neighbor_edges:
            all_possible_id = []
            for another_id in EDGES_TO_CUSTOMERS[edge_id]:
                res,_type = {},0
                if ALL_PASSENGERS[another_id]["status"] == 0:
                    res = Schedule.judgeMatching(ALL_PASSENGERS[another_id]["start_ver"],ALL_PASSENGERS[another_id]["end_ver"],start_ver,end_ver)
                elif ALL_PASSENGERS[another_id]["status"] == 1:
                    _type = 1
                    res = Schedule.judgeMatching(ALL_PASSENGERS[another_id]["next_ver"],ALL_PASSENGERS[another_id]["end_ver"],start_ver,end_ver)
                if res != {}:
                    all_possible_id.append({"gap":res["gap"],"another_id":another_id,"route1":res["route1"],
                        "route1_segs":res["route1_segs"], "route2":res["route2"],"route2_segs":res["route2_segs"],
                            "_type":_type, "data": res, "another_start_ver": ALL_PASSENGERS[another_id]["start_ver"], 
                            "another_end_ver": ALL_PASSENGERS[another_id]["end_ver"] })
            if len(all_possible_id) == 0: continue
            sorted_res = sorted(all_possible_id, key = lambda x:(x["another_start_ver"],x["another_end_ver"]))
            res = sorted_res[0]
            another_id = res["another_id"]
            # print("拼车成功passenger%s-passenger%s"%(passenger_id,another_id))
            route1,route1_segs,route2,route2_segs = res["route1"],res["route1_segs"],res["route2"],res["route2_segs"]
            # 参数记录
            ALL_PASSENGERS[passenger_id]["gap"] = res["gap"]
            ALL_PASSENGERS[another_id]["gap"] = res["gap"]
            ALL_PASSENGERS[passenger_id]["matching_ver"] = res["data"]["macting_pt2"]
            ALL_PASSENGERS[another_id]["matching_ver"] = res["data"]["macting_pt1"]
            ALL_PASSENGERS[passenger_id]["matching_id"] = another_id
            ALL_PASSENGERS[another_id]["matching_id"] = passenger_id
            ALL_PASSENGERS[passenger_id]["detour"] = res["data"]["detour2"]
            ALL_PASSENGERS[another_id]["detour"] = res["data"]["detour1"]
            ALL_PASSENGERS[passenger_id]["shared_distance"] = res["data"]["shared_distance"]
            ALL_PASSENGERS[another_id]["shared_distance"] = res["data"]["shared_distance"]
            # 触发请求
            ALL_PASSENGERS[passenger_id]["wait_for_carry"] = self.env.event()
            ALL_PASSENGERS[passenger_id]["route"], ALL_PASSENGERS[another_id]["route"] = Schedule.delNear(route2),Schedule.delNear(route1)
            ALL_PASSENGERS[passenger_id]["route_segs"], ALL_PASSENGERS[another_id]["route_segs"] = Schedule.delNear(route2_segs),Schedule.delNear(route1_segs)
            ALL_PASSENGERS[another_id]["carry_position"] = start_ver
            ALL_PASSENGERS[another_id]["carry_or"] = False
            ALL_PASSENGERS[another_id]["carry_id"] = passenger_id
            ALL_PASSENGERS[passenger_id]["status"], ALL_PASSENGERS[another_id]["status"] = 2,2
            # 记录匹配情况和触发操作
            ALL_PASSENGERS[passenger_id]["matching_type"] = 0 # 起始位置匹配到
            if res["_type"] == 0:
                ALL_PASSENGERS[another_id]["wait_for_match"].succeed()
                ALL_PASSENGERS[another_id]["matching_type"] = 1 # 起点等待匹配
            else:
                ALL_PASSENGERS[another_id]["matching_type"] = 2 # 途中匹配
            yield ALL_PASSENGERS[passenger_id]["wait_for_carry"] # 等待来接
            self.env.process(self.operateOnCar(passenger_id))
            return
        
        # 起始位置开始等待，0为起始点待匹配，1为在车上待匹配，2为已经匹配成功，3为到达目的地
        ALL_PASSENGERS[passenger_id]["wait_for_match"] = self.env.event()
        ALL_PASSENGERS[passenger_id]["status"] = 0
        all_arces = ALL_VERTEXES[start_ver]["front_arc"]

        for arc in all_arces:
            EDGES_TO_CUSTOMERS[arc].append(passenger_id)
        yield ALL_PASSENGERS[passenger_id]["wait_for_match"] | self.env.timeout(3)
        for arc in all_arces:
            EDGES_TO_CUSTOMERS[arc].remove(passenger_id)

        self.env.process(self.operateOnCar(passenger_id))

    def operateOnCar(self,passenger_id):
        '''乘客开始运行车辆（从起点开始）'''
        if ALL_PASSENGERS[passenger_id]["status"] == 0: 
            ALL_PASSENGERS[passenger_id]["status"] = 1 # 0为起始点待匹配，1为在车上待匹配，2为已经匹配成功
            route,route_segs = Schedule.verRouteByHistory(ALL_PASSENGERS[passenger_id]["start_ver"],ALL_PASSENGERS[passenger_id]["end_ver"])
            ALL_PASSENGERS[passenger_id]["route"], ALL_PASSENGERS[passenger_id]["route_segs"] = route,route_segs

        while ALL_PASSENGERS[passenger_id]["route_segs"] != []:
            if "carry_position" in ALL_PASSENGERS[passenger_id]:
                if ALL_PASSENGERS[passenger_id]["carry_or"] == False:
                    if ALL_PASSENGERS[passenger_id]["carry_position"] == ALL_PASSENGERS[passenger_id]["route"][0]:
                        ALL_PASSENGERS[ALL_PASSENGERS[passenger_id]["carry_id"]]["wait_for_carry"].succeed()
                        ALL_PASSENGERS[passenger_id]["carry_or"] = True

            ALL_PASSENGERS[passenger_id]["trajectory"] = ALL_PASSENGERS[passenger_id]["trajectory"] + ALL_EDGES[ALL_PASSENGERS[passenger_id]["route_segs"][0]]["polyline"]
            ALL_PASSENGERS[passenger_id]["final_route"].append(ALL_PASSENGERS[passenger_id]["route"][0])
            current_edge = ALL_PASSENGERS[passenger_id]["route_segs"][0]
            EDGES_TO_CUSTOMERS[current_edge].append(passenger_id)
            ALL_PASSENGERS[passenger_id]["total_distance"] += ALL_EDGES[current_edge]["length"]            
            ALL_PASSENGERS[passenger_id]["next_ver"] = ALL_PASSENGERS[passenger_id]["route"][1]
            ALL_PASSENGERS[passenger_id]["route"] = ALL_PASSENGERS[passenger_id]["route"][1:]
            ALL_PASSENGERS[passenger_id]["route_segs"] = ALL_PASSENGERS[passenger_id]["route_segs"][1:]

            yield self.env.timeout(ALL_EDGES[current_edge]["length"]/SPEED) 
            yield self.env.timeout(0.5)
            
            EDGES_TO_CUSTOMERS[current_edge].remove(passenger_id)
        
        ALL_PASSENGERS[passenger_id]["final_route"].append(ALL_PASSENGERS[passenger_id]["end_ver"])
        ALL_PASSENGERS[passenger_id]["finish"] = True
        
        # if ALL_PASSENGERS[passenger_id]["carry_or"] 
        # print("%.0f分钟 %s到达目的地" % (self.env.now, passenger_id))
        OD_id = ALL_PASSENGERS[passenger_id]["OD_id"]

        # 输出计算结果
        with open(self.csv_path,"a+") as csvfile:
            writer = csv.writer(csvfile)
            start_ver, end_ver = ALL_PASSENGERS[passenger_id]["start_ver"], ALL_PASSENGERS[passenger_id]["end_ver"]
            original_start_ver, original_end_ver = ALL_PASSENGERS[passenger_id]["original_start_ver"], ALL_PASSENGERS[passenger_id]["original_end_ver"]
            original_distance = "%2.2f" % (Schedule.distanceByHistory(start_ver, end_ver))
            real_start_time = ALL_PASSENGERS[passenger_id]["real_start_time"]
            real_date = ALL_PASSENGERS[passenger_id]["real_date"]
            if ALL_PASSENGERS[passenger_id]["status"] == 1:
                writer.writerow([passenger_id, real_date, real_start_time, ALL_PASSENGERS[passenger_id]["start_time"], "%.1f"%self.env.now, OD_id, start_ver, 
                    end_ver, original_start_ver, original_end_ver, original_distance, original_distance, 0, "", "", "", "", 
                        "" ,"", ""])
            else:
                self.overall_success = self.overall_success + 1
                writer.writerow([passenger_id, real_date, real_start_time, ALL_PASSENGERS[passenger_id]["start_time"], "%.1f"%self.env.now, OD_id, start_ver, 
                    end_ver, original_start_ver, original_end_ver, original_distance, "%2.2f" % ALL_PASSENGERS[passenger_id]["total_distance"], 1, 
                        "%2.2f" % ALL_PASSENGERS[passenger_id]["shared_distance"], "%2.2f" % ALL_PASSENGERS[passenger_id]["detour"],
                            "%2.2f" % ALL_PASSENGERS[passenger_id]["gap"], ALL_PASSENGERS[passenger_id]["matching_id"],
                                ALL_PASSENGERS[passenger_id]["matching_type"], ALL_PASSENGERS[passenger_id]["matching_ver"],""])

if __name__ == '__main__':
    max_time = 100000
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    CarpoolSimulation(env,max_time)

    env.run(until=max_time)
    # res = Schedule.verByHistory(586,80)
    # print(res)
