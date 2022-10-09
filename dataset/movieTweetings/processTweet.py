import pandas as pd
# names=['userId','movieId','rating', 'ratingTimestamp']
rowNum = 200000
targetUserNum = 100
ratingThresholdNum = 100
df = pd.read_csv('./ratings.dat', sep='::',
                 header=None, nrows=rowNum+1).values[0:]



movieScoreDict = {}
mapping = {}
def collectMovieStats():
    temp = {}
    for each in df:
        movieId = each[1]
        rating = float(each[2])
        if not temp.get(movieId):
            temp[movieId] = [rating]
        else:
            temp[movieId].append(rating)
            
    index = 1
    for each in temp:
        scoreList = temp[each]
        if len(scoreList)<ratingThresholdNum:
            continue
        mapping[each] = index
        index+=1
        movieScoreDict[each] = round(sum(scoreList)/len(scoreList),2)
    
collectMovieStats()
print(len(movieScoreDict))       
print(len(mapping)) 
        
userDict = {}
def getPreferenceList():
    for each in df:
        userId = each[0]
        movieId = each[1]
        # ratingTimestamp = each[3]
        
        if not movieScoreDict.get(movieId):
            continue
        
        # userDict
        if not userDict.get(userId):
            userDict[userId] = [mapping.get(movieId)]
        else:
            userDict[userId].append(mapping.get(movieId))
        if len(userDict) >= targetUserNum:
            print('统计结束')
            # return
            break
    
getPreferenceList()
print(userDict)


def writeIntoCsv():
    # movieScoreDict
    idList = [mapping[x] for x in list(movieScoreDict.keys())]
    scoreList = list(movieScoreDict.values())
    dataframe = pd.DataFrame({
        'movieId': idList,
        'avgScore': scoreList
    })
    dataframe.to_csv('./data/movieScore.csv', index=False)
    
    
    userIdList = list(userDict.keys())
    movieIdList = list(userDict.values())
    userDf = pd.DataFrame({
        'userId': userIdList,
        'likes': movieIdList
    })
    userDf.to_csv('./data/userLikes.csv', index=False)
    pass
    
writeIntoCsv()
        
    
    