from hashlib import sha256
import json
from block import Block

# Class holding the blockchain itself
class Blockchain:
    def __init__(self):
        self.chain = []
        # Upon creating add the preset genesis block
        # This will be the same on all nodes
        self.addInboundBlock(Block.genesisBlock())
        
    # Add a block sent by other nodes
    def addInboundBlock(self, newBlock):
        # If this is the genesis block then it can be automatically appended
        if len(self.chain) == 0:
            self.chain.append(newBlock)
        else:
            # Validate the block's previous hash variable is equal to the hash of the last block on the chain
            if self.validateNewBlock(self.chain[-1], newBlock):
                # Add to the chain if it is
                self.chain.append(newBlock)
            else:
                print("Invalid block hash!")
    
    # Add a block produced locally as the validator
    def addLocalBlock(self, txs, wallet):
        # Creates a block signed by this node as the validator using the wallet's signing functions
        newBlock = wallet.createBlock(txs, len(self.chain), self.chain[-1].hash, wallet.pubKey)
        if self.validateNewBlock(self.chain[-1], newBlock):
            self.chain.append(newBlock)
            return newBlock
        else:
            print("Invalid block hash!")
            return None
    # Getters
    def chainLength(self):
        return len(self.chain)
    
    def lastBlock(self):
        return self.chain[-1]
    
    def genesisBlock(self):
        return self.chain[0]
    
    def getBlock(self, index):
        return self.chain[index]
    
    # Function for validating the integrity of a block by comparing it against its predecessor 
    def validateNewBlock(self, oldBlock, newBlock):
        # Check that the hash of the previous block is equal to the previous hash stored in the new one
        print("genesis ", self.genesisBlock().hash)
        print(oldBlock.hash)
        print(newBlock.prevhash)
        if newBlock.prevhash != oldBlock.hash:
            print("Invalid Hash")
            return False
        # Check the index of the new block is consecutive with the old one
        elif newBlock.index - 1 != oldBlock.index:
            print("Invalid index")
            return False
        # Check that the new block has been created after the old one by comparing timestamps to prevent forgery
        elif newBlock.timestamp < oldBlock.timestamp:
            print("Invalid timestamp")
            return False
        # Disregard for gensis block
        elif oldBlock.hash == "genesis":
            return True
        # Retrun true if all checks are passed
        else:
            return True
        
    # Check each transaction held in each block is not equal to any transactions held in the transaction pool to prevent duplicates and double spends
    def isExistingTx(self, txId):
        for block in self.chain:
            for transaction in block.transactions:
                if txId == transaction.tId:
                    return True
        return False
    
    # Return a JSON representation of the blockchain
    def toJson(self):
        jsonRep = {}
        blocks = []
        for b in self.chain:
            blocks.append(b.toJson())
        jsonRep['blocks'] = blocks
        jsonRep = json.dumps(jsonRep, indent=4)
        return jsonRep
