from hashlib import sha256
from uuid import uuid4
from block import Block
from blockchain import Blockchain
from wallet import Wallet
import threading

class Node:
    def __init__(self, ip, port, pLvl):
        self.id = str(uuid4()).replace("-", "")
        self.ip = ip
        self.port = port
        self.permissionLvl = pLvl
        
        self.bchain = Blockchain()
        self.wallet = Wallet()
        
        self.knownNodesPubKey = []
        self.knownNodesNickname = []
        self.nodeBalances = {}
        
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
        
    def getBalance(self):
        return self.wallet.balance
        
    def addNode(self, nodePubKey, nodeID):
        if nodePubKey not in self.knownNodes:
            self.knownNodesPubKey.append(nodePubKey)
            self.knownNodesNickname.append(nodeID)
            self.nodeBalances[nodePubKey] = 0
            self.bchain.wallets.append(nodePubKey)
            self.bchain.walletBalances[nodePubKey] = 0
            print("New node added: ", nodeID)
            
    
        