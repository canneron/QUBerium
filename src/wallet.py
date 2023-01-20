import rsa
from block import Block
from node import Node
from transaction import Transaction

class Wallet:
    def __init__(self):
        self.pubKey, self.privKey = rsa.newkeys(1024)
        self.balance = 0
        
    def createTransaction(self, receiver, amount, type, bData = None):
        if bData != None:
            bData = self.hashData(bData)
        nTransaction = Transaction(self.pubKey, receiver, amount, bData, type)
        sig = self.sigSign(nTransaction.transactionAsString().encode('utf-8'))
        nTransaction.signTransaction(sig)
        return nTransaction
    
    def createBlock(self, node, transaction):
        nBlock = Block(transaction,node.bchain.chainLength(), node.bchain.chain[-1].hash, self.pubKey)
        sig = self.sigSign(nBlock.blockAsString().encode('utf-8'))
        nBlock.copyBAS()
        nBlock.signBlock(sig)
        node.bchain.addBlock(nBlock)
        return Block
        
    def hashData(self, data):
        data.encode('utf-8')
        encdata = rsa.encrypt(data, self.pubKey)
        return encdata
        
    def sigSign(self, data):
        sig = rsa.sign(data, self.privKey, 'SHA-256')
        return sig.hex()
    
    def validateSig(data, sig, sigPubKey):
        data = data.encode('utf-8')
        hashFunc = rsa.verify(data, sig, sigPubKey)
        if hashFunc in ['SHA-256']:
            return True
        else:
            return False
        
    def updateBalance(self, amount):
        self.balance += amount
