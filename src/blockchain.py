from hashlib import sha256
import json
from block import Block


class Blockchain:
    def __init__(self):
        self.chain = []
        self.addInboundBlock(Block.genesisBlock())
        
    def addInboundBlock(self, newBlock):
        if len(self.chain) == 0:
            self.chain.append(newBlock)
        else:
            if self.validateNewBlock(self.chain[-1], newBlock):
                self.chain.append(newBlock)
            else:
                print("Invalid block hash!")
    
    def addLocalBlock(self, txs, wallet):
        newBlock = wallet.createBlock(txs, len(self.chain), self.chain[-1].hash, wallet.pubKey)
        if self.validateNewBlock(self.chain[-1], newBlock):
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
        print("OldBlock Hash", oldBlock.hash)
        print("NewBlock PrevHash:", newBlock.prevhash)
        if newBlock.prevhash != oldBlock.hash:
            print("Invalid Hash")
            return False
        elif newBlock.index - 1 != oldBlock.index:
            print("Invalid index")
            return False
        elif newBlock.timestamp < oldBlock.timestamp:
            print("Invalid timestamp")
            return False
        elif oldBlock.hash == "genesis":
            return True
        else:
            return True
            
    def isExistingTx(self, txId):
        for block in self.chain:
            for transaction in block.transactions:
                if txId == transaction.tId:
                    return True
        return False
    
    def toJson(self):
        jsonRep = {}
        blocks = []
        for b in self.chain:
            blocks.append(b.toJson())
        jsonRep['blocks'] = blocks
        jsonRep = json.dumps(jsonRep, indent=4)
        return jsonRep
