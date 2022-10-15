import math

import numpy as np

from src.cachePoint import *
from src.request import *
import numpy
import random
import copy
from src.tools import *
from src.cacheEnv import *

# TOC-S
def TOC_S(cp_set,request_user,route_result,time_slot):
    i = route_result
    ### 效用梯度    # CP id, 效用最大的码率, 路由量, 对应的效用
    supergradient_f_t = request_user.transmission_utility[cp_set[i[0]].id][request_user.id] \
                        - transcode_utility(i[1], request_user.request.bitrate, cp_set[i[0]].computingCapacity)

    ### 步长 eta
    Delta_x = math.sqrt(2 * cp_set[i[0]].storageCapacity)
    J = request_user.transmission_utility[cp_set[i[0]].id][request_user.id]
    eta = Delta_x / (J * math.sqrt(time_slot))

    # actual_amount = actual_amount_cal(cp_set[i[0]])
    # print("TOC-S1    actual:"+str(actual_amount)+"---now storage space:"+str(cp_set[i[0]].stored_space)+"---now storageCapacity"+str(cp_set[i[0]].storageCapacity))
    # if abs(cp_set[i[0]].stored_space - actual_amount_cal(cp_set[i[0]])) > 100: # 0.0000000000001
    #     print("error3")

    ### 更新
    update_amount = round(eta * supergradient_f_t,2)
    tmp_record = copy.deepcopy(cp_set[i[0]].cacheStatus[request_user.request.req][i[1] ])
    cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] += update_amount

    ### 投影
    update_amount_2 = update_amount
    if cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] < 0:
        cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] = 0
        cp_set[i[0]].stored_space -= tmp_record * base_s * (i[1] + 1)
        # print("project1")
        # actual_amount = actual_amount_cal(cp_set[i[0]])
        # print("TOC-S1    actual:" + str(actual_amount) + "---now storage space:" + str(
        #     cp_set[i[0]].stored_space) + "---now storageCapacity" + str(cp_set[i[0]].storageCapacity)+"diff:"+str(cp_set[i[0]].stored_space-actual_amount))
    elif cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] > 1:
        update_amount_2 = round(1 - tmp_record,2)
        cp_set[i[0]].stored_space += update_amount_2*base_s*(i[1]+1)
        cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] = 1
        # print("project2")
        # actual_amount = actual_amount_cal(cp_set[i[0]])
        # print("TOC-S12    actual:" + str(actual_amount) + "---now storage space:" + str(
        #     cp_set[i[0]].stored_space) + "---now storageCapacity" + str(cp_set[i[0]].storageCapacity)+"diff:"+str(cp_set[i[0]].stored_space-actual_amount))
    else:
        cp_set[i[0]].stored_space += update_amount_2 * base_s * (i[1]+1)
        # print("project3")
        # actual_amount = actual_amount_cal(cp_set[i[0]])
        # print("TOC-S13    actual:" + str(actual_amount) + "---now storage space:" + str(
        #     cp_set[i[0]].stored_space) + "---now storageCapacity" + str(cp_set[i[0]].storageCapacity)+"diff:"+str(cp_set[i[0]].stored_space-actual_amount))


    # actual_amount = actual_amount_cal(cp_set[i[0]])
    # print("TOC-S2    actual:"+str(actual_amount)+"---now storage space:"+str(cp_set[i[0]].stored_space)+"---now storageCapacity"+str(cp_set[i[0]].storageCapacity))
    # if abs(cp_set[i[0]].stored_space - actual_amount_cal(cp_set[i[0]])) > 100:
    #     print("error4")

    ##### 最不受欢迎的内容存储量对应减少
    replace_flag = update_cache_least_popular(cp_set[i[0]],update_amount_2)
    return replace_flag


