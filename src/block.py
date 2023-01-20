from hashlib import sha256
import time


class Block:
    def __init__(self, transaction, index, prevhash, validator):
        self.transaction = transaction
        self.index = index
        self.timestamp = time.time_ns()
        self.prevhash = prevhash
        self.validator = validator
        self.signature = ''
        self.basOriginalCopy = ''
        self.hash = sha256(self.blockAsString().encode()).hexdigest()

    def genesisBlock(self):
        gBlock = Block(0, [], 'initialHash', 'genesis')
        gBlock.timestamp = 0 
        return gBlock
    
    def signBlock(self, signature):
        self.signature = signature
        
    def blockAsString(self):
        return f"{self.transaction}{self.index}{self.timestamp}{self.prevhash}{self.validator}{self.signature}"
        
    def copyBAS(self):
        self.basOriginalCopy = f"{self.transaction}{self.index}{self.timestamp}{self.prevhash}{self.validator}{self.signature}"