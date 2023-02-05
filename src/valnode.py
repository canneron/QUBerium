import json
from uuid import uuid4
from api import API
from block import Block
from blockchain import Blockchain
from pos import PoS
from transaction import Transaction
from txpool import TxPool
from wallet import Wallet
import threading
from p2pnetwork.node import Node
from nodeinfo import NodeInfo

class ValNode(Node):
    def __init__(self, ip, port, apiPort, pLvl):
        # Open P2P Communication
        super(ValNode, self).__init__(ip, port, None)
        self.start()
        # Node variables
        self.id = str(uuid4()).replace("-", "")
        self.ip = ip
        self.port = port
        self.permissionLvl = pLvl
        
        # Node tools - the blockchain copy of this node, its wallet, the transaction pool for this node, the API interface and the POS
        self.bchain = Blockchain()
        self.bchain.nodeInjection(self)
        self.wallet = Wallet()
        self.txPool = TxPool()
        self.api = API()
        self.api.nodeInjection(self)
        self.api.startAPI(apiPort)
        self.wallet.balance += 100
        self.consensus = PoS(self.wallet.pubKey, 1)
        self.wallet.balance -= 1
        
        # Track other nodes on the network
        self.nodeDiscovery()
        self.knownNodes = []
        self.nodeBalances = {}
        
        bThread = threading.Thread(target=self.broadcaster, args=self, daemon=True)
        lThread = threading.Thread(target=self.listener, args=self, daemon=True)
        lThread.start
        bThread.start

    # Override p2p methods
    # Message back from receiving node (sent from original node to new one)
    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node)
        msgJson = {}
        msgJson["type"] = "NEWNODE"
        msgJson["ip"] = self.ip
        msgJson["port"] = self.port
        msgJson["id"] = self.id
        msgJson["pmLvl"] = self.permissionLvl
        msgJson["pubKey"] = self.wallet.pubKey
        msgJson["bal"] = self.wallet.balance
        msgJson["nodes"] = self.knownNodes
        msgJson["nodeBalances"] = self.nodeBalances
        jsonMsg = json.dumps(msgJson)
        newMsg = jsonMsg.encode('utf-8')
        self.send_to_node(connected_node, newMsg)
        
    # Inbound connection when receiving a request to connect/sent a message (sent to original node from new one)
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + connected_node)
        msgJson = {}
        msgJson["type"] = "NEWNODE"
        msgJson["ip"] = self.ip
        msgJson["port"] = self.port
        msgJson["id"] = self.id
        msgJson["pmLvl"] = self.permissionLvl
        msgJson["pubKey"] = self.wallet.pubKey
        msgJson["bal"] = self.wallet.balance
        exNodes = []
        for n in self.knownNodes:
            exNodes.append(n.toJson())
        msgJson['nodes'] = exNodes
        jsonMsg = json.dumps(msgJson)
        newMsg = jsonMsg.encode('utf-8')
        self.send_to_node(connected_node, newMsg)
        
    # Message receiver
    def node_message(self, connected_node, data): # types - INFO, TRANSACTION, NEWBLOCK, CHAINREQ, CHAINREP
        msg = json.loads(data)
        if msg.type == "NEWNODE":
            newNode = True
            if self.ip == msg.ip and self.port == msg.port and self.id == msg.id:
                newNode = False
            if len(self.knownNodes) > 0:
                for xNode in self.knownNodes:
                    if xNode.ip == msg.ip and xNode.port == msg.port and xNode.id == msg.id:
                        newNode = False
            if newNode:
                self.knownNodes.append(NodeInfo(msg.ip, msg.port, msg.id, msg.pmLvl))
                self.nodeBalances[msg.pubKey] = msg.bal
                self.bchain.walletBalances[msg.pubKey] = msg.bal
                if msg.bal > 0:
                    self.consensus.addNode(msg.pubKey, msg.bal)
            newNodePeer = True
            for p in msg.nodes:
                if self.ip == p.ip and self.port == p.port and self.id == p.id:
                    newNodePeer = False
                if len(self.knownNodes) > 0:
                    for xNode in self.knownNodes:
                        if xNode.ip == p.ip and xNode.port == p.port and xNode.id == p.id:
                            newNode = False
                if newNodePeer:
                    self.connect_with_node(p.ip, p.port)
        elif msg.type == "SENDTOKENS" or msg.type == "NEWRECORD":
            tx = Transaction(msg.senderPK, msg.receiverPK, msg.amount, msg.type, msg.data)
            tx.setTX(msg.tId, msg.tTimestamp)
            self.addToChain(tx)
        elif msg.type == "BLOCK":
            block = Block(msg.transactions, msg.index, msg.prevhash, msg.validator)
            block.timestamp = msg.timestamp
            block.hash = msg.hash
            block.copyBAS()
            block.signature = msg.signature
            valid = None
            if self.bchain.chainLength == block.index:
                if self.bchain.validateNewBlock(block, self.bchain.lastBlock) and self.wallet.validateSig(block.basOriginalCopy, block.signature, block.validator) and self.validatorValid(block.validator):
                    valid = True
                else:
                    valid = False
            else:
                valid = False
                if not self.validateChain():
                    msg = {}
                    msg['type'] = "CHAINREQ"
                    self.send_to_nodes(msg)
            if valid:
                self.bchain.addInboundBlock(block)
                self.txPool.removeTxsFromPool(block.transactions)
                blockMsg = block.toJson()
                msg = blockMsg.encode('utf-8')
                self.send_to_nodes(msg)
        elif msg.type == "CHAINREQ":
            msg = {}
            msg['type'] = "CHAINREP"
            msg['blockchain'] = self.bchain.chain
            self.send_to_node(connected_node, msg)
        elif msg.type == "CHAINREP":
            print(msg.blockchain) # to do

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
        tData = transaction.toJson
        tSig = transaction.signature
        tSigner = transaction.senderPk
        validSig = self.wallet.validateSig(tData, tSig, tSigner)
        if validSig:
            transaction.signTransaction(transaction.signature)
        if transaction.tId not in self.txPool.txs and not self.bchain.isExistingTx(transaction.tId):
            if validSig:
                self.txPool.addTxToPool(transaction)
                txMsg = transaction.toJson()
                msg = txMsg.encode('utf-8')
                self.send_to_nodes(msg) # add message for transaction
        if self.txPool.isNotEmpty():
            validator = self.consensus.generateValidator(self.bchain.lastBlock.hash)
            if validator == None:
                print("Error: No validator")
            else:
                if self.wallet.pubKey == validator:
                    newBlock = self.bchain.addLocalBlock(self.txPool.txs, self.wallet)
                    self.txPool.removeTxsFromPool(newBlock.transactions)
                    blockMsg = newBlock.toJson()
                    msg = blockMsg.encode('utf-8')
                    self.send_to_nodes(msg) # add message for block creation
           
    def validateChain(self):
        if (self.bchain.chainLength > 1):
            for b in range(0, len(self.bchain.chain) -1):
                if self.bchain.validateNewBlock(self.chain[b], self.chain[b+1]):
                    continue
                else:
                    print("Coin deduction for penalising")
                    self.wallet.balance -= 1
                    return False
        return True
    
    def validateNewChain(self):
        if (self.bchain.chainLength > 1):
            for b in range(0, len(self.bchain.chain) -1):
                if self.bchain.validateNewBlock(self.chain[b], self.chain[b+1]):
                    continue
                else:
                    return False
        return True
    
    def updateToValidChain(self, newChain):
        if self.validateNewChain(newChain) and newChain.len() > len(self.bchain.chain) and self.bchain.genesisBlock() == newChain[0]:
            self.bchain.chain = newChain  
            for block in newChain:
                self.txPool.removeTxsFromPool(block.transactions)
            
    def validatorValid(self, val):
        if self.consensus.generateValidator(self.bchain.lastBlock.hash) == val:
            return True
        else:
            return False      
            
    #to do
    #--------------------
    # urgent
    #--------------------
    #add json messaging
    #sort out p2p send and receive of messages using skeleton for everything i.e. define record transaction
    #--------------------
    # wait for ihsen
    #--------------------
    #broadcasting discovery?