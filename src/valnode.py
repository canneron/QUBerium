import json
import rsa
from block import Block
from blockchain import Blockchain
from kms import KMS
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
        #Start peer to peer functions on node, initialise with parent class Node
        print("STARTING")
        super(ValNode, self).__init__(ip, port, id=nId)
        self.start()
        # Node variables
        self.nId = nId
        self.ip = ip
        self.port = port
        self.permissionLvl = pLvl
        
        # Dictionaries and lists for node information
        # Holds information on known admin nodes against their IDs
        self.knownAdmins = {}
        # Holds informatuon on known students nodes agaisnt their IDs
        self.knownStudents = {}
        # Holds ID of validators who have attempted to fabricate invalid blocks
        self.invalidCreatorIDs = []
        # Holds the balance of each node
        self.nodeBalances = {}
        # Holds the ID of each node against the key associated with it
        self.nodeKeys = {}
        # The index on the chain of each student's record
        self.recordIndex = {}
        
        # Node tools - the blockchain copy of this node, its wallet, the transaction pool for this node, the API interface and the POS
        self.kms = KMS()
        self.bchain = Blockchain()
        self.txPool = TxPool()
        if self.permissionLvl == "admin":
            self.wallet = Wallet(self.kms)
        else:
            self.wallet = Wallet()
        
        # Initialise a balance and the consensus protocol
        self.wallet.balance += 100
        self.consensus = PoS(self.wallet.pubKey, 1)
        self.wallet.balance -= 1
        # Start P2P search
        self.nodeDiscovery()      
        
    # Listens for input on console to interact with blockchain
    def keyboardListener(self):
        #listen for input here
        while True:
            value = input("Enter a command:\n")
            # Prints the blockchain as a JSON
            if value == "blockchain":
                print(self.bchain.toJson())
            # Prints the transaction pool as a JSON
            elif value == "txpool":
                print(self.txPool.txs)
            # Prints the current balance of this node and of all other nodes connected
            elif value == "balances":
                print("Your Balance: ", str(self.wallet.balance))
                print("----------------")
                for id in self.nodeBalances:
                    print(str(id) + " : " + str(self.nodeBalances[id]))
            # Creates a transaction for sending coins to another node
            elif value == "transaction":
                print("Your Balance: ", str(self.wallet.balance))
                amount = input("Enter Amount: ")
                receiver = input("Enter Receiver ID: ")
                # Check receiver ID is valid
                for key in self.nodeKeys:
                    if receiver == self.nodeKeys[key]:
                        # Create transaction and send it to other nodes
                        t = self.wallet.createTransaction(key, amount, "SENDTOKENS")
                        msgJson = t.toJson()
                        self.send_to_nodes(msgJson)
                        break
                print ("Receiver ID not found")
            # Create a new record to add to the chain
            elif value == "newrecord":
                # Users must have the privilege level of admin - students cannot add records to the chain
                if self.permissionLvl == "admin":
                    fname = input("Enter Student Foreame: ")
                    sname = input("Enter Student Surname: ")
                    id = input("Enter Student ID: ")
                    quit = False
                    modulegrades = {}
                    while (quit == False):
                        module = input("Enter Module Code: ")
                        grade = input("Enter Grade: ")
                        modulegrades[module] = grade
                        askquit = input("Enter Another Module? Y/N")
                        if (askquit == False):
                            quit = True
                    # Hold student data in an object
                    sd = StudentData(fname, sname, id, modulegrades)
                    record = self.wallet.createTransaction(self.wallet.pubKey, 0, "NEWRECORD", sd)
                    self.incomingTransaction(record)
                    msgJson = record.toJson()
                    # Send created transaction to other nodes on network
                    self.send_to_nodes(msgJson)
                else:
                    print("Insufficient privilege")
            # Allows admins to search for a students records
            elif value == "search":
                if self.permissionLvl == "admin":
                    fname = input("Enter Student Foreame: ")
                    sname = input("Enter Student Surname: ")
                    id = input("Enter Student ID: ")
                    searchResult = self.recordSearch(self.bchain.chain, id)
                    searchResult['data'] = self.kms.decrypt(searchResult['data'])
                    if searchResult == None:
                        print("Student Record Not Found")
                    else:
                        print("Forename: ", searchResult['sForename'])
                        print("Surname: ", searchResult['sSurname'])
                        print("ID: ", searchResult['sId'])
                        print("Modules: ", searchResult['sModules'])
                        print("Grades: ", searchResult['sGrades'])
                else:
                    print ("Insufficient privilege")
            # Allows a student to view their own records
            elif value == "myrecords":
                if self.permissionLvl == "student":
                    # As the data is encrypted, students must send a request to all admins for a decrypted copy of their data
                    for adminnode in self.all_nodes:
                        if adminnode.id in self.knownAdmins.keys():
                            msg = {}
                            msg["type"] = "RECORDRQ"
                            msg['sId'] = self.nId
                            self.send_to_node(adminnode, msg)
                else:
                    print("Please use search function to find student records")
            # View connected nodes
            elif value == "connections":
                print('Current Connections:')
                for peer in self.knownAdmins:
                    print(str(self.knownAdmins[peer].ip) + ":" + str(self.knownAdmins[peer].port))
                for peer in self.knownStudents:
                    print(str(self.knownStudents[peer].ip) + ":" + str(self.knownStudents[peer].port))
            # Broadcast again in case the original signal is missed
            elif value == "resendbroadcast":
                newport = input("Enter Student Foreame: ")
                self.resendBroadcast(newport)
                                         
    # Start the thread that contains the blockchain console UI
    def startFunctions(self):
        threading.Thread(target=self.keyboardListener).start()
            
    #Holds all necessary information on the node that is sent to any nodes that connect to it, including all its details and held nodes
    def nodeInformationPacket(self, connected_node):
        msgJson = {}
        msgJson["type"] = "NEWNODE"
        msgJson["ip"] = self.ip
        msgJson["port"] = self.port
        msgJson["nId"] = self.nId
        msgJson["pmLvl"] = self.permissionLvl
        msgJson["bal"] = self.wallet.balance
        exNodes = []
        for a in self.knownAdmins:
            exNodes.append(self.knownAdmins[a].toJson())
        msgJson['adminNodes'] = exNodes
        exNodes.clear()
        for s in self.knownStudents:
            exNodes.append(self.knownStudents[s].toJson())
        msgJson['studentNodes'] = exNodes
        msgJson["pubKeyE"] = self.wallet.pubKey.e
        msgJson["pubKeyN"] = self.wallet.pubKey.n
        msgJson['stake'] = self.consensus.getStake((self.wallet.pubKey.n + self.wallet.pubKey.e))
        jsonMsg = json.dumps(msgJson)
        newMsg = jsonMsg.encode('utf-8')
        self.send_to_node(connected_node, newMsg)
    # Override p2p methods
    # Message back from receiving node (sent from original node to new one)
    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + str(connected_node))
        self.nodeInformationPacket(connected_node)
        
    # Inbound connection when receiving a request to connect/sent a message (sent to original node from new one)
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + str(connected_node))
        self.nodeInformationPacket(connected_node)
        
    # Search nodes to determine if the inbound node is already known
    def searchNodes(self, list, msg):
        for xNode in list:
            if list[xNode].ip == msg['ip'] and list[xNode].port == msg['port'] and list[xNode].nId == msg['nId']:
                return False
        return True
    
    # Check to see if the list of nodes from the inbound node contains any that this node is not aware of and connect to them if so
    def searchStoredNodes(self, list, msg):
        newPeer = True
        for student in msg['studentNodes']:
            if self.ip == student['ip'] and self.port == student['port'] and self.nId == student['nId']:
                newPeer = False
            if len(self.knownStudents) > 0:
                for xNode in list:
                    if list[xNode].ip == student['ip'] and list[xNode].port == student['port'] and list[xNode].nId == student['nId']:
                        newPeer = False
            if newPeer:
                self.connect_with_node(student['ip'], student['port'])
                
    # Create a new NodeInfo object
    def addNewNode(self, list, msg):
        list[msg['nId']] = NodeInfo(msg['ip'], msg['port'], msg['nId'], msg['pmLvl'])
        list[msg['nId']] = msg['bal']
    
    # If node is new, take its information and store it
    def newNode(self, msg):
        newNode = True
        # Check the message is not from this node
        if self.ip == msg['ip'] and self.port == msg['port'] and self.nId == msg['nId']:
            newNode = False
        # Check stored nodes
        if msg['pmLvl'] == "admin":
            newNode = self.searchNodes(self.knownAdmins.keys(), msg)
        else:
            newNode = self.searchNodes(self.knownStudents.keys(), msg)
        if newNode:
            # If new node, create a new NodeInfo object storing its details and add its details to the relevant dictionaries
            if msg['pmLvl'] == "student":                   
                self.addNewNode(self.knownStudents, msg)
            else:
                self.addNewNode(self.knownAdmins, msg)
            # Recreate the public key
            pubKey = rsa.PublicKey(msg['pubKeyN'], msg['pubKeyE'])
            self.nodeKeys[pubKey] = msg['nId']
            # Add node to staking if it has any coins staked
            if msg['stake'] > 0:
                    self.consensus.addNode(msg['nId'], msg['stake'])
        # Search the node information sent from the connecting node to check for any new nodes
        self.searchStoredNodes(self.knownAdmins, msg)
        self.searchStoredNodes(self.knownStudents, msg)
            
    # If the message contains a coin transaction then handle it here
    def handleTxMessage(self, msg):
        # Recreate transaction from message contents
        # If the transaction is a new record is will contain the encrypted data containing the record
        tx = Transaction(rsa.PublicKey(msg['sendPKN'],msg['sendPKE']), rsa.PublicKey(msg['receiverPKN'], msg['receiverPKE']), int(msg['amount']), msg['type'], msg['data'])
        tx.setTX(msg['tId'], msg['tTimestamp'])
        tx.copyTAS()
        # Check that the transaction is valid and can be executed
        if self.checkTxValid(tx):
            # If valid, handle the transaction by adding it to the transaction pool
            self.incomingTransaction(tx, msg['tSig'])
        else:
            print("Invalid Transaction")
            
    def handleBlockMessage(self, msg):
        blockTxs = []
        # Recreate transactions
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
            validatorID = self.nodeKeys[block.validator]
            self.nodeBalances[validatorID] += 1
            self.bchain.addInboundBlock(block)
            for blockTx in block.transactions:
                self.handleTransaction(blockTx)
                if blockTx.type == "NEWRECORD":
                    self.recordIndex[blockTx.data.sId] = block.index
            self.txPool.updatePool(block.transactions)
            blockMsg = block.toJson()
            msg = blockMsg.encode('utf-8')
            self.send_to_nodes(msg)
        else:
            print("Invalid block detected! - Alerting Chain")
            msg = {}
            msg["type"] = "INVALIDBLOCK"
            msg["id"] = self.nodeKeys[block.validator]
            self.send_to_nodes(msg)  
            
    # Handles incoming messages
    def node_message(self, connected_node, msg): # types - INFO, TRANSACTION, NEWBLOCK, CHAINREQ, CHAINREP
        if msg['type'] == "NEWNODE":
            self.newNode(msg)
        elif msg['type'] == "SENDTOKENS" or msg['type'] == "ADDSTAKE" or msg['type'] == "SUBSTAKE" or msg['type'] == "NEWSTAKE" or msg['type'] == "NEWRECORD":
            self.handleTxMessage(msg)
        elif msg['type'] == "BLOCK":
            self.handleBlockMessage(msg)
        elif msg['type'] == "CHAINREQ":
            msg = {}
            msg['type'] = "CHAINREP"
            msg['blockchain'] = self.bchain.toJson()
            self.send_to_node(connected_node, msg)
        elif msg['type'] == "CHAINREP":
            newchain = []
            for cblock in msg['blockchain']:
                jsonTx = json.loads(cblock)
                blockTxs = []
                for transaction in cblock['transactions']:
                    tx = Transaction(rsa.PublicKey(jsonTx['sendPKN'], jsonTx['sendPKE']), rsa.PublicKey(jsonTx['receiverPKN'], jsonTx['receiverPKE']), int(jsonTx['amount']), jsonTx['type'], jsonTx['data'])
                    tx.setTX(jsonTx['tId'], jsonTx['tTimestamp'])
                    tx.signTransaction(jsonTx['tSig'])
                    tx.copyTAS()
                    blockTxs.append(tx)
                block = Block(blockTxs, cblock['index'], cblock['prevhash'], rsa.PublicKey(cblock['validatorN'], cblock['validatorE']))
                block.timestamp = cblock['timestamp']
                block.hash = cblock['hash']
                block.copyBAS()
                block.signature = cblock['signature']
                newchain.append(block)
            self.updateToValidChain(newchain)
        elif msg['type'] == "INVALIDBLOCK":
            print(msg['id'] + " has produced an invalidated block") 
            print("Their stake has been removed and ID recorded")
            self.consensus.nodes[msg['id']] = 0
            self.invalidCreatorIDs.append[msg['id']]
        elif msg['type'] == "RECORDRQ":
            result = self.recordSearch(self.bchain.chain, msg['sId'])
            decryptedData = self.kms.decrypt(result['data'])
            result['data'] = decryptedData.decode('utf-8')
            msg = {}
            msg['type'] = "RECORDREP"
            if result == None:
                msg['record'] = "NONEFOUND"
            else:
                msg['record'] = result
            self.send_to_node(connected_node, msg)
        elif msg['type'] == "RECORDREP":
            print("Forename: ", msg['sForename'])
            print("Surname: ", msg['sSurname'])
            print("ID: ", msg['sId'])
            print("Modules: ", msg['sModules'])
            print("Grades: ", msg['sGrades'])
            
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
        if transaction.tId not in self.txPool.txs and not self.bchain.isExistingTx(transaction.tId):
            if validSig:
                self.txPool.addTxToPool(transaction)
                txMsg = transaction.toJson()
                msg = txMsg.encode('utf-8')
                self.send_to_nodes(msg) # add message for transaction
                if self.txPool.isNotEmpty():
                    validator = self.consensus.generateValidator(self.bchain.lastBlock().hash)                         
                    if validator == None:
                        print("Error: No validator")
                    else:
                        if (self.wallet.pubKey.e + self.wallet.pubKey.n) == validator:
                            newBlock = self.bchain.addLocalBlock(self.txPool.txs, self.wallet)
                            if newBlock == None:
                                print("Error!")
                            else:
                                for blockTx in newBlock.transactions:
                                    self.handleTransaction(blockTx)
                                self.txPool.updatePool(newBlock.transactions)
                                
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
                    print("Invalid chain - Stake removed")
                    self.consensus.nodes[self.nId] = 0
                    return False
        return True
    
    def validateNewChain(self, chain):
        if (chain.chainLength() > 1):
            for b in range(0, len(chain) -1):
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
        if self.consensus.generateValidator(self.bchain.lastBlock().hash) == (val):
            return True
        else:
            return False      

    def recordSearch(self, chain, id):
        validTransaction = None
        validData = None
        for block in chain:
            for transaction in block.transactions:
                if transaction.data != None:
                    record = transaction.data.toDict()
                    if record['sId'] == id:
                        if validTransaction == None:
                            validTransaction = transaction
                        else:
                            if transaction.tTimestamp > validTransaction.tTimestamp:
                                validTransaction = transaction
        validData = validTransaction.data.toDict()
        return validData
    
    def resendBroadcast(self, nodePort):
        self.connect_with_node('localhost', nodePort)