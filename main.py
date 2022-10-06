import math

import numpy as np

from src.cachePoint import *
from src.request import *
from src.comparion import *
import numpy
import random
import copy
from src.tools import *
from src.cacheEnv import *


# 初始化--不变的部分
for i in range(user_num):
    # 位置
    x_u = random.random()*width
    y_u = random.random()*high
    # 偏好
    # zipf_u = random.random()+0.75  # 0.5-1.5
    zipf_u = random.random()*1.2 + 0.2  # 0.5-1.5
    user_set.append(User(i, x_u, y_u, zipf_u))
    
for i in range(cp_num):
    # 位置
    x_c = random.random()*width
    y_c = random.random()*high
    # 资源
    computing_c_nu = 0.5+random.random() # 再调整
    storage_c = random.randint(spaceMin,spaceMax)
    cp_set.append(cachePoint(i, x_c, y_c, computing_c_nu, storage_c ))
    # 连接性 传输效用
    for j in range(user_num):
        dis = distance_2(user_set[j],cp_set[-1])
        if dis < radius_r: # 联通
            user_set[j].linkMatrix[cp_set[-1].id][user_set[j].id] = 1
            cp_set[-1].linkMatrix[cp_set[-1].id][user_set[j].id] = 1
            user_set[j].transmission_utility[cp_set[-1].id][user_set[j].id] = dis*base_t
            cp_set[-1].transmission_utility[cp_set[-1].id][user_set[j].id] = dis * base_t
        else:
            user_set[j].linkMatrix[cp_set[-1].id][user_set[j].id] = 0
            cp_set[-1].linkMatrix[cp_set[-1].id][user_set[j].id] = 0
            user_set[j].transmission_utility[cp_set[-1].id][user_set[j].id] = -1
            cp_set[-1].transmission_utility[cp_set[-1].id][user_set[j].id] = -1
    # 缓存状态
    cp_set[-1].cacheStatus = np.zeros((content_libaray_size,bitrateMaxLevel-bitrateMinLevel+1))
    cp_set[-1].cache_local_preference = np.zeros((T,content_libaray_size,bitrateMaxLevel-bitrateMinLevel+1))
    # cp_set[-1].cacheStatus = cache_init(cp_set[-1],user_set[0])

cp_LFU_set = copy.deepcopy(cp_set)
cp_LRU_set = copy.deepcopy(cp_set)
cp_FIFO_set = copy.deepcopy(cp_set)
cp_DB_set = copy.deepcopy(cp_set)
cp_SB_set = copy.deepcopy(cp_set)


### 绘制场景
import matplotlib.pyplot as plt
# fig,ax=plt.subplots(figsize=(1,1))
x_user_set = []
y_user_set = []
x_cp_set = []
y_cp_set = []
for i in range(user_num):
    x_user_set.append(user_set[i].x)
    y_user_set.append(user_set[i].y)
for i in range(cp_num):
    x_cp_set.append(cp_set[i].x)
    y_cp_set.append(cp_set[i].y)
for i in range(cp_num):
    circle = plt.Circle((cp_set[i].x,cp_set[i].y),radius_r,color="pink",fill="False")
    plt.gcf().gca().add_artist(circle)
plt.scatter(x_cp_set,y_cp_set,c='red',label='Cache Point')
plt.scatter(x_user_set,y_user_set,c="blue",label="User")
##图例
plt.legend()
plt.show()


