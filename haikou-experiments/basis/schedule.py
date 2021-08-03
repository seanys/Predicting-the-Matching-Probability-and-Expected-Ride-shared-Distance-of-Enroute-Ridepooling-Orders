from copy import deepcopy
from basis.assistant import getID,getIDFour,getIDL
from basis.setting import MAX_SEARCH_LAYERS,MAX_DETOUR_LENGTH
from basis.edges import ALL_EDGES,ALL_EDGES_DIC
from basis.vertexes import ALL_VERTEXES
from basis.neighbor import ALL_NEIGHBOR_EDGES
import random
import simpy
import json
import time
import numpy as np
import pandas as pd
import csv
import progressbar

ALL_ROUTES = pd.read_csv("haikou-experiments/datasets/SHORTEST_ROUTE.csv")
ALL_NODES,ALL_SEGMENTS = {},{}

class Schedule(object):
    '''规划思路：全部是按照历史规划'''
    @staticmethod
    def getEdges(route):
        '''获得全部的边'''
        edges = []
        for i in range(len(route)-1):
            combined_id = getID(route[i], route[i+1])
            edges.append(ALL_EDGES_DIC[combined_id]["id"])
        return edges

    @staticmethod 
    def verByHistory(ver_start, ver_end):
        '''按照历史直接全部规划'''
        _id = ver_start*len(ALL_VERTEXES)+ver_end
        return json.loads(ALL_ROUTES["route"][_id]),json.loads(ALL_ROUTES["route_segs"][_id]),ALL_ROUTES["distance"][_id]

    @staticmethod 
    def verRouteByHistory(ver_start, ver_end):
        '''按照历史直接全部规划'''
        _id = ver_start*len(ALL_VERTEXES)+ver_end
        return json.loads(ALL_ROUTES["route"][_id]),json.loads(ALL_ROUTES["route_segs"][_id])

    @staticmethod 
    def distanceByHistory(ver_start, ver_end):
        '''按照历史直接全部规划'''
        _id = ver_start*len(ALL_VERTEXES)+ver_end
        return ALL_ROUTES["distance"][_id]

    @staticmethod
    def delNear(original):
        new_arr = [original[0]]
        for i in range(1,len(original)):
            if original[i] == original[i-1]: continue
            new_arr.append(original[i])
        return new_arr

    @staticmethod
    def getNeighbor(vertex):
        '''获得某个顶点邻接边'''
        search_layer,neighbor_edges,neighbor_points = 0,[],[]
        current_vertex = [vertex]
        while search_layer < MAX_SEARCH_LAYERS:
            temp_current_vertex = []
            for search_ver in current_vertex:
                temp_current_vertex = temp_current_vertex + ALL_VERTEXES[search_ver]["front_ver"]
                for ver in ALL_VERTEXES[search_ver]["front_ver"]:
                    dic_key = getID(ver,search_ver)
                    if dic_key not in ALL_EDGES_DIC.keys(): continue
                    neighbor_edges.append(ALL_EDGES_DIC[dic_key]["id"])
                    neighbor_points.append(ver)
            current_vertex = deepcopy(temp_current_vertex)
            search_layer = search_layer + 1
        # print("neighbor_points", vertex, neighbor_points)
        # print("neighbor_edges", vertex, neighbor_edges)
        return Schedule.delExist(neighbor_edges),Schedule.delExist(neighbor_points)
    
    @staticmethod
    def delExist(original):
        new_arr = []
        for item in original:
            if item not in new_arr:
                new_arr.append(item)
        return new_arr

    @staticmethod
    def judgeEdgeID(point):
        '''判断所属的ID'''
        pt_item = Point(point)
        for block_id in ALL_BLOCKS.keys():
            if ALL_BLOCKS[block_id]["block_item"].contains(pt_item) == False:
                continue
            min_distance, min_edge_id = 99999999, -1
            for edge_id in ALL_EDGES:
                if block_id not in ALL_EDGES[edge_id]["block"]: continue
                distance = LineString(ALL_EDGES[edge_id]["polyline"]).distance(pt_item)
                if distance < min_distance:
                    min_edge_id = edge_id
                    min_distance = distance
            return min_edge_id
        return -1

    @staticmethod
    def judgeMatching(first_cur,first_end,second_start,second_end):
        '''评价两个订单匹配的结果（如果超出了最大的绕道距离会直接拒绝）'''
        if first_cur == first_end or second_start == second_end: return {}
        if first_end == second_start: return {}

        distance_first,distance_second = Schedule.distanceByHistory(first_cur,first_end), Schedule.distanceByHistory(second_start,second_end)

        distance0 = Schedule.distanceByHistory(first_cur,second_start)
        distance1, distance2 = Schedule.distanceByHistory(second_start,first_end), Schedule.distanceByHistory(first_end,second_end)
        distance3, distance4 = Schedule.distanceByHistory(second_start,second_end), Schedule.distanceByHistory(second_end,first_end)

        nodes_res1,segs_res1,nodes_res2,segs_res2 = [],[],[],[]
        nodes1, segs1 = Schedule.verRouteByHistory(first_cur,second_start)
        if distance1 + distance2 < distance3 + distance4:
            shared_distance = distance1
            detour1, detour2 = distance0 + distance1 - distance_first, distance1 + distance2 - distance_second
            nodes2, segs2 = Schedule.verRouteByHistory(second_start,first_end)
            nodes3, segs3 = Schedule.verRouteByHistory(first_end,second_end)
            nodes_res1,segs_res1,nodes_res2,segs_res2 = nodes1 + nodes2, segs1 + segs2, nodes2 + nodes3, segs2 + segs3
        else:
            shared_distance = distance3
            detour1, detour2 = distance0 + distance3 + distance4 - distance_first, 0
            nodes2, segs2 = Schedule.verRouteByHistory(second_start,second_end)
            nodes3, segs3 = Schedule.verRouteByHistory(second_end,first_end)
            nodes_res1,segs_res1,nodes_res2,segs_res2 = nodes1 + nodes2 + nodes3, segs1 + segs2 + segs3, nodes2, segs2
        
        res = { "route1":nodes_res1,"route1_segs":segs_res1,"route2": nodes_res2,"route2_segs": segs_res2, "gap": distance0, 
            "shared_distance":shared_distance, "detour1":detour1, "detour2":detour2, "macting_pt1": first_cur, 
                "macting_pt2":second_start }

        if detour1 < -1 or detour2 < -1:
            print('\033[1;35m %s %s %s %s \033[0m' % (first_cur,first_end,second_start,second_end))
            print('\033[1;35m %s %s \033[0m' % (distance_first,distance_second))
            print('\033[1;35m %s %s %s %s %s \033[0m' % (distance0, distance1, distance2, distance3, distance4))
            print('\033[1;35m %s %s \033[0m' % (detour1,detour2))

        if detour1 < MAX_DETOUR_LENGTH and detour2 < MAX_DETOUR_LENGTH:
            return res

        return {}

