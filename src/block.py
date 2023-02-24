from hashlib import sha256
import json
import time

import rsa


class Block:
    def __init__(self, transactions, index, prevhash, validator):
        self.transactions = transactions
        self.index = index
        self.timestamp = time.time_ns()
        self.prevhash = prevhash
        self.validator = validator
        self.signature = ''
        self.basOriginalCopy = ''
        self.type = "BLOCK"
        self.hash = sha256(self.blockAsString().encode("utf-8")).hexdigest()
        
    def genesisBlock():
        gBlock = Block([], 0, 'initialHash', rsa.PublicKey(0,0))
        gBlock.timestamp = 0 
        return gBlock
    
    def signBlock(self, signature):
        self.signature = signature
        
    def blockAsString(self):
        bas = ''
        for tx in self.transactions:
            bas += tx.transactionAsString()
        bas += str(self.index) + str(self.timestamp) + str(self.prevhash) + str(self.validator.e) + str(self.validator.n) + self.signature + self.type
        self.copyBAS()
        bas.encode("utf-8")
        return bas
            
    def copyBAS(self):
        bas = ''
        for tx in self.transactions:
            bas += tx.transactionAsString()
        bas += str(self.index) + str(self.timestamp) + str(self.prevhash) + str(self.validator.e) + str(self.validator.n) + self.signature + self.type
        self.basOriginalCopy = bas
        
    def toJson(self):
        jsonRep = {}
        txs = []
        for n in self.transactions:
            txs.append(n.toJson())
        jsonRep['transactions'] = txs
        jsonRep['index'] = self.index
        jsonRep['timestamp'] = self.timestamp
        jsonRep['prevhash'] = self.prevhash
        jsonRep['validatorE'] = self.validator.e
        jsonRep['validatorN'] = self.validator.n
        jsonRep['signature'] = self.signature
        jsonRep['type'] = self.type
        jsonRep['hash'] = self.hash
        jsonRep = json.dumps(jsonRep)
        return jsonRep