# 主流程
### T slot
t = 0
request_list = []
request_list_summary = []
request_list_summary_times = []
while t < T:
    print("----------Time slot - "+str(t)+"----------")
    # 环境及参数更新
    ### 随机请求情况
    request_user_id = random.randint(0,user_num-1)  # 随机用户
    user_set[request_user_id].request.generateReqList() #随机请求
    request_user = user_set[request_user_id]
    request_list.append([request_user.id, request_user.request.req, request_user.request.bitrate])

    if [request_user.request.req,request_user.request.bitrate] in request_list_summary:
        request_list_summary_times[ request_list_summary.index([request_user.request.req,request_user.request.bitrate]) ] += 1
    else:
        request_list_summary.append([request_user.request.req, request_user.request.bitrate])
        request_list_summary_times.append(1)

    print("request: user_id-"+ str(request_user.id) +",content-"+ str(request_user.request.req) + ",bitrate-"+ str(request_user.request.bitrate) )

    # Routing  --- 算法1
    # routed_amout = 0
    Matching_Pool_TOC_S,Routing_Result_TOC_S,Routing_Amount_TOC_S,cache_hit_t = route(cp_set,request_user,request_user_id,t)
    Matching_Pool_LRU, Routing_Result_LRU, Routing_Amount_LRU, cache_hit_t_LRU = route(cp_LRU_set, request_user,
                                                                                               request_user_id,t)
    Matching_Pool_LFU, Routing_Result_LFU, Routing_Amount_LFU, cache_hit_t_LFU = route(cp_LFU_set, request_user,
                                                                                             request_user_id,t)
    Matching_Pool_FIFO, Routing_Result_FIFO, Routing_Amount_FIFO, cache_hit_t_FIFO = route(cp_FIFO_set, request_user,
                                                                                             request_user_id,t)

    # 时间流逝
    t += 1
    if len(cache_hit_t) > 0:
        cache_hit_ratio_record_TOC_S.append(sum(cache_hit_t)/len(cache_hit_t))
    else:
        cache_hit_ratio_record_TOC_S.append(0)

    if len(cache_hit_t_LRU) > 0:
        cache_hit_ratio_record_LRU.append(sum(cache_hit_t_LRU)/len(cache_hit_t_LRU))
    else:
        cache_hit_ratio_record_LRU.append(0)

    if len(cache_hit_t_LFU) > 0:
        cache_hit_ratio_record_LFU.append(sum(cache_hit_t_LFU) / len(cache_hit_t_LFU))
    else:
        cache_hit_ratio_record_LFU.append(0)

    if len(cache_hit_t_FIFO) > 0:
        cache_hit_ratio_record_FIFO.append(sum(cache_hit_t_FIFO) / len(cache_hit_t_FIFO))
    else:
        cache_hit_ratio_record_FIFO.append(0)


    # routing & cache utility
    if not cache_hit_ratio_record_TOC_S[-1]:
        utility_record_TOC_S.append(0)
    else:
        utility_t = 0
        for i in Routing_Result_TOC_S:
            utility_t += i[3]
        utility_record_TOC_S.append(utility_t)


    if not cache_hit_ratio_record_LRU[-1]:
        utility_record_LRU.append(0)
    else:
        utility_t_lru = 0
        for i in Routing_Result_LRU:
            utility_t_lru += i[3]
        utility_record_LRU.append(utility_t_lru)


    if not cache_hit_ratio_record_LFU[-1]:
        utility_record_LFU.append(0)
    else:
        utility_t_lfu = 0
        for i in Routing_Result_LFU:
            utility_t_lfu += i[3]
        utility_record_LFU.append(utility_t_lfu)

    if not cache_hit_ratio_record_FIFO[-1]:
        utility_record_FIFO.append(0)
    else:
        utility_t_fifo = 0
        for i in Routing_Result_FIFO:
            utility_t_fifo += i[3]
        utility_record_FIFO.append(utility_t_fifo)

    # Caching  --- 算法2
    replace_flag_TOC_S = False
    replace_flag_LRU = False
    replace_flag_LFU = False
    replace_flag_FIFO = False
    if Routing_Result_TOC_S == []:
        # 从云端拉取
        for i in cp_set:
            # 方案1
            # if i.stored_space + 1*base_s*(request_user.request.bitrate+1) > i.storageCapacity:
            #     update_cache_least_popular(i, 1)
            #     i.cacheStatus[request_user.request.req,request_user.request.bitrate] = 1
            # else:
            #     i.cacheStatus[request_user.request.req,request_user.request.bitrate] = 1
            # 方案2
            replace_flag_TOC_S = TOC_S(cp_set, request_user, [i.id,request_user.request.bitrate,1,0.0], t)
    else:
        for i in Routing_Result_TOC_S:
            ### TOC-S
            if i[1] > bitrateMaxLevel:
                continue
            replace_flag_TOC_S = TOC_S(cp_set, request_user, i, t)

    if Routing_Result_LRU == []:
        # 从云端拉取
        for i in cp_LRU_set:
            # 方案2
            replace_flag_LRU = LRU(cp_LRU_set, request_user, [i.id,request_user.request.bitrate,1,0.0], t)
    else:
        for i in Routing_Result_LRU:
            ### LRU
            if i[1] > bitrateMaxLevel:
                continue
            replace_flag_LRU = LRU(cp_LRU_set, request_user, i, t)

    if Routing_Result_LFU == []:
        # 从云端拉取
        for i in cp_LFU_set:
            # 方案2
            replace_flag_LFU = LFU(cp_LFU_set, request_user, [i.id,request_user.request.bitrate,1,0.0], t)
    else:
        for i in Routing_Result_LFU:
            ### LFU
            if i[1] > bitrateMaxLevel:
                continue
            replace_flag_LFU = LFU(cp_LFU_set, request_user, i, t)

    if Routing_Result_FIFO == []:
        # 从云端拉取
        for i in cp_FIFO_set:
            # 方案2
            replace_flag_FIFO = FIFO(cp_FIFO_set, request_user, [i.id, request_user.request.bitrate, 1, 0.0], t)
    else:
        for i in Routing_Result_FIFO:
            ### FIFO
            if i[1] > bitrateMaxLevel:
                continue
            replace_flag_FIFO = FIFO(cp_FIFO_set, request_user, i, t)

    cache_replace_frequency_TOC_S.append(replace_flag_TOC_S)
    cache_replace_frequency_LRU.append(replace_flag_LRU)
    cache_replace_frequency_LFU.append(replace_flag_LFU)
    cache_replace_frequency_FIFO.append(replace_flag_FIFO)

