import json


class TxPool:
    def __init__(self):
        self.txs = []
        
    def addTxToPool(self, newTx):
        if self.notInPool(newTx):
            self.txs.append(newTx)
        
    def notInPool(self, newTx):
        for tx in self.txs:
            if newTx.tId == tx.tId:
                return False
        return True
    
    def updatePool(self, txs):
        updatedPool = []
        for t in txs:
            if not t in self.txs:
                updatedPool.append(t)
        self.txs = updatedPool
        
    def isNotEmpty(self):
        if len(self.txs) > 0:
            return True
        else:
            return False