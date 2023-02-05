from hashlib import sha256
import json
import time


class Block:
    def __init__(self, transactions, index, prevhash, validator):
        self.transactions = transactions
        self.index = index
        self.timestamp = time.time_ns()
        self.prevhash = prevhash
        self.validator = validator
        self.signature = ''
        self.basOriginalCopy = ''
        self.hash = sha256(self.blockAsString()).hexdigest()
        self.type = "BLOCK"
        
    def genesisBlock(self):
        gBlock = Block(0, [], 'initialHash', 'genesis')
        gBlock.timestamp = 0 
        return gBlock
    
    def signBlock(self, signature):
        self.signature = signature
        
    def blockAsString(self):
        bas = ''
        for tx in self.transactions:
            bas += tx
        bas += self.index + self.timestamp + self.prevhash + self.validator + self.signature
        return bas
            
    def copyBAS(self):
        bas = ''
        for tx in self.transactions:
            bas += tx
        bas += self.index + self.timestamp + self.prevhash + self.validator + self.signature
        self.basOriginalCopy = bas
        
    def toJson(self):
         return json.dumps(self, indent = 4, default=lambda o: o.__dict__)