# Benchmark
print("Execute benchmark algorithm...")
cache_hit_ratio_record_SB,utility_record_SB = static_benchmark(request_list,request_list_summary,request_list_summary_times,cp_SB_set,user_set,cp_set)
cache_hit_ratio_record_DB,utility_record_DB = dynamic_benchmark(request_list,request_list_summary,request_list_summary_times,cp_DB_set,user_set,cp_set)
print("done.")
print("saving data...")

import scipy.io as scio
import time
date = time.strftime('%Y.%m.%d %H.%M.%S',time.localtime(time.time()))
scio.savemat( date+".mat",
             {"cache_hit_ratio_record_TOC_S": cache_hit_ratio_record_TOC_S,"cache_hit_ratio_record_LRU":cache_hit_ratio_record_LRU,
              "cache_hit_ratio_record_LFU":cache_hit_ratio_record_LFU,"cache_hit_ratio_record_FIFO":cache_hit_ratio_record_FIFO,
              "utility_record_TOC_S":utility_record_TOC_S,"utility_record_LRU":utility_record_LRU,"utility_record_LFU":utility_record_LFU,
              "utility_record_FIFO":utility_record_FIFO,"cache_replace_frequency_TOC_S":cache_replace_frequency_TOC_S,
              "cache_replace_frequency_LRU": cache_replace_frequency_LRU, "cache_replace_frequency_LFU": cache_replace_frequency_LFU,
              "cache_replace_frequency_FIFO": cache_replace_frequency_FIFO,"cache_hit_ratio_record_DB":cache_hit_ratio_record_DB,
              "utility_record_DB":utility_record_DB,"cache_hit_ratio_record_SB":cache_hit_ratio_record_SB,
              "utility_record_SB":utility_record_SB})
