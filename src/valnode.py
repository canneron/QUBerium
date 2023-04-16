import json
import time
from tkinter import messagebox
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

# This class acts as the main hub of the blockchain
# It acts as the node and the top layer of the blockchain program
# The peer to peer functions are called and stored in this class alongside the node's information such as IP and Port
# It also holds the users ID, permissions and instances of their wallet, blockchain and transaction pool
class ValNode(Node):
    def __init__(self, ip, port, pLvl, nId):
        #Start peer to peer functions on node, initialise with parent class Node
        # Node variables
        self.nId = nId
        self.ip = ip
        self.port = port
        self.permissionLvl = pLvl
        self.end = False
        self.command = None
        self.cmd = False
        self.record = None
        self.reply = False
        
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
        # The KMS class holds a client for the AWS KMS service that is only accessible to admins for encrypting/decrypting data with a key stored in the amazon key vault
        if self.permissionLvl == "admin":    
            self.kms = KMS()
        else:
            self.kms = None
        self.bchain = Blockchain()
        self.txPool = TxPool()
        if self.permissionLvl == "admin":
            self.wallet = Wallet(self.kms)
            self.wallet.balance += 100
            self.consensus = PoS(self.wallet.pubKey, 50)
            self.wallet.balance -= 50
        else:
            self.wallet = Wallet()
            self.wallet.balance += 20
            self.consensus = PoS(self.wallet.pubKey, 5)
            self.wallet.balance -= 5
            # Variable for storing block that is being validated by admin
            self.storedBlock = None
        
        # Initialise a balance and the consensus protocol
        self.nodeKeys[self.wallet.pubKey] = self.nId
          
        
    # Listens for input on console to interact with blockchain
    def keyboardListener(self):
        #listen for input here
        while self.end == False:
            value = input("Enter a command:\n")
            # Prints the blockchain as a JSON
            if value == "blockchain" or self.command == "blockchain":
                print(self.bchain.toJson())
            # Prints the transaction pool as a JSON
            elif value == "txpool" or self.command == "txpool":
                print(self.txPool.txs)
            elif value == "commands" or self.command == "commands":
                print("blockchain - View Blockchain")
                print("txpool - View Transaction Pool")
                print("balances - View your balance and the balance of other users")
                print("transaction - Send tokens to another user")
                if (self.permissionLvl == "admin"):
                    print("newrecord - Create a new student record")
                    print("search - Search for a student record")
                else:
                    print("myrecords - View your records")
                print("connections - View connections to other nodes")
                print("resendbroadcast - Connect to a specified node")
                print("quit - Shut down node and exit")
            # Prints the current balance of this node and of all other nodes connected
            elif value == "balances" or self.command == "balances":
                print("Your Balance: ", str(self.wallet.balance))
                print("----------------")
                for id in self.nodeBalances:
                    print(str(id) + " : " + str(self.nodeBalances[id]))
            # Creates a transaction for sending coins to another node
            elif value == "transaction" or self.command == "transaction":
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
                        self.incomingTransaction(t, t.tSig)
                        break
                print ("Receiver ID not found")
            # Create a new record to add to the chain
            elif value == "newrecord" or self.command == "newrecord":
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
                        if (askquit == "N"):
                            quit = True
                    # Hold student data in an object
                    sd = StudentData(fname, sname, id, modulegrades)
                    record = self.wallet.createTransaction(self.wallet.pubKey, 0, "NEWRECORD", sd)
                    msgJson = record.toJson()
                    # Send created transaction to other nodes on network
                    self.send_to_nodes(msgJson)
                    self.incomingTransaction(record, record.tSig)
                else:
                    print("Insufficient privilege")
            # Allows admins to search for a students records
            elif value == "search" or self.command == "search":
                if self.permissionLvl == "admin":
                    id = input("Enter Student ID: ")
                    searchResult = self.recordSearch(self.bchain.chain, id)
                    if searchResult == None:
                        print("Student Record Not Found")
                    else:
                        self.printRecords(searchResult)
                else:
                    print ("Insufficient privilege")
            # Allows a student to view their own records
            elif value == "myrecords" or self.command == "myrecords":
                if self.permissionLvl == "student":
                    # As the data is encrypted, students must send a request to all admins for a decrypted copy of their data
                    admins = []
                    for adminKeys in self.knownAdmins.keys():
                        admins.append(str(adminKeys))
                    for adminnode in self.all_nodes:
                        if adminnode.id in admins:
                            msg = {}
                            msg["type"] = "RECORDRQ"
                            msg['sId'] = self.nId
                            self.send_to_node(adminnode, msg)
                            print("Request Sent")
                    if len(admins) == 0:
                        print("Network error - no administrator nodes online")
                else:
                    print("Please use search function to find student records")
            # View connected nodes
            elif value == "connections" or self.command == "connections":
                print('Current Connections:')
                print("**** ADMINS ****")
                for peer in self.knownAdmins:
                    print(str(self.knownAdmins[peer].ip) + ":" + str(self.knownAdmins[peer].port) + " (" + str(self.knownAdmins[peer].nId) + ")")
                print("**** STUDENTS ****")
                for peer in self.knownStudents:
                    print(str(self.knownStudents[peer].ip) + ":" + str(self.knownStudents[peer].port) + " (" + str(self.knownStudents[peer].nId) + ")")
            # Broadcast again in case the original signal is missed
            elif value == "resendbroadcast" or self.command == "resendbroadcast":
                newport = input("Enter Student Foreame: ")
                self.resendBroadcast(newport)
            elif value == "exit" or self.command == "exit":
                print("Node shutting down")
                self.node_request_to_stop()
                self.stop()
                self.end = True
                                         
    # Start the thread that contains the blockchain console UI
    def startFunctions(self):
        print("STARTING")
        super(ValNode, self).__init__(self.ip, self.port, id=self.nId)
        self.start()
        # Start P2P search
        self.nodeDiscovery()
        if self.cmd == True:
            threading.Thread(target=self.keyboardListener).start()
        
    
    def nodeDiscovery(self):
        if self.port != 5001:
            self.connect_with_node('localhost', 5001)
            
    def stopNode(self):
        self.send = True
        self.stop()
        
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
        print(exNodes)
        msgJson['adminNodes'] = exNodes
        stNodes = []
        for s in self.knownStudents:
            stNodes.append(self.knownStudents[s].toJson())
        msgJson['studentNodes'] = stNodes
        msgJson["pubKeyE"] = self.wallet.pubKey.e
        msgJson["pubKeyN"] = self.wallet.pubKey.n
        msgJson['stake'] = self.consensus.getStake(self.wallet.pubKey)
        if self.bchain.chainLength() > 1:
            msgJson['blockchain'] = self.bchain.toJson()
        else:
            msgJson['blockchain'] = None
        jsonMsg = json.dumps(msgJson)
        newMsg = jsonMsg.encode('utf-8')
        self.send_to_node(connected_node, newMsg)
        
    # Override p2p methods
    # Message back from receiving node (sent from original node to new one)
    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + str(connected_node))
        self.nodeInformationPacket(connected_node)
        print("Enter a command: ")
        
    # Inbound connection when receiving a request to connect/sent a message (sent to original node from new one)
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + str(connected_node))
        self.nodeInformationPacket(connected_node)
        print("Enter a command: ")
        
    # Search nodes to determine if the inbound node is already known
    def searchNodes(self, list, msg):
        for xNode in list:
            if list[xNode].ip == msg['ip'] and list[xNode].port == msg['port'] and list[xNode].nId == msg['nId']:
                return False
        return True
    
    # Check to see if the list of nodes from the inbound node contains any that this node is not aware of and connect to them if so
    def searchStoredNodes(self, list, nodelist, msg):
        newPeer = True
        for node in msg[nodelist]:
            if self.ip == node['ip'] and self.port == node['port'] and self.nId == node['nId']:
                newPeer = False
            if len(list) > 0:
                for xNode in list:
                    if list[xNode].ip == node['ip'] and list[xNode].port == node['port'] and list[xNode].nId == node['nId']:
                        newPeer = False
            if newPeer:
                self.connect_with_node(node['ip'], node['port'])
                
    # Create a new NodeInfo object
    def addNewNode(self, list, msg):
        list[msg['nId']] = NodeInfo(msg['ip'], msg['port'], msg['nId'], msg['pmLvl'])
        self.nodeBalances[msg['nId']] = msg['bal']
    
    # If node is new, take its information and store it
    def newNode(self, msg):
        newNode = True
        # Check the message is not from this node
        if self.ip == msg['ip'] and self.port == msg['port'] and self.nId == msg['nId']:
            newNode = False
        # Check stored nodes
        if msg['pmLvl'] == "admin":
            newNode = self.searchNodes(self.knownAdmins, msg)
        else:
            newNode = self.searchNodes(self.knownStudents, msg)
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
                self.consensus.addNode(pubKey, msg['stake'])
            if msg['blockchain'] != None:
                self.handleInboundBlockchain(msg)
        # Search the node information sent from the connecting node to check for any new nodes
        self.searchStoredNodes(self.knownAdmins, 'adminNodes', msg)
        self.searchStoredNodes(self.knownStudents, 'studentNodes', msg)
            
    # Recreate transactions from incoming messages to operate on
    def recreateTx(self, msg):
        tx = Transaction(rsa.PublicKey(msg['sendPKN'],msg['sendPKE']), rsa.PublicKey(msg['receiverPKN'], msg['receiverPKE']), int(msg['amount']), msg['type'], msg['data'])
        tx.setTX(msg['tId'], msg['tTimestamp'])
        tx.tasOriginalCopy = msg['tasCopy']
        tx.signTransaction(msg['tSig'])
        if tx.type == "NEWRECORD":
            tx.data.encode('latin-1')
            tx.encrypted = True
        return tx
    
    # Recreate blocks from incoming messages to operate on
    def recreateBlock(self, msg, blockTxs):
        if msg['index'] == 0:
            block = Block(blockTxs, msg['index'], msg['prevhash'], msg['validatorN'])
        else:
            block = Block(blockTxs, msg['index'], msg['prevhash'], rsa.PublicKey(msg['validatorN'], msg['validatorE']))
        block.timestamp = msg['timestamp']
        block.hash = msg['hash']
        block.copyBAS()
        block.signature = msg['signature']
        return block
    
    # If the message contains a coin transaction then handle it here
    def handleTxMessage(self, msg):
        # Recreate transaction from message contents
        # If the transaction is a new record is will contain the encrypted data containing the record
        tx = self.recreateTx(msg)
        # Check that the transaction is valid and can be executed
        if self.checkTxValid(tx):
            # If valid, handle the transaction by adding it to the transaction pool
            self.incomingTransaction(tx, msg['tSig'])
        else:
            messagebox.showerror(str(self.nId), "Invalid Transaction")
            print("Invalid Transaction")
            
    # Handle incoming blocks
    def handleBlockMessage(self, msg):
        blockTxs = []
        # Check that the block is not already on the chain
        if msg['index'] > self.bchain.lastBlock().index:
            # Recreate transactions
            for transaction in msg['transactions']:
                jsonTx = json.loads(transaction)
                tx = self.recreateTx(jsonTx)
                blockTxs.append(tx)
            block = self.recreateBlock(msg, blockTxs)
            # Check that the incoming block is actually valid
            valid = False
            # Index should be the same as the amount of blocks on the chain before it is added
            if self.bchain.chainLength() == (block.index):
                # Check 1) the block's previous hash variable is equal to the hash of the last block on the chain
                # Check 2) the block's signature is valid
                # Check 3) the block's validator is valid by running an election under the same parameters and comparing results
                if self.bchain.validateNewBlock(self.bchain.lastBlock(), block) and self.wallet.validateSig(block.basOriginalCopy, block.signature, block.validator) and self.validatorValid(block.validator):
                    valid = True
            else:
                # If the block's index is incorrect attempt to validate the entire blockchain for errors
                if not self.validateChain():
                    # If there is an error send a request to other nodes for the correct chain
                    msg = {}
                    msg['type'] = "CHAINREQ"
                    self.send_to_nodes(msg)
            validatorID = self.nodeKeys[block.validator]
            if valid:
                # If valid retrieve the ID of the block's validator and reward them for being loyal by increasing their balance
                if validatorID in self.knownStudents.keys():
                    self.nodeBalances[validatorID] += 1
                elif validatorID in self.knownAdmins.keys():
                    self.nodeBalances[validatorID] += 2
                # Add block to the chain
                self.bchain.addInboundBlock(block)
                for blockTx in block.transactions:
                    self.handleTransaction(blockTx)
                    if blockTx.type == "NEWRECORD" and self.permissionLvl == "admin":
                        record = self.kms.decrypt(blockTx.data.encode('latin-1'))
                        self.recordIndex[record['sId']] = block.index
                    if blockTx.type == "SENDTOKENS":
                        sender = str(self.nodeKeys[blockTx.senderPK])
                        messagebox.showinfo(str(self.nId), "Received " + str(blockTx.amount) + " from " + sender)
                # Transactions in the block must be removed from the transaction pool
                messagebox.showinfo(str(self.nId), "New Block Added\nValidator: " + str(validatorID))
                print ("Validator: " + str(self.nodeKeys[block.validator]))
                self.txPool.updatePool(block.transactions)
            else:
                # If block is invalid alert the other nodes of the ID of the validator who produced it
                # This ID is publicly displayed and added to a list for university authorities to deal with
                print("Invalid block detected! - Alerting Chain")
                msg = {}
                msg["type"] = "INVALIDBLOCK"
                msg["id"] = self.nodeKeys[block.validator]
                self.send_to_nodes(msg)
                print(str(validatorID) + " has produced an invalid block") 
                print("Their stake has been removed and ID recorded")
                messagebox.showerror(str(self.nId), "Invalid block detected! - Alerting Chain\n" + str(validatorID) + " has produced an invalid block\nTheir Stake has been removed and ID recorded")
                for pubKey in self.nodeKeys:
                    if self.nodeKeys[pubKey] == msg['id']:
                        # Node who produced an invalid block is punished by having their stake removed and burned  
                        self.consensus.nodes[(pubKey.e + pubKey.n)] = 0
                self.invalidCreatorIDs.append(msg['id'])
            
    # Send a copy of this node's chain to another requesting it
    def handleChainRequest(self, connected_node):
        msg = {}
        msg['type'] = "CHAINREP"
        msg['blockchain'] = self.bchain.toJson()
        self.send_to_node(connected_node, msg)
            
    # Take incoming chains and compare with your own to update to a new one
    def handleInboundBlockchain(self, msg):
        newchain = []
        chain = json.loads(msg['blockchain'])
        for cblock in chain['blocks']:
            blockJson = json.loads(cblock)
            blockTxs = []
            for jsonTx in blockJson['transactions']:
                jsonTx = json.loads(jsonTx)
                tx = self.recreateTx(jsonTx)
                blockTxs.append(tx)
            block = self.recreateBlock(blockJson, blockTxs)
            newchain.append(block)
        self.updateToValidChain(newchain)
    
    # Punish nodes who have been found to be producing invalid blocks
    def handleInvalidBlock(self, msg):
        print(str(msg['id']) + " has produced an invalid block") 
        print("Their stake has been removed and ID recorded")
        messagebox.showerror(str(self.nId), "Invalid block detected! - Alerting Chain\n" + str(msg['id']) + " has produced an invalid block\nTheir Stake has been removed and ID recorded")
        for pubKey in self.nodeKeys:
            if self.nodeKeys[pubKey] == msg['id']:  
                self.consensus.nodes[(pubKey.e + pubKey.n)] = 0
        self.invalidCreatorIDs.append(msg['id'])
    
    # When admins receive a request from students to send their decrypted records the admin must search for the student and then send them back
    def handleRecordRequest(self, msg, connected_node):
        result = self.recordSearch(self.bchain.chain, str(msg['sId']))
        msg = {}
        msg['type'] = "RECORDREP"
        if result == None:
            msg['record'] = None
        else:
            msg['record'] = result
        self.send_to_node(connected_node, msg)
        
    def createNewRecord(self, sd):
        record = self.wallet.createTransaction(self.wallet.pubKey, 0, "NEWRECORD", sd)
        msgJson = record.toJson()
        # Send created transaction to other nodes on network
        self.send_to_nodes(msgJson)
        self.incomingTransaction(record, record.tSig)
        
    def requestRecords(self):
        admins = []
        for adminKeys in self.knownAdmins.keys():
            admins.append(str(adminKeys))
        for adminnode in self.all_nodes:
            if adminnode.id in admins:
                msg = {}
                msg["type"] = "RECORDRQ"
                msg['sId'] = self.nId
                self.send_to_node(adminnode, msg)
                print("Request Sent")
    
    def getStudentRecord(self):
        return self.record
        
    # Function for printing student records
    def printRecords(self, record):
        print("Forename: ", record['sForename'])
        print("Surname: ", record['sSurname'])
        print("ID: ", record['sId'])
        print("------------")
        print("Module Grades")
        print("------------")
        for grade in record['sGrades']:
            print(str(grade) + ": " + str(record['sGrades'][grade]))
                            
    # Returned records are printed in an easier to read form
    def handleRecordReply(self, msg):
        record = msg['record']
        if record == None:
            print("Records not found - please contact administrator")
        else:
            self.record = record
            self.printRecords(record)
        self.reply = True
            
    def validateValidator(self, msg, connected_node):
        blockTxs = []
        blockMsg = json.loads(msg['block'])
        for transaction in blockMsg['transactions']:
            jsonTx = json.loads(transaction)
            tx = self.recreateTx(jsonTx)
            blockTxs.append(tx)
        block = self.recreateBlock(blockMsg, blockTxs)
        reply = {}
        reply['type'] = "VALIDATEDBLOCK"
        if self.bchain.validateNewBlock(self.bchain.lastBlock(), block) and self.wallet.validateSig(block.basOriginalCopy, block.signature, block.validator) and self.validatorValid(block.validator):
            for tx in block.transactions:
                if self.wallet.validateSig(tx.tasOriginalCopy, tx.tSig, tx.senderPK):
                    reply['valid'] = "TRUE"
                else:
                    reply['valid'] = "FALSE"
                    self.send_to_node(connected_node, reply)
        else:
            reply['valid'] = "FALSE"
        self.send_to_node(connected_node, reply)
        
        
    def studentBlockValidated(self, msg):
        if self.storedBlock != None:
            if msg['valid'] == "TRUE":
                self.send_to_nodes(self.storedBlock)
                self.storedBlock = None
            else:
                print("Invalid block detected! - Alerting Chain")
                msg = {}
                msg["type"] = "INVALIDBLOCK"
                msg["id"] = self.nId
                self.send_to_nodes(msg)
                print(str(msg['id']) + " has produced an invalid block") 
                print("Their stake has been removed and ID recorded")
                messagebox.showerror(str(self.nId), "Invalid block detected! - Alerting Chain\n" + str(msg['id']) + " has produced an invalid block\nTheir Stake has been removed and ID recorded")
                for pubKey in self.nodeKeys:
                    if self.nodeKeys[pubKey] == msg['id']:
                        # Node who produced an invalid block is punished by having their stake removed and burned  
                        self.consensus.nodes[(pubKey.e + pubKey.n)] = 0
                self.invalidCreatorIDs.append(msg['id'])
        else:
            print("No block")
            
    # Handles incoming messages
    def node_message(self, connected_node, msg):
        if msg['type'] == "NEWNODE":
            self.newNode(msg)
        elif msg['type'] == "SENDTOKENS" or msg['type'] == "ADDSTAKE" or msg['type'] == "SUBSTAKE" or msg['type'] == "NEWSTAKE" or msg['type'] == "NEWRECORD":
            self.handleTxMessage(msg)
        elif msg['type'] == "BLOCK":
            self.handleBlockMessage(msg)
        elif msg['type'] == "CHAINREQ":
            self.handleChainRequest(connected_node)
        elif msg['type'] == "CHAINREP":
            self.handleInboundBlockchain(msg)
        elif msg['type'] == "INVALIDBLOCK":
            self.handleInvalidBlock(msg)
        elif msg['type'] == "INVALIDCHAIN":
            self.handleInvalidChain(msg)
        elif msg['type'] == "RECORDRQ":
            self.handleRecordRequest(msg, connected_node)
        elif msg['type'] == "RECORDREP":
            self.handleRecordReply(msg)
        elif msg['type'] == "STUDENTVALIDATION":
            self.validateValidator(msg, connected_node)
        elif msg['type'] == "VALIDATEDBLOCK":
            self.studentBlockValidated(msg)

    # Return wallet balance
    def getBalance(self):
        return self.wallet.balance
            
    # Handle an incoming transaction
    def incomingTransaction(self, transaction, tSig):
        # Check the transaction is not in the transaction pool and not already in a block on the chain
        if transaction.tId not in self.txPool.txs and not self.bchain.isExistingTx(transaction.tId):
            tData = transaction.tasOriginalCopy
            tSigner = transaction.senderPK
            # Validate that the transaction's signature is valid and has not been forged
            validSig = self.wallet.validateSig(tData, tSig, tSigner)
            if validSig:
                transaction.signTransaction(tSig)
                # If the transaction is valid add it to the pool and send it to other nodes
                self.txPool.addTxToPool(transaction)
                # Check the transaction pool is not empty - if it is not then proceed to create a block to hold the transaction in
                # This can be changed to hold n amount of transactions in a block, but for the purpose of this project n = 1
                if self.txPool.isNotEmpty():
                    # Hold a raffle to see which staker will be the validator for this block
                    # See comments on the PoS class for more information
                    validator = self.consensus.generateValidator(self.bchain.lastBlock().hash)  
                     
                    if validator == None:
                        messagebox.showerror(str(self.nId), "No Validator Chosen")
                        print("Error: No validator")
                    else:
                        # If this node is the validator continue, otherwise wait for the validator to broadcast the block
                        if (self.wallet.pubKey.e + self.wallet.pubKey.n) == validator:
                            if self.permissionLvl == "student":
                                self.wallet.balance += 1
                            else:
                                self.wallet.balance += 2
                            # If validator create a new block and add it to the chain
                            newBlock = self.bchain.addLocalBlock(self.txPool.txs, self.wallet)
                            print("Validator: " + str(self.nId))
                            if newBlock == None:
                                print("Error - no block created!")
                                messagebox.showerror(str(self.nId), "No Block Creaed")
                            else:
                                # Handle each transaction in the block by executing it's function
                                for blockTx in newBlock.transactions:
                                    self.handleTransaction(blockTx)
                                # Remove the transactions held in the block from the transaction pool
                                self.txPool.updatePool(newBlock.transactions)
                                # Broadcast the block to other nodes
                                blockMsg = newBlock.toJson()
                                msg = blockMsg.encode('utf-8')
                                if self.permissionLvl == "student":
                                    admins = []
                                    for adminKeys in self.knownAdmins.keys():
                                        admins.append(str(adminKeys))
                                    for adminnode in self.all_nodes:
                                        if adminnode.id in admins:
                                            msg2 = {}
                                            msg2["type"] = "STUDENTVALIDATION"
                                            msg2["block"] = blockMsg
                                            self.storedBlock = blockMsg
                                            self.send_to_node(adminnode, msg2)
                                            print("Block Sent To Admins For Validation")
                                else:
                                    self.send_to_nodes(msg)
    
    # Check each transaction can actually be executed before being added to the block
    # The amount being sent/staked should be more than the amount held in the respective users wallet                        
    def handleTx(self, tx, senderKey, myKey, errorMsg):
        if senderKey == myKey:
            if self.wallet.balance >= tx.amount : 
                return True
            else:
                messagebox.showerror(str(self.nId), errorMsg)
                print(errorMsg)
                return False
        else:
            if self.nodeBalances[tx.senderPK] >= tx.amount : 
                return True
            else:
                messagebox.showerror(str(self.nId), errorMsg)
                print("errorMsg")
                return False
    
    # Check each transaction can actually be executed before being added to the block
    # Amount being unstaked should be more than is being staked currently by the user
    def handleSubStakeTx(self, tx, senderKey):
        if self.consensus[tx.senderPK] >= tx.amount: 
            return True
        else:
            messagebox.showerror(str(self.nId), "Insufficient funds to withdraw")
            print("Insufficient funds to withdraw")
            return False
        
    # Reformat public keys into strings    
    def handleKeys(self, tx):
        senderKey = tx.senderPK
        receiveKey = tx.receiverPK
        myKey = self.wallet.pubKey
        return senderKey, receiveKey, myKey
    
    # Check each transaction can actually be executed before being added to the block depending on its type
    # Also ensure that the sender/receiver actually exists on the network
    def checkTxValid(self, tx):
        senderKey, receiveKey, myKey = self.handleKeys(tx)
        isValidTx = False
        if (senderKey in self.nodeKeys.keys() or senderKey == myKey) and (receiveKey in self.nodeKeys.keys() or receiveKey == myKey):
            if tx.type == "NEWSTAKE" or tx.type == "ADDSTAKE":
                isValidTx = self.handleTx(tx, senderKey, myKey, "Insufficient funds to stake")
            elif tx.type == "SUBSTAKE":
                isValidTx = self.handleTx(tx, senderKey, myKey, "Insufficient funds to add to stake")
            elif tx.type == "SUBSTAKE":
                isValidTx = self.handleSubStakeTx(tx, senderKey)
            elif tx.type == "SENDTOKENS":
                isValidTx = self.handleTx(tx, senderKey, myKey, "Insufficient funds to send")
            elif tx.type == "NEWRECORD":
                isValidTx = True
        else:
            messagebox.showerror(str(self.nId), "Sender or receiver not found")
            print("Sender or receiver not found")
        
        return isValidTx
            
    # If transactions are valid, execute them                        
    def handleTransaction(self, tx):
        senderKey, receiveKey, myKey = self.handleKeys(tx)
        if tx.type == "NEWSTAKE":
            id = self.nodeKeys[tx.senderPK]
            self.nodeBalances[id] -= tx.amount
            self.consensus.addNode(tx.senderPK, tx.amount)
        if tx.type == "ADDSTAKE":
            if senderKey == myKey:
                self.wallet.balance -= tx.amount
            else:
                id = self.nodeKeys[tx.senderPK]
                self.nodeBalances[id] -= tx.amount
            self.consensus.addStake(tx.senderPK, tx.amount)
        if tx.type == "SUBSTAKE":
            if senderKey == myKey:
                self.wallet.balance -= tx.amount
            else:
                id = self.nodeKeys[tx.senderPK]
                self.nodeBalances[id] += tx.amount
            self.consensus.subStake(tx.senderPK, tx.amount)
        elif tx.type == "SENDTOKENS":
            if senderKey == myKey:
                self.wallet.balance -= tx.amount
                id = self.nodeKeys[tx.receiverPK]
                self.nodeBalances[id] += tx.amount
            elif receiveKey == myKey:
                id = self.nodeKeys[tx.senderPK]
                self.nodeBalances[id] -= tx.amount
                self.wallet.balance += tx.amount
            else:
                id = self.nodeKeys[tx.senderPK]
                self.nodeBalances[id] -= tx.amount
                id2 = self.nodeKeys[tx.receiverPK]
                self.nodeBalances[id2] += tx.amount
        elif tx.type == "NEWRECORD":
            print("New record added")
    
    # Validate this nodes chain is correct
    # The index of each block should follow on from the next one, and the hash chain should be intact    
    def validateChain(self):
        if (self.bchain.chainLength() > 1):
            # Compare each block against the one after it to ensure integrity
            for b in range(0, len(self.bchain.chain) -1):
                if self.bchain.validateNewBlock(self.bchain.chain[b], self.bchain.chain[b+1]):
                    continue
                else:
                    # If the chain is invalid the stake is removed as this node may be a risk of being untrustworthy
                    print("Invalid chain - Stake removed")
                    messagebox.showerror(str(self.nId), "Invalid chain - stake removed")
                    self.consensus.nodes[(self.wallet.pubKey.e + self.wallet.pubKey.e)] = 0
                    msg = {}
                    msg["type"] = "INVALIDCHAIN"
                    msg["id"] = self.nId
                    self.send_to_nodes(msg)
                    return False
        return True
    
    # Validate that the chain sent by other nodes is correct so the node does not update to another invalid chain
    def validateNewChain(self, chain):
        if (len(chain) > 1):
            for b in range(0, len(chain) -1):
                if self.bchain.validateNewBlock(chain[b], chain[b+1]):
                    continue
                else:
                    return False
        return True
    
    # The new chain must not only be valid, but also as a principle longer than the existing chain for it to be replaced
    # The genesis block's must be the same so the hashing chains can produce the same results for comparison
    # If valid and longe replace the existing chain with the new one and remove transactions in the blocks from the transaction pool 
    def updateToValidChain(self, newChain):
        if self.validateNewChain(newChain) and len(newChain) > len(self.bchain.chain) and self.bchain.genesisBlock().hash == newChain[0].hash:
            self.bchain.chain = newChain  
            for block in newChain:
                self.txPool.updatePool(block.transactions)
    
    # Hold a raffle with the same seed in order to produce the winner locally and compare against the validator of the block sent by other nodes        
    def validatorValid(self, val):
        if self.consensus.generateValidator(self.bchain.lastBlock().hash) == (val.e + val.n):
            return True
        else:
            return False      

    # Search for a students records based on their student ID
    # Student may have multiple records on the chain, so return the latest one
    def recordSearch(self, chain, id):
        if id in self.recordIndex.keys():
            index = self.recordIndex[id]
            recordBlock = self.bchain.getBlock(index)
            for tx in recordBlock.transactions:
                if self.kms == None:
                    return False
                record = self.kms.decrypt(tx.data.encode('latin-1'))
                if record['sId'] == id:
                    return record
        validTransaction = None
        validData = None
        for block in chain:
            for transaction in block.transactions:
                if transaction.data != None:
                    # The transaction is encrypted on the chain so the admin account must use their AWS KMS credentials and decrpyt it
                    if self.kms == None:
                        return False
                    record = self.kms.decrypt(transaction.data.encode('latin-1'))
                    if record['sId'] == id:
                        if validTransaction == None:
                            validData = record
                        else:
                            # Check this is the newest record
                            if transaction.tTimestamp > validTransaction.tTimestamp:
                                validData = record
        return validData
    # Resend the broadcast message to a specified node as an emergency measure
    def resendBroadcast(self, nodePort):
        self.connect_with_node('localhost', nodePort)