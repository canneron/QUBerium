from hashlib import sha256
from block import Block


class Blockchain:
    def __init__(self):
        self.chain = []
        self.addBlock(Block.genesisBlock())
        self.wallets = []
        self.walletBalances = {}

    def addBlock(self, newBlock):
        if self.validateNewBlock(self.chain[-1], newBlock):
            self.handleTransactions(newBlock.transactions)
            self.chain.append(newBlock)
        else:
            print("Invalid block hash!")
        
    def chainLength(self):
        return len(self.chain)
    
    def lastBlock(self):
        return self.chain[-1]
    
    def validateNewBlock(self, oldBlock, newBlock):
        if newBlock.prevhash != oldBlock.hash:
            print("Invalid Hash")
            return False
        elif newBlock.index - 1 != oldBlock.index:
            print("Invalid index")
            return False
        elif newBlock.timestamp < oldBlock.timestamp:
            print("Invalid timestamp")
            return False
        else:
            return True
    
    def updateNodeBalance(self, nPubKey, amount):
        if nPubKey in self.wallets:
            self.walletBalances[nPubKey] += amount
            
    def getNodeBalance(self, nPubKey):
        if nPubKey in self.wallets:
            return self.walletBalances[nPubKey]
        
    def handleTransactions(self, transactions):
        for tx in transactions:
            if tx.senderPK in self.wallets and tx.receiverPK in self.wallets:
                if self.getNodeBalance[tx.senderPK] >= tx.amount: 
                    self.walletBalances[tx.senderPK] -= tx.amount
                    self.walletBalances[tx.receiverPK] += tx.amount
                else:
                    print("Insufficient funds to send")
            else:
                print("Sender or Receiver not found")
