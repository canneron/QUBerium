import rsa
from block import Block
from node import Node

class Wallet:
    def __init__(self):
        self.pubKey, self.privKey = rsa.newkeys(1024)
        self.balance = 0
        
    def createBlock(self, node, bData):
        encData = self.hashData(bData)
        nBlock = Block(node.bchain.chainLength(), encData, node.bchain.chain[-1].hash, self.pubKey)
        sig = self.sigSign(nBlock.blockAsString().encode('utf-8'))
        nBlock.copyBAS()
        nBlock.signBlock(sig)
        node.bchain.addBlock(nBlock)
        
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
        
