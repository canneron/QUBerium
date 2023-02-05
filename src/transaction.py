import json
import time
from uuid import uuid4


class Transaction:
    def __init__(self, sender, receiver, amount, type, data = None):
        self.senderPK  = sender
        self.receiverPK = receiver
        self.amount = amount
        self.data = data
        self.type = type
        self.tId = str(uuid4()).replace("-", "")
        self.tTimestamp = time.time_ns()
        self.tSig = ''
        self.tasOriginalCopy = ''
    
    def toJson(self):
         return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
     
    def setTX(self, id, ts):
        self.tId = id
        self.ts = self.tTimestamp
        
    def signTransaction(self, sig):
        self.tSig = sig
        
    def transactionAsString(self):
        tas = f"{self.senderPK}{self.receiverPK}{self.amount}{self.data}{self.type}{self.tId}{self.tTimestamp}{self.tSig}"
        self.copyTAS()
        return tas
        
    def copyTAS(self):
        self.tasOriginalCopy = f"{self.senderPK}{self.receiverPK}{self.amount}{self.data}{self.type}{self.tId}{self.tTimestamp}{self.tSig}"