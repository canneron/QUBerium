from hashlib import sha256
import json
from block import Block


class Blockchain:
    def __init__(self):
        self.chain = []
        self.addInboundBlock(Block.genesisBlock())
        self.wallets = []
        self.walletBalances = {}
        global node
        node = None

    def nodeInjection(self, nodeInj):
        self.node = nodeInj
        
    def addInboundBlock(self, newBlock):
        if self.chainLength == 0:
            self.chain.append(newBlock)
        elif self.validateNewBlock(self.chain[-1], newBlock):
            self.handleTransactions(newBlock.transactions)
            self.chain.append(newBlock)
        else:
            print("Invalid block hash!")
    
    def addLocalBlock(self, txs, wallet):
        newBlock = self.wallet.createBlock(txs, self.chain.len(), self.chain[-1], wallet.pubKey)
        if self.validateNewBlock(self.chain[-1], newBlock):
            self.handleTransactions(newBlock.transactions)
            self.chain.append(newBlock)
            return newBlock
        else:
            print("Invalid block hash!")
            return None
        
    def chainLength(self):
        return len(self.chain)
    
    def lastBlock(self):
        return self.chain[-1]
    
    def genesisBlock(self):
        return self.chain[0]
    
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
            if tx.type == "NEWSTAKE":
                if tx.senderPK in self.wallets and tx.receiverPK in self.wallets:
                    if self.getNodeBalance[tx.senderPK] >= tx.amount: 
                        self.walletBalances[tx.senderPK] -= tx.amount
                        self.node.consensus.addNode(tx.senderPK, tx.amount)
                    else:
                        print("Insufficient funds to stake")
                else:
                    print("Invalid wallet")
            if tx.type == "ADDSTAKE":
                if tx.senderPK in self.wallets and tx.receiverPK in self.wallets:
                    if self.getNodeBalance[tx.senderPK] >= tx.amount: 
                        self.walletBalances[tx.senderPK] -= tx.amount
                        self.node.consensus.addStake(tx.senderPK, tx.amount)
                    else:
                        print("Insufficient funds to stake")
                else:
                    print("Invalid wallet")
            if tx.type == "SUBSTAKE":
                if tx.senderPK in self.wallets and tx.receiverPK in self.wallets:
                    if self.getNodeBalance[tx.senderPK] >= tx.amount: 
                        self.walletBalances[tx.senderPK] -= tx.amount
                        self.node.consensus.subStake(tx.senderPK, tx.amount)
                    else:
                        print("Insufficient funds to stake")
                else:
                    print("Invalid wallet")
            elif tx.type == "SEND":
                if tx.senderPK in self.wallets and tx.receiverPK in self.wallets:
                    if self.getNodeBalance[tx.senderPK] >= tx.amount: 
                        self.walletBalances[tx.senderPK] -= tx.amount
                        self.walletBalances[tx.receiverPK] += tx.amount
                    else:
                        print("Insufficient funds to send")
                else:
                    print("Sender or Receiver not found")
            elif tx.type == "RECORD":
                print("New record added")
                break
            
    def isExistingTx(self, txId):
        for block in self.chain:
            for transaction in block:
                if txId == transaction.id:
                    return True
        return False
    
    def toJson(self):
         return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
