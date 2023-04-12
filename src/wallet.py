import rsa
from block import Block
from transaction import Transaction

# The wallet class holds the node's keyset and their token balance
class Wallet:
    def __init__(self, adminKey = None):
        # Use the python RSA library to generate a public and private key pair
        self.pubKey, self.privKey = rsa.newkeys(1024)
        # Stores a nodes token balance
        self.balance = 0
        # Stores the AWS KMS client if an admin for encrypting data when creating a transaction, defaults to None if a student
        self.adminKey = adminKey
    
    # Produce a digital signature with the node's private key and data of the transaction/block   
    def sigSign(self, data):
        return rsa.sign(data, self.privKey, 'SHA-256').hex()
    
    # Creates a new transaction and signs it with the node's private key so that other users can verify it with the public key
    # If an admin, the data (student records) will be encrpyted using AWS KMS to obfuscate data on the chain   
    def createTransaction(self, receiver, amount, type, bData = None):
        nTransaction = Transaction(self.pubKey, receiver, amount, type, bData)
        sig = self.sigSign(nTransaction.transactionAsString().encode('utf-8'))
        nTransaction.copyTAS()
        nTransaction.signTransaction(sig)
        if nTransaction.data != None and self.adminKey != None:
            nTransaction.data = nTransaction.data.toDict()
            nTransaction.data = self.adminKey.encrypt(nTransaction.data)
            nTransaction.data = nTransaction.data.decode('latin-1')
            nTransaction.encrypted = True
        return nTransaction
    
    # Creates a new block and signs it using the node's private key for other users to verify with the public key
    def createBlock(self, transactions, index, previousHash, validator):
        nBlock = Block(transactions, index, previousHash, validator)
        nBlock.copyBAS()
        sig = self.sigSign(nBlock.blockAsString().encode('utf-8'))
        nBlock.signBlock(sig)
        return nBlock
    
    # Validate that a signature on a transaction/block is real using the RSA library@
    # Verifying with the signature, the public key of the signer and the data used to sign it (store in the transaction/block) will return the encryption algorithm
    def validateSig(self, data, sig, sigPubKey):
        data = data.encode('utf-8')
        try:
            if rsa.verify(data, bytes.fromhex(sig), sigPubKey) == "SHA-256":
                return True
        except:
            print("Invalid Siganture!")
            return False
    
    # Updates a node's balance   
    def updateBalance(self, amount):
        if self.balance + amount > 0:
            self.balance += amount
        else:
            print ("Balance cannot go below 0")

