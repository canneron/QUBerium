from hashlib import sha256
import random
import time

class PoS:
    def __init__(self, pk, stake):
        self.nodes = {}
        self.addNode(pk, stake)
        
    def addNode(self, validator, stake):
        key = validator.e + validator.n
        if key not in list(self.nodes.keys()):
            self.nodes[key] = stake
        else:
            print ("Node already in staking pool")
        
    def addStake(self, validator, stake):
        key = validator.e + validator.n
        if key in list(self.nodes.keys()):
            self.nodes[key] += stake
        else:
            print ("Node not in staking pool")
            
    def subStake(self, validator, stake):
        key = validator.e + validator.n
        if key in list(self.nodes.keys()):
            self.nodes[key] -= stake
        else:
            print ("Node not in staking pool")
            
    def getStake(self, val):
        key = val.e + val.n
        return self.nodes[key]
    
    def generateValidator(self, lastHash):
        pool = {}
        for staker in self.nodes.keys():
            for chance in range(self.nodes[staker]):
                guessStr = str(staker) + str(chance)
                guess = int(sha256(guessStr.encode("utf-8")).hexdigest(), 16)
                pool[guess] = staker
        targetStr = (lastHash).encode("utf-8")
        targetNum = int(sha256(targetStr).hexdigest(), 16)
        nearestGuess = None
        for guess in pool.keys():
            if nearestGuess == None:
                nearestGuess = guess
            else:
                if abs(guess - targetNum) < abs(nearestGuess - targetNum):
                    nearestGuess = guess
        print("Winner is:", pool[nearestGuess])
        return pool[nearestGuess]