from hashlib import sha256
import time


class Block:
    def __init__(self, index, data, prevhash, validator):
        self.index = index
        self.timestamp = time.time_ns()
        self.data = data
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
        return f"{self.index}{self.timestamp}{self.data}{self.prevhash}{self.validator}{self.signature}"
        
    def copyBAS(self):
        self.basOriginalCopy = f"{self.index}{self.timestamp}{self.data}{self.prevhash}{self.validator}{self.signature}"