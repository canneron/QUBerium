from hashlib import sha256
import random
import time

class PoS:
    def __init__(self, pk, stake):
        self.nodes = {}
        self.nodes[pk] = stake
        
    def addNode(self, validator, stake):
        if validator not in list(self.nodes.keys()):
            self.nodes[validator] = stake
        else:
            print ("Node already in staking pool")
        
    def addStake(self, validator, stake):
        if validator in list(self.nodes.keys()):
            self.nodes[validator] += stake
        else:
            print ("Node not in staking pool")
            
    def subStake(self, validator, stake):
        if validator in list(self.nodes.keys()):
            self.nodes[validator] -= stake
        else:
            print ("Node not in staking pool")
            
    def getStake(self, val):
        return self.nodes[val]
    
    def generateValidator(self, lastHash):
        pool = {}
        for staker in self.nodes.keys():
            for chance in range(0,...,self.nodes[staker]):
                guessStr = "" + staker + chance
                guess = int(sha256(guessStr).hexdigest())
                pool[guess] = staker
        targetNum = int(sha256(lastHash))
        nearestGuess = None
        for guess in pool.keys():
            if nearestGuess == None:
                nearestGuess == guess
            else:
                if abs(guess - targetNum) < abs(nearestGuess - targetNum):
                    nearestGuess = guess
        print("Winner is: " + pool[nearestGuess])
        return pool[nearestGuess]