
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
    utility = avaluable_amount * base_s * (user.request.bitrate+1) * (user.transmission_utility[cp.id][user.id] - transcode_utility(bitrate,user.request.bitrate,cp.computed_frequency) )
    return utility,avaluable_amount

def add_match_pool(cp,request_user,request_amount,matching_pool):
    cache_hit = False
    cache_hit_transcode = False
    cache_hit_direct = False

    # 如果cp以前在匹配池里放过内容
    ### 效用梯度    # CP id, 效用最大的码率, 路由量, 对应的效用
    for i in matching_pool:
        if i[0] == cp.id:
            if i[1] > bitrateMaxLevel:
                return False,False,False # 超过码率上限不再改动
            else:
                i[1] += 1
                i[3],i[2] = cal_utility(cp,request_user,i[1],request_amount)
                if i[2] > 0:
                    cache_hit = True
                    cache_hit_transcode = True
                    cache_hit_direct = False
                return cache_hit,cache_hit_transcode,cache_hit_direct

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
        if request_user.request.bitrate == max_utility_b:
            cache_hit_transcode = False
            cache_hit_direct = True
        else:
            cache_hit_transcode = True
            cache_hit_direct = False
    else:
        cache_hit = False
        cache_hit_transcode = False
        cache_hit_direct = False
    return cache_hit,cache_hit_transcode,cache_hit_direct

def route(cp_set,request_user,request_user_id,time_slot):
    Matching_Pool = []
    Routing_Result = []
    Routing_Amount = []
    cache_hit_t = True
    cache_hit_cp = []
    cache_hit_cp_transcode = []
    cache_hit_cp_direct = []

    # 匹配池初始化
    for i in range(cp_num):
        if time_slot > 0:
            cp_set[i].cache_local_preference[time_slot] = copy.deepcopy(cp_set[i].cache_local_preference[time_slot-1])
        cp_set[i].cache_local_preference[time_slot, request_user.request.req, request_user.request.bitrate] += 1
        if request_user.linkMatrix[i, request_user_id] == 0:
            continue
        request_amount = 1 - sum(Routing_Amount)
        hit_cp_temp,hit_cp_transcode_temp,hit_cp_direct_temp= add_match_pool(cp_set[i],request_user,request_amount,Matching_Pool)
        cache_hit_cp.append(hit_cp_temp)
        cache_hit_cp_transcode.append(hit_cp_transcode_temp)
        cache_hit_cp_direct.append(hit_cp_direct_temp)


    if Matching_Pool == []:
        # 无服务节点，从云端取
        cache_hit_t = False
        return Matching_Pool,Routing_Result,Routing_Amount,cache_hit_cp,cache_hit_cp_transcode,cache_hit_cp_direct

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
            hit_cp_temp, hit_cp_transcode_temp, hit_cp_direct_temp = add_match_pool(cp_set[Matching_Pool[best_route_id][0]], request_user, request_amount, Matching_Pool)
            cache_hit_cp.append(hit_cp_temp)
            cache_hit_cp_transcode.append(hit_cp_transcode_temp)
            cache_hit_cp_direct.append(hit_cp_direct_temp)
    return Matching_Pool,Routing_Result,Routing_Amount,cache_hit_cp,cache_hit_cp_transcode,cache_hit_cp_direct

def actual_amount_cal(cp):
    actual_amount = 0.0
    for i in range(cp.cacheStatus.shape[0]):
        for j in range(cp.cacheStatus.shape[1]):
            actual_amount += cp.cacheStatus[i][j] * base_s * (j + 1)
    actual_amount = round(actual_amount,2)
    return actual_amount

