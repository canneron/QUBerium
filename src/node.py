from uuid import uuid4
from blockchain import Blockchain
from wallet import Wallet
import threading

class Node:
    def __init__(self, ip, port):
        self.id = str(uuid4()).replace("-", "")
        self.ip = ip
        self.port = port
        self.bchain = Blockchain()
        self.wallet = Wallet()
        bThread = threading.Thread(target=self.broadcast, args=self, daemon=True)
        lThread = threading.Thread(target=self.listener, args=self, daemon=True)
        sThread = threading.Thread(target=self.sender, args=self, daemon=True)
        
        lThread.start
        bThread.start
        sThread.start
    
    def broadcast(self):
        x = 1

    def listener(self):
        x = 2
        
    def sender(self):
        x = 3