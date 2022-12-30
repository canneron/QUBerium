from hashlib import sha256
import time


class Block:
    def __init__(self, index, data, prevhash, validator):
        self.index = index
        self.timestamp = time.time()
        self.prevhash = prevhash
        self.data = data
        self.validator = validator
        self.digsignature = ''
        
        bas = f"{self.index}{self.timestamp}{self.prevhash}{self.validator}{self.signature}"
        for t in self.transactions:
            bas += t
        self.hash = sha256(bas.encode()).hexdigest()

    def genesisBlock():
        gBlock = Block(0, [], 'initialHash', 'genesis')
        gBlock.timestamp = 0 
        return gBlock
    
    def signBlock(self, signature):
        self.digsignature = signature