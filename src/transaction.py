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
        jsonRep = {}
        jsonRep['sendPKE'] = self.senderPK.e
        jsonRep['sendPKN'] = self.senderPK.n
        jsonRep['receiverPKE'] = self.receiverPK.e
        jsonRep['receiverPKN'] = self.receiverPK.n
        jsonRep['amount'] = self.amount
        jsonRep['data'] = self.data.toDict()
        jsonRep['type'] = self.type
        jsonRep['tId'] = self.tId
        jsonRep['tTimestamp'] = self.tTimestamp
        jsonRep['tSig'] = self.tSig
        jsonRep = json.dumps(jsonRep)
        return jsonRep
     
    def setTX(self, id, ts):
        self.tId = id
        self.tTimestamp = ts
        
    def signTransaction(self, sig):
        self.tSig = sig
        
    def transactionAsString(self):
        tas = f"{self.senderPK.e}{self.senderPK.n}{self.receiverPK.e}{self.receiverPK.n}{self.amount}{self.data}{self.type}{self.tId}{self.tTimestamp}{self.tSig}"
        self.copyTAS()
        tas.encode('utf-8')
        return tas
        
    def copyTAS(self):
        self.tasOriginalCopy = f"{self.senderPK.e}{self.senderPK.n}{self.receiverPK.e}{self.receiverPK.n}{self.amount}{self.data}{self.type}{self.tId}{self.tTimestamp}{self.tSig}"