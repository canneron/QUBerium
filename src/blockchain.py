from block import Block


class Blockchain:
    def __init__(self):
        self.chain = []
        self.addBlock(Block.genesisBlock())

    def addBlock(self, newBlock):
        self.chain.append(newBlock)