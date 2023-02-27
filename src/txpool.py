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
        keep = True
        for t in txs:
            for pooltx in self.txs:
               if t.tId == pooltx.tId and t.tTimestamp == pooltx.tTimestamp and t.tSig == pooltx.tSig:
                   keep = False
            if keep:
                updatedPool.append(t)
        self.txs = updatedPool
        
    def isNotEmpty(self):
        if len(self.txs) > 0:
            return True
        else:
            return False