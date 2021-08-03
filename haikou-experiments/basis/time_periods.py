from basis.setting import PERIODS
from basis.assistant import getID
import progressbar

ALL_PERIODS = []
for i in range(len(PERIODS)-1):
    ALL_PERIODS.append({"from":{"hour":PERIODS[i][0],"minute":PERIODS[i][1]},"to":{"hour":PERIODS[i+1][0],"minute":PERIODS[i+1][1]}})

def getperiodsIndex(all_periods):
    time_dics = {}
    for i,period in enumerate(all_periods):
        for hour in range(period["from"]["hour"],period["to"]["hour"]+1):
            min_minute,max_minute = 0,60
            if hour == period["from"]["hour"]: min_minute = period["from"]["minute"]
            if hour == period["to"]["hour"]: max_minute = period["to"]["minute"]
            for minute in range(min_minute,max_minute):
                time_dics[getID(hour,minute)] = i
    return time_dics
    
def getMinutes(all_periods):
    for i,period in enumerate(all_periods):
        period["minutes"] = (period["to"]["hour"]-period["from"]["hour"])*60 + period["to"]["minute"] - period["from"]["minute"]
    return all_periods

ALL_PERIODS = getMinutes(ALL_PERIODS)
TIME_DICS = getperiodsIndex(ALL_PERIODS)