def TOC_E(cp_set,request_user,route_result,time_slot):
    # 动态约束条件
    i = route_result

    ### 步长 eta
    Delta_x = math.sqrt(2 * cp_set[i[0]].storageCapacity)
    # J = request_user.transmission_utility[cp_set[i[0]].id][request_user.id]
    eta = math.sqrt( Delta_x / time_slot )  # (J * math.sqrt(time_slot))

    delta = 5 * pow( cp_set[i[0]].cacheStatus[request_user.request.req,request_user.request.bitrate] ,2)

    ### 效用梯度    # CP id, 效用最大的码率, 路由量, 对应的效用
    supergradient_f_t = request_user.transmission_utility[cp_set[i[0]].id][request_user.id] \
                        - transcode_utility(i[1], request_user.request.bitrate, cp_set[i[0]].computingCapacity)

    # 方案1
    gradient_g_1_t = cp_set[i[0]].lambda_1 * base_s * request_user.request.bitrate
    gradient_g_2_t = cp_set[i[0]].lambda_2 * i[2] * transcode_utility(i[1], request_user.request.bitrate, cp_set[i[0]].computingCapacity)
    gradient_x_t = supergradient_f_t + gradient_g_1_t + gradient_g_2_t
    gradient_lambda_1_t = cp_set[i[0]].cacheStatus[request_user.request.req,request_user.request.bitrate] * base_s * request_user.request.bitrate - cp_set[i[0]].Constraint_C[time_slot-1] - eta * cp_set[i[0]].lambda_1 * delta
    gradient_lambda_2_t = i[2] * base_s * request_user.request.bitrate * transcode_utility(i[1], request_user.request.bitrate, cp_set[i[0]].computingCapacity) - cp_set[i[0]].Constraint_H[time_slot-1] - eta * cp_set[i[0]].lambda_2 * delta

    # 方案2
    # gradient_g_1_t = cp_set[i[0]].lambda_1[request_user.request.req,request_user.request.bitrate] * base_s * request_user.request.bitrate
    # gradient_g_2_t = cp_set[i[0]].lambda_2[request_user.request.req,request_user.request.bitrate] * i[2] * transcode_utility(i[1], request_user.request.bitrate, cp_set[i[0]].computingCapacity)
    # gradient_x_t = supergradient_f_t + gradient_g_1_t + gradient_g_2_t
    # gradient_lambda_1_t = cp_set[i[0]].cacheStatus[request_user.request.req,request_user.request.bitrate] * base_s * request_user.request.bitrate - cp_set[i[0]].Constraint_C[time_slot] - eta * cp_set[i[0]].lambda_1[request_user.request.req,request_user.request.bitrate] * delta
    # gradient_lambda_2_t = i[2] * base_s * request_user.request.bitrate * transcode_utility(i[1], request_user.request.bitrate, cp_set[i[0]].computingCapacity) - cp_set[i[0]].Constraint_H[time_slot]  - eta * cp_set[i[0]].lambda_2[request_user.request.req,request_user.request.bitrate] * delta

    # 约束违反状况
    g_1 = cp_set[i[0]].stored_space - cp_set[i[0]].Constraint_C[time_slot-1]
    g_2 = i[2] * base_s * request_user.request.bitrate * transcode_utility(i[1], request_user.request.bitrate, cp_set[i[0]].computingCapacity) - cp_set[i[0]].Constraint_H[time_slot-1]
    cp_set[i[0]].Constraint_Violation_C[time_slot-1] = g_1
    cp_set[i[0]].Constraint_Violation_H[time_slot-1] = g_2

    # actual_amount = actual_amount_cal(cp_set[i[0]])
    # print("TOC-E1    actual:"+str(actual_amount)+"---now storage space:"+str(cp_set[i[0]].stored_space)+"---now storageCapacity"+str(cp_set[i[0]].storageCapacity))
    # if abs(cp_set[i[0]].stored_space - actual_amount_cal(cp_set[i[0]])) > 5:
    #     print("error1")

    ### 缓存变量更新
    update_amount = eta * gradient_x_t
    tmp_record = copy.deepcopy(cp_set[i[0]].cacheStatus[request_user.request.req][i[1]])
    cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] += update_amount

    ### 对偶变量更新
    ##### 方案1
    cp_set[i[0]].lambda_1 = cp_set[i[0]].lambda_1 + eta * gradient_lambda_1_t
    cp_set[i[0]].lambda_2 = cp_set[i[0]].lambda_2 + eta * gradient_lambda_2_t

    cp_set[i[0]].lambda_1_list.append( cp_set[i[0]].lambda_1 )
    cp_set[i[0]].lambda_2_list.append(cp_set[i[0]].lambda_2)

    # actual_amount = actual_amount_cal(cp_set[i[0]])
    # print("TOC-E2    actual:"+str(actual_amount)+"---now storage space:"+str(cp_set[i[0]].stored_space)+"---now storageCapacity"+str(cp_set[i[0]].storageCapacity))
    # if abs(cp_set[i[0]].stored_space - actual_amount_cal(cp_set[i[0]])) > 5:
    #     print("error2")

    ##### 方案2
    # cp_set[i[0]].lambda_1[request_user.request.req,request_user.request.bitrate] = cp_set[i[0]].lambda_1[request_user.request.req,request_user.request.bitrate] + eta * gradient_lambda_1_t
    # cp_set[i[0]].lambda_2[request_user.request.req,request_user.request.bitrate] = cp_set[i[0]].lambda_2[request_user.request.req,request_user.request.bitrate] + eta * gradient_lambda_2_t

    ### 投影
    update_amount_2 = update_amount
    if cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] < 0:
        cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] = 0
        cp_set[i[0]].stored_space -= tmp_record * base_s * (i[1] + 1)
        # print("project E-1")
    elif cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] > 1:
        update_amount_2 = 1 - tmp_record
        cp_set[i[0]].stored_space += update_amount_2 * base_s * (i[1] + 1)
        cp_set[i[0]].cacheStatus[request_user.request.req][i[1]] = 1
        # print("project E-2")
    else:
        cp_set[i[0]].stored_space += update_amount_2 * base_s * (i[1] + 1)
        # print("project E-3")

    # actual_amount = actual_amount_cal(cp_set[i[0]])
    # print("TOC-E3    actual:"+str(actual_amount)+"---now storage space:"+str(cp_set[i[0]].stored_space)+"---now storageCapacity"+str(cp_set[i[0]].storageCapacity))
    # if abs(cp_set[i[0]].stored_space - actual_amount_cal(cp_set[i[0]])) > 5:
    #     print("error3")

    ##### 最不受欢迎的内容存储量对应减少
    replace_flag = update_cache_least_popular(cp_set[i[0]], update_amount_2)
    return replace_flag,g_1,g_2

