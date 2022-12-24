import time
class SessionMap(object):
    # 不想实现LRU了，直接每次满了删最小时间戳
    def __init__(self, capcity, expireTime):
        self.capacity = capcity
        self.expireTime = expireTime
        self.GameMap = dict()

    def getGameBySessionID(self, sessionID):
        game = self.GameMap.get(sessionID, False)
        return game

    def createGame(self, Game, sessionID):
        if self.GameMap.__len__() >= self.capacity:
            self.delOldestSession() 
        self.GameMap[sessionID] = (Game, int(time.time()))

    
    def delGame(self, sessionID):
        self.GameMap.pop(sessionID, False)

    def delOldestSession(self):
        sessionID = min(self.GameMap, key=lambda k:self.GameMap[k][1])
        self.GameMap.pop(sessionID, False)

    

