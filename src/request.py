import numpy as np
import random
from src.cacheEnv import *
from src.tools import *
# max就是K 内容库

class User:
    def __init__(self,id,x,y,zipf_p) -> None:
        self.x = x
        self.y = y
        self.request = UserRequest(zipf_p)
        self.id = id
        self.zipf_p = zipf_p
        self.linkMatrix = np.zeros((cp_num,user_num))
        self.transmission_utility = np.zeros((cp_num,user_num))
        

class UserRequest:
    def __init__(self, zipf_p, min=0, max=content_libaray_size-1):
        self.min = min
        self.max = max
        self.zipf_p = zipf_p
        # current slot req bitrate
        self.req, self.bitrate = self.generateReqList()

    def generateReqList(self):
        # zipf分布
        temp_content = zipf_distribution_sample(self.zipf_p, self.max, self.min)
        temp_bitrate = random.randint(bitrateMinLevel, bitrateMaxLevel)
        self.req = temp_content
        self.bitrate = temp_bitrate
        return temp_content, temp_bitrate

    # temp = np.random.zipf(self.zipf_p, 1)[0]
    # # 超出内容库 丢掉
    # while temp < self.min or temp > self.max:
    #     temp = np.random.zipf(self.zipf_p, 1)[0] - 1
       






class MultiUserReqList:
    def __init__(self, userNum, timeSlot, min, max):
        self.userNum = userNum
        self.overallReqList = []
        for i in range(userNum):
            singleReqList = UserRequest(timeSlot, min, max)
            self.overallReqList.append(singleReqList)
            
    def getReqListByUserIndex(self, index):
        return self.overallReqList[index]
    

            
        
            
        
# userReq = UserRequest(10)
# print(userReq.reqList, userReq.bitrateLevelList)
# test = MultiUserReqList(10, 10, 1, 5)
# print(test.getReqListByUserIndex(3).reqList, '\n')


