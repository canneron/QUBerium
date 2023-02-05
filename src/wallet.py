import json
import rsa
from block import Block
from valnode import Node
from transaction import Transaction

class Wallet:
    def __init__(self):
        self.pubKey, self.privKey = rsa.newkeys(1024)
        self.balance = 0
        
    def createTransaction(self, receiver, amount, type, bData = None):
        if bData != None:
            bData = self.hashData(bData)
        nTransaction = Transaction(self.pubKey, receiver, amount, type, bData)
        sig = self.sigSign(nTransaction.transactionAsString().encode('utf-8'))
        nTransaction.signTransaction(sig)
        return nTransaction
    
    def createBlock(self, transactions, length, previousHash, validator):
        nBlock = Block(transactions, length, previousHash, validator)
        sig = rsa.sign(nBlock.blockAsString().encode('utf-8'), self.privKey, 'SHA-256')
        nBlock.copyBAS()
        nBlock.signBlock(sig)
        return nBlock
        
    def hashData(self, data):
        data.encode('utf-8')
        encdata = rsa.encrypt(data, self.pubKey)
        return encdata
    
    def validateSig(data, sig, sigPubKey):
        data = data.encode('utf-8')
        return rsa.verify(data, sig, sigPubKey)
        
    def updateBalance(self, amount):
        self.balance += amount
        
    def toJson(self):
         return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
