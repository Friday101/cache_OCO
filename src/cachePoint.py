import numpy as np
from src.cacheEnv import *

class cachePoint:
    def __init__(self, id, x, y, computed_frequency, computingCapacity, storageCapacity):
        self.storageCapacity = storageCapacity
        self.stored_space = 0
        self.computingCapacity = computingCapacity
        self.computed_frequency = computed_frequency
        self.connection = None
        self.transmission_utility = np.zeros((cp_num,user_num))
        self.linkMatrix = np.zeros((cp_num,user_num)) # 元素是字典，连接对象和传输效用
        self.cacheStatus = None
        self.cache_FIFO_history = []
        self.cache_LRU_queue = []
        self.cache_LFU_dict = {}
        self.cache_FIFO_queue = []
        self.x = x
        self.y = y
        self.id = id
        self.cache_local_preference = None
        self.lambda_1 = 1
        self.lambda_2 = 1
        self.lambda_1_list = []
        self.lambda_2_list = []
        # self.lambda_1 = np.zeros([content_libaray_size,bitrateMaxLevel+1])
        # self.lambda_2 = np.zeros([content_libaray_size,bitrateMaxLevel+1])
        self.Constraint_C = np.zeros(T)
        self.Constraint_H = np.zeros(T)
        self.Constraint_Violation_C = np.zeros(T)
        self.Constraint_Violation_H = np.zeros(T)
        self.nb_len = []