# LRU 最近频繁使用 强调使用时间
def LRU(cp_set,request_user,route_result,time_slot):
    # 缓存更新
    new_download_amount = 1 - cp_set[route_result[0]].cacheStatus[request_user.request.req,request_user.request.bitrate]
    cp_set[route_result[0]].cacheStatus[request_user.request.req, request_user.request.bitrate] = 1
    cp_set[route_result[0]].stored_space += new_download_amount * base_s * (request_user.request.bitrate+1)

    replace_flag = False
    # 缓存替换
    while cp_set[route_result[0]].stored_space + new_download_amount*base_s*(route_result[1]+1) > cp_set[route_result[0]].storageCapacity:
        # 队首弹出，最久未使用
        evicted_content = cp_set[route_result[0]].cache_LRU_queue[0]
        cp_set[route_result[0]].stored_space -= cp_set[route_result[0]].cacheStatus[evicted_content[0],evicted_content[1]]*base_s*(evicted_content[1]+1)
        cp_set[route_result[0]].cacheStatus[evicted_content[0], evicted_content[1]] = 0
        cp_set[route_result[0]].cache_LRU_queue[0:-1] = cp_set[route_result[0]].cache_LRU_queue[1:]
        cp_set[route_result[0]].cache_LRU_queue.pop()
        replace_flag = True

    # LRU队列更新
    if [request_user.request.req,request_user.request.bitrate] in cp_set[route_result[0]].cache_LRU_queue:
        cp_set[route_result[0]].cache_LRU_queue.remove([request_user.request.req,request_user.request.bitrate])
    cp_set[route_result[0]].cache_LRU_queue.append([request_user.request.req,request_user.request.bitrate])
    return replace_flag


