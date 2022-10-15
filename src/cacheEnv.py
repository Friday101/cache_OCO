import random
import numpy as np
import torch

# scene
width = 500
high = 500

# user
user_density = 60  # 50
cp_density = 8  # 8


# random.poisson(lam=user_density) # numpy.random.poisson(user_density)
user_num = np.random.poisson(user_density, 1)[0]
cp_num = np.random.poisson(cp_density, 1)[0]  # random.poisson(lam=cp_density)

user_set = []
cp_set = []

# 执行时间
T = 10000  # 10000
# 通信半径
radius_r = 250  # 200

# 文件库大小
content_libaray_size = 60  # 50

# 基础传输效用
base_t = 0.3

# 基础媒体大小
base_s = 10

# content size
bitrateMinLevel = 0
bitrateMaxLevel = 5

# 转码开销控制因子
# vartheta = 2 # 控制计算资源对转码的影响
nu = 8  # 放缩因子

# 缓存空间设置
spaceMax = 6000  # 4000 # 5000
spaceMin = 800  # 600 # 800

# 计算资源设置
computeMax = 2
computeMin = 0


# 数据集
data_mode_set = ['zipf','movie_lens','movie_tweet','movie_comoda','movie_yahoo']
data_mode = data_mode_set[3]
# data_mode = 'zipf'
# data_mode = 'movie_lens'
# data_mode = 'movie_tweet'
# data_mode = 'movie_comoda'
# data_mode = 'movie_yahoo'

if data_mode == 'movie_lens':
    user_num = 100
    content_libaray_size = 135+1
elif data_mode == 'movie_tweet':
    user_num = 100
    content_libaray_size = 397+1
elif data_mode == 'movie_comoda':
    user_num = 120
    content_libaray_size = 1232+1
elif data_mode == 'movie_yahoo':
    user_num = 100
    content_libaray_size = 107+1


################## 数据记录 #################
cache_hit_ratio_record_TOC_S = []
cache_hit_ratio_record_TOC_S_transcode = []
cache_hit_ratio_record_TOC_S_direct = []
utility_record_TOC_S = []
cache_replace_frequency_TOC_S = []

cache_hit_ratio_record_TOC_E = []
cache_hit_ratio_record_TOC_E_transcode = []
cache_hit_ratio_record_TOC_E_direct = []
utility_record_TOC_E = []
cache_replace_frequency_TOC_E = []
constraint_violation_g_1_TOC_E = []
constraint_violation_g_2_TOC_E = []

cache_hit_ratio_record_LRU = []
cache_hit_ratio_record_LRU_transcode = []
cache_hit_ratio_record_LRU_direct = []
utility_record_LRU = []
cache_replace_frequency_LRU = []

cache_hit_ratio_record_LFU = []
cache_hit_ratio_record_LFU_transcode = []
cache_hit_ratio_record_LFU_direct = []
utility_record_LFU = []
cache_replace_frequency_LFU = []

cache_hit_ratio_record_FIFO = []
cache_hit_ratio_record_FIFO_transcode = []
cache_hit_ratio_record_FIFO_direct = []
utility_record_FIFO = []
cache_replace_frequency_FIFO = []