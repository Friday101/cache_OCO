
from src.cachePoint import *
from src.request import *
import numpy as np
import copy
import random
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
# 计算两点间的距离
def distance_2(node_1,node_2):
    d = np.sqrt( pow(node_1.x - node_2.x,2) + pow(node_1.y - node_2.y,2) )
    return d

# 齐夫分布 np里的参数必须要大于1
def zipf_distribution_sample(beta,max_index,min_index):
    p = []
    sum_x = 0
    for i in range(content_libaray_size):
        sum_x += pow(i+1,-beta)
    for i in range(content_libaray_size):
        p.append(pow(i+1, -beta)/sum_x)

    index = list(range(len(p)))
    sampled_index = random.choices(index, weights=p, k=1)[0]

    # p_tensor = torch.tensor(p)
    # sampled_index = p_tensor.multinomial(num_samples=content_libaray_size, replacement=False)[random.randint(0,content_libaray_size-1)]
    # while sampled_index > max_index or sampled_index < min_index:
    #     sampled_index = p_tensor.multinomial(num_samples=content_libaray_size, replacement=False)[random.randint(0,content_libaray_size-1)]
    return sampled_index


def cache_init(cp,user):
    capacity = cp.storageCapacity
    c = 0
    while c < capacity:
        random_content,random_bitrate = user.request.generateReqList()
        if c + random_bitrate*base_s*0.5 > capacity:
            break
        else:
            c += random_bitrate*base_s * 0.5
            cp.cacheStatus[random_content,random_bitrate] = 0.5
            if [random_content,random_bitrate] not in cp.cache_FIFO_history:
                cp.cache_FIFO_history.append([random_content,random_bitrate])
            if [random_content,random_bitrate] in cp.cache_LRU_queue:
                cp.cache_LRU_queue.remove([random_content,random_bitrate])
            cp.cache_LRU_queue.append([random_content,random_bitrate])
            if (random_content,random_bitrate) in cp.cache_LFU_dict.keys():
                cp.cache_LFU_dict[random_content,random_bitrate] += 1
            else:
                cp.cache_LFU_dict[random_content, random_bitrate] = 1

    cp.stored_space = c
    return cp.cacheStatus

# 转码开销
def transcode_utility(bitrate,request_bitrate,vartheta):
    # return pow(bitrate - request_bitrate, vartheta)
    return pow(bitrate - request_bitrate+1, vartheta)*nu

# 计算某个码率的效用
def cal_utility(cp,user,bitrate,request_amount):
    if bitrate > bitrateMaxLevel:
        return float('-inf'),0
    avaluable_amount = request_amount
    if cp.cacheStatus[user.request.req][user.request.bitrate] < request_amount:
        avaluable_amount = cp.cacheStatus[user.request.req][user.request.bitrate]
    # 乘码率0时为0.故+1
    utility = avaluable_amount * base_s * (user.request.bitrate+1) * (user.transmission_utility[cp.id][user.id] - transcode_utility(bitrate,user.request.bitrate,cp.computingCapacity) )
    return utility,avaluable_amount

def add_match_pool(cp,request_user,request_amount,matching_pool):
    cache_hit = False
    # 如果cp以前在匹配池里放过内容
    for i in matching_pool:
        if i[0] == cp.id:
            if i[1] > bitrateMaxLevel:
                return cache_hit # 超过码率上限不再改动
            else:
                i[1] += 1
                i[3],i[2] = cal_utility(cp,request_user,i[1],request_amount)
                if i[2] > 0:
                    cache_hit = True
                return cache_hit

    # 如果cp以前还没放过匹配池
    utility_cp = np.zeros(bitrateMaxLevel + 1)
    avaliable_amount_b = np.zeros(bitrateMaxLevel + 1)
    # cp根据请求排列路由效用
    for b in range(request_user.request.bitrate, bitrateMaxLevel + 1):
        utility_b, avaliable_amount = cal_utility(cp, request_user, b, request_amount)
        utility_cp[b] = utility_b
        avaliable_amount_b[b] = avaliable_amount
    max_utility_b = np.argmax(utility_cp)
    # CP id, 效用最大的码率, 路由量, 对应的效用
    if avaliable_amount_b[max_utility_b] > 0:
        cache_hit = True
        matching_pool.append([cp.id, max_utility_b, avaliable_amount_b[max_utility_b], utility_cp[max_utility_b]])
    return cache_hit

def route(cp_set,request_user,request_user_id,time_slot):
    Matching_Pool = []
    Routing_Result = []
    Routing_Amount = []
    cache_hit_t = True
    cache_hit_cp = []
    # 匹配池初始化
    for i in range(cp_num):
        if time_slot > 0:
            cp_set[i].cache_local_preference[time_slot] = copy.deepcopy(cp_set[i].cache_local_preference[time_slot-1])
        cp_set[i].cache_local_preference[time_slot, request_user.request.req, request_user.request.bitrate] += 1
        if request_user.linkMatrix[i, request_user_id] == 0:
            continue
        request_amount = 1 - sum(Routing_Amount)
        hit_cp_temp = add_match_pool(cp_set[i],request_user,request_amount,Matching_Pool)
        cache_hit_cp.append(hit_cp_temp)


    if Matching_Pool == []:
        # 无服务节点，从云端取
        cache_hit_t = False
        return Matching_Pool,Routing_Result,Routing_Amount,cache_hit_cp

    routed_amout = 0
    while routed_amout < 1:
        ### 匹配池产出路由结果
        best_route_utility = -1
        best_route_id = -1
        for i in range(len(Matching_Pool)):
            if Matching_Pool[i][1] > bitrateMaxLevel: #该节点已经无法提供服务
                continue
            if Matching_Pool[i][3]> best_route_utility:
                best_route_utility = Matching_Pool[i][3]
                best_route_id = i

        if best_route_utility == -1:
            # 没有缓存该内容，从云端取
            cache_hit_t = False
            break
        else:
            # 更新路由结果
            Routing_Amount.append(copy.deepcopy(Matching_Pool[best_route_id][2]))
            Routing_Result.append(copy.deepcopy(Matching_Pool[best_route_id]))
            routed_amout = sum(Routing_Amount)
            # 更新匹配池
            request_amount = 1 - sum(Routing_Amount)
            add_match_pool(cp_set[Matching_Pool[best_route_id][0]], request_user, request_amount, Matching_Pool)
    return Matching_Pool,Routing_Result,Routing_Amount,cache_hit_cp

def update_cache_least_popular(cp,update_amount):
    replace_flag = False
    if cp.stored_space > cp.storageCapacity:
        replace_flag = True
        update_done_flag = False
        for j in range(content_libaray_size - 1, -1, -1):
            for b in range(bitrateMaxLevel+1):
                if cp.cacheStatus[j][b] > 0:
                    if cp.cacheStatus[j][b] - update_amount >= 0:
                        cp.cacheStatus[j][b] -= update_amount  # over
                        cp.stored_space -= update_amount*base_s*(b+1)
                        if cp.stored_space <= cp.storageCapacity:
                            update_done_flag = True
                    else:
                        cp.cacheStatus[j][b] = 0
                        update_amount -= cp.cacheStatus[j][b]
                        cp.stored_space -= cp.cacheStatus[j][b]*base_s*(b+1)
                if update_done_flag:
                    break
            if update_done_flag:
                break
    return replace_flag