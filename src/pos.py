class PoS:
    def __init__(self):
        self.nodes = {}
        
    def addNode(self, newPK, tokens):
        if newPK in list(self.nodes.keys()):
            self.nodes[newPK] = tokens
        else:
            print ("Node not in staking pool")
        
    def addStake(self, newPK, tokens):
        if newPK in list(self.nodes.keys()):
            self.nodes[newPK] += tokens
        else:
            print ("Node not in staking pool")
            
    def subStake(self, newPK, tokens):
        if newPK in list(self.nodes.keys()):
            self.nodes[newPK] -= tokens
        else:
            print ("Node not in staking pool")
            
    def getStake(self, pk):
        return self.nodes[pk]
    
    def generateValidator(self):
        
        
        
# Notes
# Doesn't have to be true p2p - you can use a client list if needed but try to use p2pnetwork package
# Focus on making consensus the best it can be as that's the important bit