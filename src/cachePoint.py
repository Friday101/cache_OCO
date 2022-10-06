import numpy as np
from src.cacheEnv import *

class cachePoint:
    def __init__(self, id, x, y, computingCapacity, storageCapacity):
        self.storageCapacity = storageCapacity
        self.stored_space = 0
        self.computingCapacity = computingCapacity
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
        
        