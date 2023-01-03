from hashlib import sha256
from block import Block


class Blockchain:
    def __init__(self):
        self.chain = []
        self.addBlock(Block.genesisBlock())

    def addBlock(self, newBlock):
        self.chain.append(newBlock)
        
    def chainLength(self):
        return len(self.chain)
    
    def validateLastHash(self, block):
        prevBlock = self.chain[block.index - 1]
        prevHash = sha256(prevBlock.blockAsString().encode()).hexdigest()
        if prevHash == block.prevhash:
            return True
        else:
            return False