# LFU 最不经常使用 # 强调使用频率
def LFU(cp_set, request_user, route_result, time_slot):
    # 缓存更新
    new_download_amount = 1 - cp_set[route_result[0]].cacheStatus[request_user.request.req,request_user.request.bitrate]
    cp_set[route_result[0]].cacheStatus[request_user.request.req, request_user.request.bitrate] = 1
    cp_set[route_result[0]].stored_space += new_download_amount * base_s * (request_user.request.bitrate+1)

    # 缓存替换
    replace_flag = False
    while cp_set[route_result[0]].stored_space + new_download_amount*base_s*(route_result[1]+1) > cp_set[route_result[0]].storageCapacity:
        # 频率最少弹出
        evicted_content = sorted(cp_set[route_result[0]].cache_LFU_dict.items(), key=lambda x: x[1], reverse=False)[0][0]
        cp_set[route_result[0]].stored_space -= cp_set[route_result[0]].cacheStatus[evicted_content[0],evicted_content[1]]*base_s*(evicted_content[1]+1)
        cp_set[route_result[0]].cacheStatus[evicted_content[0], evicted_content[1]] = 0
        cp_set[route_result[0]].cache_LFU_dict.pop(evicted_content)
        replace_flag = True

    # LFU字典更新
    if (request_user.request.req,request_user.request.bitrate) in cp_set[route_result[0]].cache_LFU_dict.keys():
        cp_set[route_result[0]].cache_LFU_dict[request_user.request.req,request_user.request.bitrate] += 1
    else:
        cp_set[route_result[0]].cache_LFU_dict[request_user.request.req,request_user.request.bitrate] = 1
    return replace_flag

# FIFO 先入先出
def FIFO(cp_set,request_user,route_result,time_slot):
    # 缓存更新
    new_download_amount = 1 - cp_set[route_result[0]].cacheStatus[request_user.request.req,request_user.request.bitrate]
    cp_set[route_result[0]].cacheStatus[request_user.request.req, request_user.request.bitrate] = 1
    cp_set[route_result[0]].stored_space += new_download_amount * base_s * (request_user.request.bitrate+1)

    replace_flag = False
    # 缓存替换
    while cp_set[route_result[0]].stored_space + new_download_amount*base_s*(route_result[1]+1) > cp_set[route_result[0]].storageCapacity:
        # 首先进入的弹出
        evicted_content = cp_set[route_result[0]].cache_FIFO_history[0]
        cp_set[route_result[0]].stored_space -= cp_set[route_result[0]].cacheStatus[evicted_content[0],evicted_content[1]]*base_s*(evicted_content[1]+1)
        cp_set[route_result[0]].cacheStatus[evicted_content[0], evicted_content[1]] = 0
        cp_set[route_result[0]].cache_FIFO_history[0:-1] = cp_set[route_result[0]].cache_FIFO_history[1:]
        cp_set[route_result[0]].cache_FIFO_history.pop()
        replace_flag = True

    # FIFO数组更新
    if [request_user.request.req,request_user.request.bitrate] not in cp_set[route_result[0]].cache_FIFO_history:
        cp_set[route_result[0]].cache_FIFO_history.append([request_user.request.req,request_user.request.bitrate])

    return replace_flag


