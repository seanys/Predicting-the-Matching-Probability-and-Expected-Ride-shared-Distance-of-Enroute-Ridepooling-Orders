import platform
import random

# DATA_PATH = "/Users/sean/Documents/Projects/Data/滴滴数据"
DATA_PATH = "/Users/yangshan/Documents/Data/滴滴数据"
PLATFORM  = "APPLE M1"
if platform.system() != "Darwin":
    DATA_PATH = "/home/wangxiaolei/桌面/滴滴数据"
    PLATFORM = "INTEL Core i10900K"


MAX_SEARCH_LAYERS = 3 # 最多检索层数
MAX_DETOUR_LENGTH = 1500 # 最大的绕道距离

MINUTE = 1 # 统计时间
SPEED = 500 # 车辆速度
WAITING_TIME = 3 # 初始的等待时间

PERIODS = [[8,00],[16,30]] # 21:00-22:00用于测试
PERIODS_MINUTES = [510]

# PERIODS = [[7,30],[9,30],[11,30],[13,00],[15,00],[17,30],[19,00],[21,00]] # 21:00-22:00用于测试
# PERIODS_MINUTES = [120,120,90,120,150,90,120]
MONTHS_DAY = [22,22,22,10]

CRITERION = [5,5,5,6,7,6,5]

def getSpeed():
    '''获得在路段的速度'''
    speed = random.gauss(500, 50)
    if speed < 350:
        return 350
    return speed
