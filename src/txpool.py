# This calss stores the valid transactions received by the node in the transaction pool before they added to a block
class TxPool:
    def __init__(self):
        self.txs = []
    
    def addTxToPool(self, newTx):
        if self.notInPool(newTx):
            self.txs.append(newTx)
    
    # Check a transaction is not already in the pool
    def notInPool(self, newTx):
        for tx in self.txs:
            if newTx.tId == tx.tId:
                return False
        return True
    
    # Takes a list of transactions being added to a block and removes them from the pool
    # The pool has to be reproduced from a new list without the transactions in the block rather than have them removed from the existing list
    # Removing them from the existing list will cause them to also be removed from the block
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
        
    # Check the pool is not empty to decide when to add transactions to a block
    # This can be changed so that blocks will hold more transactions
    def isNotEmpty(self):
        if len(self.txs) > 0:
            return True
        else:
            return False