def update_cache_least_popular(cp,update_amount):
    replace_flag = False
    # actual_amount = actual_amount_cal(cp)
    # print("Update-1    actual:" + str(actual_amount) + "---now storage space:" + str(
    #     cp.stored_space) + "---now storageCapacity" + str(cp.storageCapacity))
    # if abs(cp.stored_space - actual_amount_cal(cp)) > 100:
    #     print("error-1")
    # print("update1")
    while cp.stored_space > cp.storageCapacity:
        # print("update2")
        replace_flag = True
        # cp.cacheStatus > 0 nb[0]行 nb[1]列
        nb = np.where(np.array(cp.cacheStatus) > 0)
        n = 10
        average_amount_update = round(update_amount/n,2) #len(nb[0])
        cp.nb_len.append(len(nb[0]))
        # if len(cp.nb_len) > 5:
        #     if cp.nb_len[-1] - cp.nb_len[-2] < 0:
        #         ## 实际存储大小
        #         print("loss nb len"+str(cp.nb_len[-1]))
                # actual_amount = actual_amount_cal(cp)

        # actual_amount = actual_amount_cal(cp)
        # print("Update0    actual:" + str(actual_amount) + "---now storage space:" + str(
        #     cp.stored_space) + "---now storageCapacity" + str(cp.storageCapacity)+"diff:"+str(cp.stored_space-actual_amount))


        own_amount = 0
        for i in range(n):
            if cp.stored_space <= cp.storageCapacity:
                break
            index = random.randint(0,len(nb[0])-1)

            # actual_amount = actual_amount_cal(cp)
            # print("Update1    actual:" + str(actual_amount) + "---now storage space:" + str(
            #     cp.stored_space) + "---now storageCapacity" + str(cp.storageCapacity) + "diff:" + str(
            #     cp.stored_space - actual_amount))
            # print("cacheStatus:"+str(cp.cacheStatus[nb[0][index],nb[1][index]])+"---average_amount_update:"+str(average_amount_update))
            if cp.cacheStatus[nb[0][index],nb[1][index]] >= average_amount_update:
                #b = copy.deepcopy(cp.cacheStatus[nb[0][index],nb[1][index]])
                cp.cacheStatus[nb[0][index],nb[1][index]] -= average_amount_update
                #b2 = copy.deepcopy(cp.cacheStatus[nb[0][index],nb[1][index]])

                #a = copy.deepcopy(cp.stored_space)
                cp.stored_space -= average_amount_update * base_s * (nb[1][index] + 1)
                cp.stored_space = round(cp.stored_space,2)
                #a2 = copy.deepcopy(cp.stored_space)

                # actual_amount = actual_amount_cal(cp)
                # print("Update2    actual:" + str(actual_amount) + "---now storage space:" + str(
                #     cp.stored_space) + "---now storageCapacity" + str(cp.storageCapacity) + "diff:" + str(
                #     cp.stored_space - actual_amount))

                # if cp.stored_space - actual_amount_cal(cp) > 0:
                #     print("Catch it")
                #     actual_amount = actual_amount_cal(cp)
                #     print("Update3    actual:" + str(actual_amount) + "---now storage space:" + str(
                #         cp.stored_space) + "---now storageCapacity" + str(cp.storageCapacity) + "diff:" + str(
                #         cp.stored_space - actual_amount))
                #     print(str(a)+"---"+str(a2))
                #     print(str(b) + "-"+str(average_amount_update)+"=" + str(b2))
                #     print("-----------------")

                # actual_amount = actual_amount_cal(cp)
                # print("Update1    actual:" + str(actual_amount) + "---now storage space:" + str(
                #     cp.stored_space) + "---now storageCapacity" + str(cp.storageCapacity))
                # if abs( cp.stored_space - actual_amount_cal(cp) ) > 100:
                #     print("error1")
                # print("own_amount:"+str(own_amount))
                if own_amount == 0:
                    continue
                if cp.cacheStatus[nb[0][index], nb[1][index]] > own_amount:
                    cp.cacheStatus[nb[0][index], nb[1][index]] -= own_amount
                    cp.stored_space -= round(own_amount * base_s * (nb[1][index] + 1),2)
                    own_amount = 0
            else:
                own_amount += average_amount_update - cp.cacheStatus[nb[0][index],nb[1][index]]
                cp.stored_space -= round(cp.cacheStatus[nb[0][index], nb[1][index]] * base_s * (nb[1][index] + 1), 2)
                cp.cacheStatus[nb[0][index], nb[1][index]] = 0

        if cp.stored_space > cp.storageCapacity:
            update_amount = 0.3


        # for j in range(content_libaray_size - 1, -1, -1):
        #     for b in range(bitrateMaxLevel+1):
        #         if cp.cacheStatus[j][b] > 0:
        #             if cp.cacheStatus[j][b] - update_amount >= 0:
        #                 cp.cacheStatus[j][b] -= update_amount  # over
        #                 cp.stored_space -= update_amount*base_s*(b+1)
        #                 if cp.stored_space <= cp.storageCapacity:
        #                     update_done_flag = True
        #             else:
        #                 cp.cacheStatus[j][b] = 0
        #                 update_amount -= cp.cacheStatus[j][b]
        #                 cp.stored_space -= cp.cacheStatus[j][b]*base_s*(b+1)
        #         if update_done_flag:
        #             break
        #     if update_done_flag:
        #         break
    return replace_flag