import random

class PoS:
    def __init__(self):
        self.nodes = {}
        
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
    
    def generateValidator(self):
        pool = 0
        for v in self.nodes.keys():
            pool += self.nodes[v]
        winner = random.randrange(0, pool)
        winnerpool = 0
        for v in self.nodes.keys():
            winnerpool += self.nodes[v]
            if winnerpool > winner:
                print("Validator chosen: ", v)
                return v
        print("No validator chosen")
        return None
        
# Notes
# Doesn't have to be true p2p - you can use a client list if needed but try to use p2pnetwork package
# Focus on making consensus the best it can be as that's the important bit