import json
import time
from uuid import uuid4

import rsa
#from api import API
from block import Block
from blockchain import Blockchain
from pos import PoS
from studentdata import StudentData
from transaction import Transaction
from txpool import TxPool
from wallet import Wallet
import threading
from p2pnetwork.node import Node
from nodeinfo import NodeInfo

class ValNode(Node):
    def __init__(self, ip, port, pLvl, nId):
        print("STARTING")
        super(ValNode, self).__init__(ip, port, id=nId)
        self.start()
        # Node variables
        self.nId = nId
        self.ip = ip
        self.port = port
        self.permissionLvl = pLvl
        self.knownNodes = []
        self.nodeBalances = {}
        self.nodeKeys = {}
        self.nodePermissions = {}
        
        # Node tools - the blockchain copy of this node, its wallet, the transaction pool for this node, the API interface and the POS
        self.bchain = Blockchain()
        self.wallet = Wallet()
        self.txPool = TxPool()
        self.wallet.balance += 100
        self.consensus = PoS(self.wallet.pubKey, 1)
        self.wallet.balance -= 1
        self.nodeDiscovery()      
            
    def keyboardListener(self):
        #listen for input here
        while True:
            value = input("Enter a command:\n")
            if value == "blockchain":
                print(self.bchain.toJson())
            elif value == "txpool":
                print(self.txPool.txs)
            elif value == "balances":
                print(self.nodeBalances)
                print("Your Balance: ", self.wallet.balance)
            elif value == "transaction":
                tx = input("Enter details:\n")
                details = tx.split(" ")
                x = list(self.nodeKeys.keys())[0]
                t = self.wallet.createTransaction(self.nodeKeys[x], details[0], "SENDTOKENS")
                msgJson = t.toJson()
                self.send_to_nodes(msgJson)
            elif value == "newrecord":
                tx = input("Enter record:\n")
                details = tx.split(" ")
                sd = StudentData(details[0], details[1], details[2], details[3], details[4])
                x = list(self.nodeKeys.keys())[0]
                t = self.wallet.createTransaction(self.nodeKeys[x], 0, "NEWRECORD", sd)
                self.incomingTransaction(t)
                msgJson = t.toJson()
                self.send_to_nodes(msgJson)
            elif value == "search":
                fname = input("Enter Student Foreame: ")
                sname = input("Enter Student Surname: ")
                id = input("Enter Student ID: ")
                searchResult = self.recordSearch(self.bchain.chain, fname, sname, id)
                if searchResult == None:
                    print("Student Record Not Found")
                else:
                    print("Forename: ", searchResult['sForename'])
                    print("Surname: ", searchResult['sSurname'])
                    print("ID: ", searchResult['sId'])
                    print("Modules: ", searchResult['sModules'])
                    print("Grades: ", searchResult['sGrades'])
            elif value == "connections":
                print('Current Connections:')
                for peer in self.knownNodes:
                    print(str(peer.ip) + ":" + str(peer.port))
            elif value == "resendbroadcast":
                newport = input("Enter Student Foreame: ")
                self.resendBroadcast(newport)                

    def startFunctions(self):
        threading.Thread(target=self.keyboardListener).start()
            
    # Override p2p methods
    # Message back from receiving node (sent from original node to new one)
    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + str(connected_node))
        msgJson = {}
        msgJson["type"] = "NEWNODE"
        msgJson["ip"] = self.ip
        msgJson["port"] = self.port
        msgJson["nId"] = self.nId
        msgJson["pmLvl"] = self.permissionLvl
        msgJson["pubKeyE"] = self.wallet.pubKey.e
        msgJson["pubKeyN"] = self.wallet.pubKey.n
        msgJson["bal"] = self.wallet.balance
        msgJson["stake"] = self.consensus.getStake(self.wallet.pubKey)
        exNodes = []
        for n in self.knownNodes:
            exNodes.append(n.toJson())
        msgJson['nodes'] = exNodes
        jsonMsg = json.dumps(msgJson)
        newMsg = jsonMsg.encode('utf-8')
        self.send_to_node(connected_node, newMsg)
        
    # Inbound connection when receiving a request to connect/sent a message (sent to original node from new one)
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + str(connected_node))
        msgJson = {}
        msgJson["type"] = "NEWNODE"
        msgJson["ip"] = self.ip
        msgJson["port"] = self.port
        msgJson["nId"] = self.nId
        msgJson["pmLvl"] = self.permissionLvl
        msgJson["pubKeyE"] = self.wallet.pubKey.e
        msgJson["pubKeyN"] = self.wallet.pubKey.n
        msgJson["bal"] = self.wallet.balance
        msgJson["stake"] = self.consensus.getStake(self.wallet.pubKey)
        exNodes = []
        for n in self.knownNodes:
            exNodes.append(n.toJson())
        msgJson['nodes'] = exNodes
        jsonMsg = json.dumps(msgJson)
        newMsg = jsonMsg.encode('utf-8')
        self.send_to_node(connected_node, newMsg)
        
    # Message receiver
    def node_message(self, connected_node, msg): # types - INFO, TRANSACTION, NEWBLOCK, CHAINREQ, CHAINREP
        if msg['type'] == "NEWNODE":
            newNode = True
            if self.ip == msg['ip'] and self.port == msg['port'] and self.nId == msg['nId']:
                newNode = False
            for xNode in self.knownNodes:
                if xNode.ip == msg['ip'] and xNode.port == msg['port'] and xNode.nId == msg['nId']:
                    newNode = False
            if newNode:
                self.knownNodes.append(NodeInfo(msg['ip'], msg['port'], msg['nId'], msg['pmLvl']))
                pubKey = rsa.PublicKey(msg['pubKeyN'], msg['pubKeyE'])
                self.nodeBalances[pubKey.n + pubKey.e] = msg['bal']
                self.nodeKeys[msg['nId']] = pubKey
                self.nodePermissions[msg['nId']] = msg['pmLvl']
                if msg['stake'] > 0:
                    self.consensus.addNode(pubKey, msg['stake'])
                
            newNodePeer = True
            for p in msg['nodes']:
                if self.ip == p['ip'] and self.port == p['port'] and self.nId == p['nId']:
                    newNodePeer = False
                if len(self.knownNodes) > 0:
                    for xNode in self.knownNodes:
                        if xNode.ip == p['ip'] and xNode.port == p['port'] and xNode.nId == p['nId']:
                            newNode = False
                if newNodePeer:
                    self.connect_with_node(p['ip'], p['port'])
        elif msg['type'] == "SENDTOKENS" or msg['type'] == "ADDSTAKE" or msg['type'] == "SUBSTAKE" or msg['type'] == "NEWSTAKE":
            tx = Transaction(rsa.PublicKey(msg['sendPKN'],msg['sendPKE']), rsa.PublicKey(msg['receiverPKN'], msg['receiverPKE']), int(msg['amount']), msg['type'])
            tx.setTX(msg['tId'], msg['tTimestamp'])
            tx.copyTAS()
            if self.checkTxValid(tx):
                self.incomingTransaction(tx, msg['tSig'])
            else:
                print("Invalid Transaction")
        elif msg['type'] == "NEWRECORD":
            tx = Transaction(rsa.PublicKey(msg['sendPKN'],msg['sendPKE']), rsa.PublicKey(msg['receiverPKN'], msg['receiverPKE']), int(msg['amount']), msg['type'], msg['data'])
            tx.setTX(msg['tId'], msg['tTimestamp'])
            tx.copyTAS()
            if self.checkTxValid(tx):
                self.incomingTransaction(tx, msg['tSig'])
            else:
                print("Invalid Transaction")
        elif msg['type'] == "BLOCK":
            blockTxs = []
            for transaction in msg['transactions']:
                jsonTx = json.loads(transaction)
                tx = Transaction(rsa.PublicKey(jsonTx['sendPKN'], jsonTx['sendPKE']), rsa.PublicKey(jsonTx['receiverPKN'], jsonTx['receiverPKE']), int(jsonTx['amount']), jsonTx['type'], jsonTx['data'])
                tx.setTX(jsonTx['tId'], jsonTx['tTimestamp'])
                tx.signTransaction(jsonTx['tSig'])
                tx.copyTAS()
                blockTxs.append(tx)
            block = Block(blockTxs, msg['index'], msg['prevhash'], rsa.PublicKey(msg['validatorN'], msg['validatorE']))
            block.timestamp = msg['timestamp']
            block.hash = msg['hash']
            block.copyBAS()
            block.signature = msg['signature']
            valid = None
            if self.bchain.chainLength() == block.index:
                if self.bchain.validateNewBlock(self.bchain.lastBlock(), block) and self.wallet.validateSig(block.basOriginalCopy, block.signature, block.validator) and self.validatorValid(block.validator):
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
                for blockTx in block.transactions:
                    self.handleTransaction(blockTx)
                self.txPool.updatePool(block.transactions)
                blockMsg = block.toJson()
                msg = blockMsg.encode('utf-8')
                self.send_to_nodes(msg)
        elif msg['type'] == "CHAINREQ":
            msg = {}
            msg['type'] = "CHAINREP"
            msg['blockchain'] = self.bchain.toJson()
            self.send_to_node(connected_node, msg)
        elif msg['type'] == "CHAINREP":
            newchain = []
            print(msg)

    def nodeDiscovery(self):
        if self.port != 5001:
            self.connect_with_node('localhost', 5001)
        
    def broadcaster(self):
        while True:
            x = 1

    def getBalance(self):
        return self.wallet.balance
            
    def incomingTransaction(self, transaction, tSig):
        tData = transaction.tasOriginalCopy
        tSigner = transaction.senderPK
        validSig = self.wallet.validateSig(tData, tSig, tSigner)
        if validSig:
            transaction.signTransaction(tSig)
        print("TETSE 1")
        if transaction.tId not in self.txPool.txs and not self.bchain.isExistingTx(transaction.tId):
            if validSig:
                print("TETSE 2")
                self.txPool.addTxToPool(transaction)
                txMsg = transaction.toJson()
                msg = txMsg.encode('utf-8')
                self.send_to_nodes(msg) # add message for transaction
                if self.txPool.isNotEmpty():
                    print("TETSE 3")
                    validator = self.consensus.generateValidator(self.bchain.lastBlock().hash)
                    
                    if validator == None:
                        print("Error: No validator")
                    else:
                        if (self.wallet.pubKey.e + self.wallet.pubKey.n) == validator:
                            print("TETSE 4")
                            newBlock = self.bchain.addLocalBlock(self.txPool.txs, self.wallet)
                            if newBlock == None:
                                print("Error!")
                            else:
                                for blockTx in newBlock.transactions:
                                    self.handleTransaction(blockTx)
                                self.txPool.updatePool(newBlock.transactions)
                                print("LENGTH: ", len(self.txPool.txs))
                                
                                blockMsg = newBlock.toJson()
                                msg = blockMsg.encode('utf-8')
                                self.send_to_nodes(msg)
                        else:
                            print("Not validator")
                            
    def checkTxValid(self, tx):
        senderKey = tx.senderPK.e + tx.senderPK.n
        receiveKey = tx.receiverPK.e + tx.receiverPK.n
        myKey = self.wallet.pubKey.n + self.wallet.pubKey.e
        if (senderKey in self.nodeBalances.keys() or senderKey == myKey) and (receiveKey in self.nodeBalances.keys() or receiveKey == myKey):
            if tx.type == "NEWSTAKE":
                if senderKey == myKey:
                    if self.wallet.balance >= tx.amount : 
                        return True
                    else:
                        print("Insufficient funds to stake")
                        return False
                else:
                    if self.nodeBalances[senderKey] >= tx.amount : 
                        return True
                    else:
                        print("Insufficient funds to stake")
                        return False
            elif tx.type == "ADDSTAKE":
                if senderKey == myKey:
                    if self.wallet.balance >= tx.amount : 
                        return True
                    else:
                        print("Insufficient funds to add to stake")
                        return False
                else:
                    if self.nodeBalances[senderKey] >= tx.amount : 
                        return True
                    else:
                        print("Insufficient funds to add to stake")
                        return False
            elif tx.type == "SUBSTAKE":
                if self.consensus[senderKey] >= tx.amount: 
                    return True
                else:
                    print("Insufficient funds to withdraw")
                    return False
            elif tx.type == "SENDTOKENS":
                if senderKey == myKey:
                    if self.wallet.balance >= tx.amount : 
                        return True
                    else:
                        print("Insufficient funds to send")
                        return False
                else:
                    if self.nodeBalances[senderKey] >= tx.amount : 
                        return True
                    else:
                        print("Insufficient funds to send")
                        return False
            elif tx.type == "NEWRECORD":
                return True
        else:
            print("Sender or Receiver not found")
            return False
            
                            
    def handleTransaction(self, tx):
        senderKey = tx.senderPK.e + tx.senderPK.n
        receiveKey = tx.receiverPK.e + tx.receiverPK.n
        myKey = self.wallet.pubKey.n + self.wallet.pubKey.e
        if tx.type == "NEWSTAKE":
            self.nodeBalances[senderKey] -= tx.amount
            self.consensus.addNode(tx.senderPK, tx.amount)
        if tx.type == "ADDSTAKE":
            if senderKey == myKey:
                self.wallet.balance -= tx.amount
            else:
                self.nodeBalances[senderKey] -= tx.amount
            self.consensus.addStake(tx.senderPK, tx.amount)
        if tx.type == "SUBSTAKE":
            if senderKey == myKey:
                self.wallet.balance -= tx.amount
            else:
                self.nodeBalances[senderKey] += tx.amount
            self.consensus.subStake(tx.senderPK, tx.amount)
        elif tx.type == "SENDTOKENS":
            if senderKey == myKey:
                self.wallet.balance -= tx.amount
                self.nodeBalances[receiveKey] += tx.amount
            elif receiveKey == myKey:
                self.nodeBalances[senderKey] -= tx.amount
                self.wallet.balance += tx.amount
            else:
                self.nodeBalances[senderKey] -= tx.amount
                self.nodeBalances[receiveKey] += tx.amount
        elif tx.type == "NEWRECORD":
            print("New record added")
        
    def validateChain(self):
        if (self.bchain.chainLength() > 1):
            for b in range(0, len(self.bchain.chain) -1):
                if self.bchain.validateNewBlock(self.bchain.chain[b], self.bchain.chain[b+1]):
                    continue
                else:
                    print("Coin deduction for penalising")
                    self.wallet.balance -= 1
                    return False
        return True
    
    def validateNewChain(self):
        if (self.bchain.chainLength() > 1):
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
                self.txPool.updatePool(block.transactions)
            
    def validatorValid(self, val):
        if self.consensus.generateValidator(self.bchain.lastBlock().hash) == (val.n + val.e):
            return True
        else:
            return False      

    def recordSearch(self, chain, fname, sname, id):
        for block in chain:
            for transaction in block.transactions:
                if transaction.data != None:
                    record = transaction.data.toDict()
                    if record['sForename'] == fname and record['sSurname'] == sname and record['sId'] == id:
                        return transaction.data
        return None
    
    def resendBroadcast(self, nodePort):
        self.connect_with_node('localhost', nodePort)