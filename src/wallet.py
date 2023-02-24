import json
import rsa
from block import Block
from transaction import Transaction

class Wallet:
    def __init__(self):
        self.pubKey, self.privKey = rsa.newkeys(1024)
        self.balance = 0
        
    def sigSign(self, data):
        return rsa.sign(data, self.privKey, 'SHA-256').hex()
        
    def createTransaction(self, receiver, amount, type, bData = None):
        #if bData != None:
            #bData = self.hashData(bData)
        nTransaction = Transaction(self.pubKey, receiver, amount, type, bData)
        sig = self.sigSign(nTransaction.transactionAsString().encode('utf-8'))
        nTransaction.signTransaction(sig)
        return nTransaction
    
    def createBlock(self, transactions, index, previousHash, validator):
        nBlock = Block(transactions, index, previousHash, validator)
        sig = self.sigSign(nBlock.blockAsString().encode('utf-8'))
        nBlock.signBlock(sig)
        return nBlock
        
    def hashData(self, data):
        data.encode('utf-8')
        encdata = rsa.encrypt(data, self.pubKey)
        return encdata
    
    def validateSig(self, data, sig, sigPubKey):
        data = data.encode('utf-8')
        return rsa.verify(data, bytes.fromhex(sig), sigPubKey)
        
    def updateBalance(self, amount):
        self.balance += amount

