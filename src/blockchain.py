from hashlib import sha256
import json
from block import Block


class Blockchain:
    def __init__(self):
        self.chain = []
        self.addInboundBlock(Block.genesisBlock())
        self.walletBalances = {}
        global node
        node = None

    def nodeInjection(self, nodeInj):
        self.node = nodeInj
        
    def testAdd(self, block):
        for tx in block.transactions:
            valid = self.handleTransaction(tx)
            if not valid:
                block.transactions.remove(tx)
        self.chain.append(block)
        
    def addInboundBlock(self, newBlock):
        if len(self.chain) == 0:
            self.chain.append(newBlock)
        else:
            if self.validateNewBlock(self.chain[-1], newBlock):
                for tx in newBlock.transactions:
                    valid = self.handleTransaction(tx)
                    if not valid:
                        newBlock.transactions.remove(tx)
                self.chain.append(newBlock)
            else:
                print("Invalid block hash!")
    
    def addLocalBlock(self, txs, wallet):
        newBlock = wallet.createBlock(txs, len(self.chain), self.chain[-1].hash, wallet.pubKey)
        if self.validateNewBlock(self.chain[-1], newBlock):
            for tx in newBlock.transactions:
                valid = self.handleTransaction(tx)
                if not valid:
                    newBlock.transactions.remove(tx)
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
        print("PREVHASH", newBlock.prevhash)
        print("OLDHASH", oldBlock.hash)
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
        key = nPubKey.e + nPubKey.n
        if key in self.walletBalances.keys():
            self.walletBalances[key] += amount
        else:
            self.walletBalances[key] = amount
            
    def getNodeBalance(self, nPubKey):
        key = nPubKey.e + nPubKey.n
        if key in self.walletBalances.keys():
            return self.walletBalances[key]
        
    def handleTransaction(self, tx):
        senderKey = tx.senderPK.e + tx.senderPK.n
        receiveKey = tx.receiverPK.e + tx.receiverPK.n
        if tx.type == "NEWSTAKE":
            if not senderKey in self.walletBalances.keys() and receiveKey in self.walletBalances.keys():
                if self.getNodeBalance(tx.senderPK) >= tx.amount: 
                    self.walletBalances[senderKey] -= tx.amount
                    self.node.consensus.addNode(tx.senderPK, tx.amount)
                    return True
                else:
                    print("Insufficient funds to stake")
                    return False
            else:
                print("Invalid wallet")
                return False
        if tx.type == "ADDSTAKE":
            if senderKey in self.walletBalances.keys() and receiveKey in self.walletBalances.keys():
                if self.getNodeBalance(tx.senderPK) >= tx.amount: 
                    self.walletBalances[senderKey] -= tx.amount
                    self.node.consensus.addStake(tx.senderPK, tx.amount)
                    return True
                else:
                    print("Insufficient funds to stake")
                    return False
            else:
                print("Invalid wallet")
                return False
        if tx.type == "SUBSTAKE":
            if senderKey in self.walletBalances.keys() and receiveKey in self.walletBalances.keys():
                if self.getNodeBalance(tx.senderPK) >= tx.amount: 
                    self.walletBalances[senderKey] -= tx.amount
                    self.node.consensus.subStake(tx.senderPK, tx.amount)
                    return True
                else:
                    print("Insufficient funds to stake")
                    return False
            else:
                print("Invalid wallet")
                return False
        elif tx.type == "SENDTOKENS":
            if senderKey in self.walletBalances.keys() and receiveKey in self.walletBalances.keys():
                if self.getNodeBalance(tx.senderPK) >= tx.amount: 
                    self.walletBalances[senderKey] -= tx.amount
                    self.walletBalances[receiveKey] += tx.amount
                    return True
                else:
                    print("Insufficient funds to send")
                    return False
            else:
                print("Sender or Receiver not found")
                return False
        elif tx.type == "NEWRECORD":
            print("New record added")
            return True
            
    def isExistingTx(self, txId):
        for block in self.chain:
            for transaction in block.transactions:
                if txId == transaction.id:
                    return True
        return False
    
    def toJson(self):
        jsonRep = {}
        blocks = []
        for b in self.chain:
            blocks.append(b.toJson())
        jsonRep['blocks'] = blocks
        jsonRep['walletbalances'] = self.walletBalances
        jsonRep = json.dumps(jsonRep)
        return jsonRep
