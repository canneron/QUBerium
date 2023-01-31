from hashlib import sha256
from uuid import uuid4
from api import API
from block import Block
from blockchain import Blockchain
from txpool import TxPool
from wallet import Wallet
import threading
from p2pnetwork.node import Node

class ValNode(Node):
    def __init__(self, ip, port, apiPort, pLvl):
        super(ValNode, self).__init__(ip, port, None)
        self.start()
        self.id = str(uuid4()).replace("-", "")
        self.ip = ip
        self.port = port
        self.permissionLvl = pLvl
        
        self.bchain = Blockchain()
        self.wallet = Wallet()
        self.txPool = TxPool()
        self.api = API()
        
        self.knownNodes = []
        self.nodeBalances = {}
        
        bThread = threading.Thread(target=self.broadcaster, args=self, daemon=True)
        lThread = threading.Thread(target=self.listener, args=self, daemon=True)
        lThread.start
        bThread.start
        
        self.api.nodeInjection(self)
        self.api.startAPI(apiPort)

        
    # Override p2p methods
    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node)
        msg = "INFO~"
        ip = self.ip
        port = self.port
        id = self.id
        pmLvl = self.permissionLvl
        msg += ip + "~" + port + "~" + id + "~" + pmLvl + "~"
        for pk in self.nodeBalances.keys():
            msg += pk + ";"
        msg += "~"
        for bal in self.nodeBalances.keys():
            msg+= self.nodeBalances[bal] + ";"
        msg += "~"
        for nIp in self.knownNodes:
            msg += nIp[0] + ";"
        msg += "~"
        for nPort in self.knownNodes:
            msg += nIp[1] + ";"
        self.send_to_node(connected_node, msg)
        
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + connected_node)
        msg = "INFO~"
        ip = self.ip
        port = self.port
        id = self.id
        pmLvl = self.permissionLvl
        pubKey = self.wallet.pubKey
        msg += ip + "~" + port + "~" + id + "~" + pmLvl + "~"
        for pk in self.nodeBalances.keys():
            msg += pk + ";"
        msg += "~"
        for bal in self.nodeBalances.keys():
            msg+= self.nodeBalances[bal] + ";"
        msg += "~"
        for nNodes in self.knownNodes:
            msg += nNodes[0] + ";"
            msg += nNodes[1] + ";"
            msg += nNodes[2] + ";"
            msg += nNodes[3] + ":"
        msg += "~"
        msg += self.wallet.pubKey + ";" + self.wallet.balance
        self.send_to_node(connected_node, msg)
        
    def node_message(self, node, data):
        msgData = data.split("~")
        if (msgData[0] == "INFO"):
            nIp = data[1]
            nPort = data[2]
            nId = data[3]
            nPmLvl = data[4]
            nBalancesPK = data[5]
            nBalances = data[6]
            nNodes = data[7]
            nWallet = data[8]
            newNode = True
            for n in self.knownNodes:
                if (n[0] == nIp and n[1] == nPort) or (nIp == self.ip and nPort == self.port):
                    newNode = False
            if newNode:
                self.knownNodes.append((nIp, nPort, nId, nPmLvl))
                balancePK = nBalancesPK.split(";")
                balances = nBalances.split(";")
                for i in range(0, balancePK.len()):
                    if balancePK[i] not in self.nodeBalances.keys():
                        self.nodeBalances[balancePK[i]] = balances[i]
                nodeList = nNodes.split(":")
                for node in nodeList:
                    nData = node.split(";")
                    nodeTuple = (nData[0], nData[1], nData[2], nData[3])
                    if nodeTuple not in self.knownNodes:
                        self.knownNodes.append(nodeTuple)
                wallet = nWallet.split(";")
                if wallet[0] not in self.nodeBalances:
                    self.nodeBalances[wallet[0]] = wallet[1]
        elif msgData[0] == "TRANSACTION":
            transaction = msgData[1]
            self.addToChain(transaction)
        
    def nodeDiscovery(self):
        if self.port != 5001:
            self.connect_with_node('localhost', 5001)
        
    def broadcaster(self):
        while True:
            x = 1
            
    def listener(self):
        while True:
            x = 1

    def getBalance(self):
        return self.wallet.balance
        
    def addNode(self, nodePubKey, nodeID):
        if nodePubKey not in self.knownNodes:
            self.nodeBalances[nodePubKey] = 0
            self.bchain.wallets.append(nodePubKey)
            self.bchain.walletBalances[nodePubKey] = 0
            print("New node added: ", nodeID)
            
    def addToChain(self, transaction):
        tData = transaction.transactionAsString()
        tSig = transaction.signature
        tSigner = transaction.senderPk
        validSig = self.wallet.validateSig(tData, tSig, tSigner)
        if transaction.tId not in self.txPool.txs:
            if validSig:
                self.txPool.addTxToPool(transaction)
                self.send_to_nodes(txMessage)
        
        
            
    def validateChain(self):
        for b in range(0, self.bchain.chain.len() -1):
            if self.bchain.validateNewBlock(self.chain[b], self.chain[b+1]):
                continue
            else:
                print("Coin deduction for penalising")
                self.wallet.balance -= 100
                return False
        return True
    
    def updateToValidChain(self, newChain):
        if self.validateChain(newChain) and newChain.len() > self.bchain.chain.len():
            chain = newChain
            
    
        