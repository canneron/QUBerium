from hashlib import sha256
import json
import time

import rsa


class Block:
    def __init__(self, transactions, index, prevhash, validator):
        self.transactions = transactions
        self.index = index
        if self.index == 0:
            self.timestamp = 0
        else:
            self.timestamp = time.time_ns()
        self.prevhash = prevhash
        self.validator = validator
        self.signature = ''
        self.basOriginalCopy = ''
        self.type = "BLOCK"
        self.hash = sha256(self.blockAsString().encode("utf-8")).hexdigest()
        
    def genesisBlock():
        gBlock = Block([], 0, "genesis", "genesis")
        return gBlock
    
    def signBlock(self, signature):
        self.signature = signature
        
    def blockAsString(self):
        bas = ''
        if self.index == 0:
            val = self.validator
        else:
            val = str(self.validator.e) + str(self.validator.n)
        for tx in self.transactions:
            bas += tx.transactionAsString()
        bas += str(self.index) + str(self.timestamp) + str(self.prevhash) + val + self.signature + self.type
        bas.encode("utf-8")
        return bas
            
    def copyBAS(self):
        bas = ''
        if self.index == 0:
            val = self.validator
        else:
            val = str(self.validator.e) + str(self.validator.n)
        for tx in self.transactions:
            bas += tx.transactionAsString()
        bas += str(self.index) + str(self.timestamp) + str(self.prevhash) + val + self.signature + self.type
        self.basOriginalCopy = bas
        
    def toJson(self):
        jsonRep = {}
        jsonRep['index'] = self.index
        txs = []
        for n in self.transactions:
            txs.append(n.toJson())
        jsonRep['transactions'] = txs
        jsonRep['timestamp'] = self.timestamp
        jsonRep['prevhash'] = self.prevhash
        if (self.index == 0):
            jsonRep['validatorE'] = self.validator
            jsonRep['validatorN'] = self.validator
        else:
            jsonRep['validatorE'] = self.validator.e
            jsonRep['validatorN'] = self.validator.n
        jsonRep['signature'] = self.signature
        jsonRep['type'] = self.type
        jsonRep['hash'] = self.hash
        jsonRep = json.dumps(jsonRep, indent=4)
        return jsonRep