def static_benchmark(request_list,request_list_summary,request_list_summary_times,cp_set,user_set,cp_o_set):
    t = 0
    cache_hit_ratio_record_SB = []
    cache_hit_ratio_record_SB_transcode = []
    cache_hit_ratio_record_SB_direct = []
    utility_record_SB = []
    # 缓存决策 - 静态
    for i in cp_set:
        preference_T = copy.deepcopy(cp_o_set[i.id].cache_local_preference[T - 1])
        best_index = np.argmax(preference_T)
        index_row = int(best_index / preference_T.shape[1])
        index_col = best_index % preference_T.shape[1]

        updated_amount = 1 - i.cacheStatus[index_row, index_col]
        while i.stored_space + updated_amount * base_s * (index_col + 1) <= i.storageCapacity:
            i.cacheStatus[index_row, index_col] = 1
            i.stored_space += updated_amount * base_s * (index_col + 1)
            preference_T[index_row, index_col] = -1
            best_index = np.argmax(preference_T)
            index_row = int(best_index / preference_T.shape[1])
            index_col = best_index % preference_T.shape[1]

    while t < T:
        # print("----------Time slot - " + str(t) + "----------")
        # 计算当前时隙效用
        user_set[request_list[t][0]].request.req = request_list[t][1]
        user_set[request_list[t][0]].request.bitrate = request_list[t][2]
        Matching_Pool_SB, Routing_Result_SB, Routing_Amount_SB, cache_hit_t_SB,cache_hit_t_transcode_SB, cache_hit_t_direct_SB = route(cp_set,
                                                                                       user_set[request_list[t][0]],
                                                                                       request_list[t][0], t)
        if len(cache_hit_t_SB) > 0:
            cache_hit_ratio_record_SB.append(sum(cache_hit_t_SB) / len(cache_hit_t_SB))
            cache_hit_ratio_record_SB_transcode.append(sum(cache_hit_t_transcode_SB) / len(cache_hit_t_transcode_SB))
            cache_hit_ratio_record_SB_direct.append(sum(cache_hit_t_direct_SB) / len(cache_hit_t_direct_SB))
        else:
            cache_hit_ratio_record_SB.append(0)
            cache_hit_ratio_record_SB_transcode.append(0)
            cache_hit_ratio_record_SB_direct.append(0)

        if not cache_hit_ratio_record_SB[-1]:
            utility_record_SB.append(0)
        else:
            utility_t = 0
            for i in Routing_Result_SB:
                utility_t += i[3]
            utility_record_SB.append(utility_t)

        t+=1

    return cache_hit_ratio_record_SB,utility_record_SB,cache_hit_ratio_record_SB_transcode,cache_hit_ratio_record_SB_direct

