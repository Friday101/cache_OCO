from this import d
import numpy as np
import random
from src.cacheEnv import *
from src.tools import *
# max就是K 内容库

# import pandas as pd
# df = pd.read_csv('../dataset/movieLens/data/userLikes.csv', header=None).values[0:]
# print(df)
import pandas as pd
lens_df = pd.read_csv(
    'dataset/movieLens/data/userLikes.csv', header=None).values[1:]
tweet_df = pd.read_csv(
    'dataset/movieTweetings/data/userLikes.csv', header=None).values[1:]
comoda_df = pd.read_csv(
    'dataset/CoMoDa/data/userLikes.csv', header=None).values[1:]
yahoo_df = pd.read_csv(
    'dataset/yahoo/data/userLikes.csv', header=None).values[1:]


req_lens = {}
for each in lens_df:
    id = int(each[0])
    _temp = (each[1][1:-1]).split(', ')
    likesList = [int(x) for x in _temp]
    req_lens[id] = likesList

req_tweet = {}
for each in tweet_df:
    id = int(each[0])
    _temp = (each[1][1:-1]).split(', ')
    likesList = [int(x) for x in _temp]
    req_tweet[id] = likesList
     
req_comoda = {}
for each in comoda_df:
    id = int(each[0])
    _temp = (each[1][1:-1]).split(', ')
    likesList = [int(x) for x in _temp]
    req_comoda[id] = likesList
# print(req_lens)
# print(req_tweet)
# print(req_comoda)
req_yahoo = {}
for each in yahoo_df:
    id = int(each[0])
    _temp = (each[1][1:-1]).split(', ')
    likesList = [int(x) for x in _temp]
    req_yahoo[id] = likesList


class User:
    def __init__(self, id, x, y, zipf_p, mode='zipf') -> None:
        self.x = x
        self.y = y
        self.id = id
        self.zipf_p = zipf_p
        self.linkMatrix = np.zeros((cp_num, user_num))
        self.transmission_utility = np.zeros((cp_num, user_num))
        if mode == 'zipf':
            self.request = UserRequest(zipf_p)
        else:
            self.request = MovieDataRequest(self.id, mode)


class UserRequest:
    def __init__(self, zipf_p, min=0, max=content_libaray_size-1):
        self.min = min
        self.max = max
        self.zipf_p = zipf_p
        # current slot req bitrate
        self.req, self.bitrate = self.generateReqList()

    def generateReqList(self, mode='zipf', id=-1):
        # zipf分布
        temp_content = zipf_distribution_sample(
            self.zipf_p, self.max, self.min)
        temp_bitrate = random.randint(bitrateMinLevel, bitrateMaxLevel)
        self.req = temp_content
        self.bitrate = temp_bitrate
        return temp_content, temp_bitrate



class MovieDataRequest:
    def __init__(self, user_id, mode):
        self.min = min
        self.max = max
        # current slot req bitrate
        self.req, self.bitrate = self.generateReqList(mode, user_id)

    def generateReqList(self, mode, user_id):
        if mode == 'movie_lens':
            temp_content = random.choice(req_lens[user_id])
        elif mode == 'movie_tweet':
            temp_content = random.choice(req_tweet[user_id])
        elif mode == 'movie_comoda':
            temp_content = random.choice(req_comoda[user_id])
        elif mode == 'movie_yahoo':
            temp_content = random.choice(req_yahoo[user_id])
            
        temp_bitrate = random.randint(bitrateMinLevel, bitrateMaxLevel)
        self.req = temp_content
        self.bitrate = temp_bitrate
        return temp_content, temp_bitrate
