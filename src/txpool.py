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
    
    def removeTxsFromPool(self, txs):
        for t in txs:
            if t in self.txs:
                self.txs.remove(t)
        
    def isNotEmpty(self):
        if self.txs.len() > 0:
            return True
        else:
            return False