# 在t时刻缓存今后能取得最大收益的内容    可以进一步记录regret水平
def dynamic_benchmark(request_list,request_list_summary,request_list_summary_times,cp_set,user_set,cp_o_set):
    #
    t = 0
    cache_hit_ratio_record_DB = []
    cache_hit_ratio_record_DB_transcode = []
    cache_hit_ratio_record_DB_direct = []

    utility_record_DB = []
    cache_replace_frequency_DB = []
    replace_flag_DB = False
    while t < T:
        # print("----------Time slot - " + str(t) + "----------")
        # 计算当前时隙效用
        user_set[request_list[t][0]].request.req = request_list[t][1]
        user_set[request_list[t][0]].request.bitrate = request_list[t][2]
        Matching_Pool_DB, Routing_Result_DB, Routing_Amount_DB, cache_hit_t_DB,cache_hit_t_transcode_DB, cache_hit_t_direct_DB = route(cp_set,user_set[request_list[t][0]],request_list[t][0],t)
        if len(cache_hit_t_DB) > 0:
            cache_hit_ratio_record_DB.append(sum(cache_hit_t_DB) / len(cache_hit_t_DB))
            cache_hit_ratio_record_DB_transcode.append(sum(cache_hit_t_transcode_DB) / len(cache_hit_t_transcode_DB))
            cache_hit_ratio_record_DB_direct.append(sum(cache_hit_t_direct_DB) / len(cache_hit_t_direct_DB))
        else:
            cache_hit_ratio_record_DB.append(0)
            cache_hit_ratio_record_DB_transcode.append(0)
            cache_hit_ratio_record_DB_direct.append(0)

        if not cache_hit_ratio_record_DB[-1]:
            utility_record_DB.append(0)
        else:
            utility_t = 0
            for i in Routing_Result_DB:
                utility_t += i[3]
            utility_record_DB.append(utility_t)

        # 缓存更新 方案3 缓存下一时隙的内容
        if t+1 < T:
            for i in cp_set:
                if i.linkMatrix[i.id,request_list[t+1][0]] == 1:
                    cache_content = request_list[t+1][1]
                    cache_bitrate = request_list[t+1][2]
                    updated_amount = 1- i.cacheStatus[cache_content,cache_bitrate]
                    i.stored_space += updated_amount * base_s * (cache_bitrate+1)
                    i.cacheStatus[cache_content, cache_bitrate] = 1
                    if i.stored_space + updated_amount * base_s * (cache_bitrate+1) > i.storageCapacity:
                        replace_flag_DB = update_cache_least_popular(i,updated_amount)

        cache_replace_frequency_DB.append( replace_flag_DB )
        t+=1

        # 缓存更新 方案1 所有cp按后面的请求频率缓存内容 初期效果好，后期越来越差
        # for i in cp_set:
        #     cache_down_flag = False
        #     request_list_summary_times_copy = copy.deepcopy(request_list_summary_times[t:])
        #     request_list_summary_copy = copy.deepcopy(request_list_summary[t:])
        #     # i.cacheStatus = np.zeros((content_libaray_size,bitrateMaxLevel-bitrateMinLevel+1))
        #     while not cache_down_flag:
        #         if len(request_list_summary_copy) == 0:
        #             break
        #         max_times_index = request_list_summary_times_copy.index(max(request_list_summary_times_copy))
        #         max_times_request = request_list_summary_copy[max_times_index]
        #         i.cacheStatus[max_times_request[0], max_times_request[1]] = 1
        #         i.stored_space += 1 * base_s * (max_times_request[1]+1)
        #         if i.stored_space + 1 * base_s * (max_times_request[1]+1) > i.storageCapacity:
        #             update_cache_least_popular(i,1)
        #             cache_down_flag = True
        #         request_list_summary_copy.remove(max_times_request)
        #         request_list_summary_times_copy[max_times_index:-1] = request_list_summary_times_copy[
        #                                                               max_times_index + 1:]
        #         request_list_summary_times_copy.pop()
                
        # 缓存更新 方案2 针对性更新 效果并不好，因为考虑的还是长期的，短期存在不命中的可能，导致效用低
        # for i in cp_set:
        #     preference_t = copy.deepcopy(cp_o_set[i.id].cache_local_preference[t])
        #     preference_T = copy.deepcopy(cp_o_set[i.id].cache_local_preference[T-1])
        #     preference_compute = preference_T - preference_t
        #     best_index = np.argmax(preference_compute)
        #     index_row = int( int(best_index) / preference_compute.shape[1] )
        #     index_col = best_index % preference_compute.shape[1]
        #     while i.stored_space + 1 * base_s * (index_col+1) <= i.storageCapacity:
        #         i.cacheStatus[index_row, index_col] = 1
        #         i.stored_space += 1 * base_s * (index_col+1)
        #         preference_compute[index_row,index_col] = -1
        #
        #         best_index = np.argmax(preference_compute)
        #         index_row = int(best_index / preference_compute.shape[0])
        #         index_col = best_index % preference_compute.shape[1]
    return cache_hit_ratio_record_DB,utility_record_DB,cache_replace_frequency_DB,cache_hit_ratio_record_DB_transcode,cache_hit_ratio_record_DB_direct
