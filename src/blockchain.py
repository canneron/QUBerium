from hashlib import sha256
from block import Block


class Blockchain:
    def __init__(self):
        self.chain = []
        self.addBlock(Block.genesisBlock())
        self.wallets = []
        self.walletBalances = {}

    def addBlock(self, newBlock):
        if self.validateLastHash(newBlock):
            self.chain.append(newBlock)
        else:
            print("Invalid block hash!")
        
    def chainLength(self):
        return len(self.chain)
    
    def lastBlock(self):
        return self.chain[-1]
    
    def validateLastHash(self, block):
        prevBlock = self.chain[block.index - 1]
        prevHash = sha256(prevBlock.blockAsString().encode()).hexdigest()
        if prevHash == block.prevhash:
            return True
        else:
            return False
    
    def updateNodeBalance(self, nPubKey, amount):
        if nPubKey in self.wallets:
            self.walletBalances[nPubKey] += amount
            
    def getNodeBalance(self, nPubKey):
        if nPubKey in self.wallets:
            return self.walletBalances[nPubKey]
        
    def handleTransaction(self, tx):
        if tx.senderPK in self.wallets and tx.receiverPK in self.wallets:
            if self.getNodeBalance[tx.senderPK] >= tx.amount: 
                self.walletBalances[tx.senderPK] -= tx.amount
                self.walletBalances[tx.receiverPK] += tx.amount
            else:
                print("Insufficient funds to send")
        else:
            print("Sender or Receiver not found")
