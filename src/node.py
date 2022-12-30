from uuid import uuid4
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class Node:
    def __init__(self, ip, port):
        self.id = str(uuid4()).replace("-", "")
        self.ip = ip
        self.port = port
        self.generateKeys()
        
    def generateKeys(self):
        privKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        
        encrypted_pem_private_key = privKey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(private_key_pass)
        )

        pem_public_key = privKey.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        
        privKeyFile = open("example-rsa.pem", "w")
        privKeyFile.write(encrypted_pem_private_key.decode())
        privKeyFile.close()

        pubKeyFile = open("example-rsa.pub", "w")
        pubKeyFile.write(pem_public_key.decode())
        pubKeyFile.close()
        