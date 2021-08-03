import platform
import random

PLATFORM  = "APPLE M1"

MAX_SEARCH_LAYERS = 3 # Search distance - one layer = 500 m 
MAX_DETOUR_LENGTH = 1500 # Max detour distance

MINUTE = 1
SPEED = 500 # Average speed of the vehicles
WAITING_TIME = 3 # Average waiting time

PERIODS = [[8,00],[16,30]] 
PERIODS_MINUTES = [510]

MONTHS_DAY = [22,22,22,10]

CRITERION = [5,5,5,6,7,6,5]

def getSpeed():
    speed = random.gauss(500, 50)
    if speed < 350:
        return 350
    return speed
