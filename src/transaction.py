import json
import time
from uuid import uuid4

# Class defining a transaction
class Transaction:
    def __init__(self, sender, receiver, amount, type, data = None):
        # The public keys of the sender and receiver
        self.senderPK  = sender
        self.receiverPK = receiver
        # The amount, if any, to be transferred
        self.amount = amount
        # The data variable holds the student records, is set to None by default for token transactions
        self.data = data
        # Type of transaction eg NEWRECORD, SENDTOKENS, ADDSTAKE
        self.type = type
        # Unique ID for each transaction
        self.tId = str(uuid4()).replace("-", "")
        # Timestamp to further identify the transaction
        self.tTimestamp = time.time_ns()
        # Signature of the creator of the transaction
        self.tSig = ''
        # Copy of the transaction as a string before being signed
        # This is for verification purposes, as after a transaction is signed the transaction as a string will change
        # When other nodes then go to verify the signature it will then fail as the data is different
        # Therefore, a copy of the transaction's data before it is signed has to be saved for verifying the signature
        self.tasOriginalCopy = ''
        # Flags if the data has been encrypted on this transaciton
        self.encrypted = False
    
    # JSON representation of the transaction
    def toJson(self):
        jsonRep = {}
        jsonRep['sendPKE'] = self.senderPK.e
        jsonRep['sendPKN'] = self.senderPK.n
        jsonRep['receiverPKE'] = self.receiverPK.e
        jsonRep['receiverPKN'] = self.receiverPK.n
        jsonRep['amount'] = self.amount
        # If encrypted the data will not be a StudentData object so must be sent as plaintext
        if self.encrypted == True or self.encrypted == None:
            jsonRep['data'] = self.data
        else:
            jsonRep['data'] = self.data.toDict()
        jsonRep['type'] = self.type
        jsonRep['tId'] = self.tId
        jsonRep['tTimestamp'] = self.tTimestamp
        jsonRep['tSig'] = self.tSig
        jsonRep['tasCopy'] = self.tasOriginalCopy
        jsonRep = json.dumps(jsonRep, indent=4)
        return jsonRep
    
    # Setters for recreation on other nodes
    def setTX(self, id, ts):
        self.tId = id
        self.tTimestamp = ts
        
    def signTransaction(self, sig):
        self.tSig = sig
        
    # Produces a string representation of the transaction for producing a digital signature
    def transactionAsString(self):
        tas = f"{self.senderPK.e}{self.senderPK.n}{self.receiverPK.e}{self.receiverPK.n}{self.amount}{self.data}{self.type}{self.tId}{self.tTimestamp}{self.tSig}"
        self.copyTAS()
        tas.encode('utf-8')
        return tas
        
    # Copies string representation before the transaction is signed
    def copyTAS(self):
        self.tasOriginalCopy = f"{self.senderPK.e}{self.senderPK.n}{self.receiverPK.e}{self.receiverPK.n}{self.amount}{self.data}{self.type}{self.tId}{self.tTimestamp}{self.tSig}"