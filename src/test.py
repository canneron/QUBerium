from hashlib import sha256
import json
from subprocess import PIPE, Popen
import time
import unittest
from unittest import mock
from unittest.mock import patch
import rsa
from block import Block
from blockchain import Blockchain
from kms import KMS
from nodeinfo import NodeInfo
from pos import PoS
from studentdata import StudentData
from transaction import Transaction
from txpool import TxPool
from valnode import ValNode
from wallet import Wallet

class TestBlock(unittest.TestCase):
    pubKey1 = rsa.PublicKey(1, 2)
    pubKey2 = rsa.PublicKey(3, 4)
    tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
    block = Block([tx], 0, 0, "Validator")
    block.copyBAS()

    def test_givenBlock_whenCreated_thenProduceJSON(self):
        block = Block([self.tx], 0, 0, "Validator")
        bJson = block.toJson()
        bJson = json.loads(bJson)
        hash = sha256(block.blockAsString().encode("utf-8")).hexdigest()
        self.assertEqual(bJson['index'], 0, "Should be 0")
        self.assertEqual(bJson['validatorE'], "Validator", "Should be validator")
        self.assertEqual(bJson['signature'], "", "Should be null")
        self.assertEqual(bJson['type'], "BLOCK", "Should be block")
        self.assertEqual(bJson['hash'], hash, "Should be hash")
        print ("Success")
        
    def test_givenBlock_whenCreated_thenLoadCorrectDataTypes(self):
        bJson = self.block.toJson()
        bJson = json.loads(bJson)
        self.assertNotEqual(bJson['index'], "0", "Should be 0")
        self.assertNotEqual(bJson['signature'], None, "Should be null")
        self.assertNotEqual(bJson['type'], "block", "Should be block")
        print ("Success")
        
    def test_givenGenesisBlock_whenCreated_thenCreateGBlock(self):
        gBlock = Block.genesisBlock()
        hash = sha256(gBlock.blockAsString().encode("utf-8")).hexdigest()
        self.assertEqual(gBlock.transactions, [], "Should be empty")
        self.assertEqual(gBlock.index, 0, "Should be 0")
        self.assertEqual(gBlock.timestamp, 0, "Should be 0")
        self.assertEqual(gBlock.prevhash, "genesis", "Should be genesis")
        self.assertEqual(gBlock.signature, '', "Should be empty")
        self.assertEqual(gBlock.type, "BLOCK", "Should be  BLOCK")
        self.assertEqual(gBlock.hash, hash, "Should be hash")
        
    def test_givenBlock_whenSigned_thenStoreSignature(self):
        kspub, pspriv = rsa.newkeys(1024)
        sig = rsa.sign(self.block.blockAsString().encode('utf-8'), pspriv, 'SHA-256').hex()
        self.block.signBlock(sig)
        self.assertEqual(self.block.signature, sig, "Should be sig")
        
    def test_givenBAS_whenSigned_thenRaiseErrorVerifyingSig(self):
        kspub, pspriv = rsa.newkeys(1024)
        sig = rsa.sign(self.block.blockAsString().encode('utf-8'), pspriv, 'SHA-256').hex()
        self.block.signBlock(sig)
        data = self.block.blockAsString().encode('utf-8')
        with self.assertRaises(rsa.VerificationError) as context:
            rsa.verify(data, bytes.fromhex(self.block.signature), kspub)
            
        self.assertTrue(type(context.exception) == rsa.VerificationError)
        
    def test_givenBAS_whenNotSigned_thenVerifySig(self):
        kspub, pspriv = rsa.newkeys(1024)
        sig = rsa.sign(self.block.blockAsString().encode('utf-8'), pspriv, 'SHA-256').hex()
        self.block.signBlock(sig)
        data = self.block.basOriginalCopy.encode('utf-8')
        self.assertTrue(rsa.verify(data, bytes.fromhex(self.block.signature), kspub))
   
class TestTransaction(unittest.TestCase):
    pubKey1 = rsa.PublicKey(1, 2)
    pubKey2 = rsa.PublicKey(3, 4)
    sd = StudentData("Test", "Test", "1", {"Test" : "Case"})

    def test_givenTransaction_whenCreated_thenProduceJSON(self):
        tx = Transaction(self.pubKey1, self.pubKey2, "100", "SENDTOKENS")
        tJson = tx.toJson()
        tJson = json.loads(tJson)
        self.assertEqual(tJson['sendPKE'], self.pubKey1.e, "Should be e")
        self.assertEqual(tJson['sendPKN'], self.pubKey1.n, "Should be n")
        self.assertEqual(tJson['receiverPKE'], self.pubKey2.e, "Should be e")
        self.assertEqual(tJson['receiverPKN'], self.pubKey2.n, "Should be n")
        self.assertEqual(tJson['amount'], "100", "Should be 100")
        self.assertEqual(tJson['data'], None, "Should be None")
        self.assertEqual(tJson['type'], "SENDTOKENS", "Should be SENDTOKENS")
        self.assertEqual(tJson['tSig'], '', "Should be null")
        print ("Success")
        
    def test_givenTransaction_whenSetTx_thenChangeTxData(self):
        tx = Transaction(self.pubKey1, self.pubKey2, "100", "SENDTOKENS")
        oldId = tx.tId
        oldTs = tx.tTimestamp
        tx.setTX(10, 100)
        self.assertNotEqual(oldId, tx.tId)
        self.assertNotEqual(oldTs, tx.tTimestamp)
        print ("Success")

    def test_givenTransaction_whenSigned_thenStoreSignature(self):
        tx = Transaction(self.pubKey1, self.pubKey2, "100", "SENDTOKENS")
        kspub, pspriv = rsa.newkeys(1024)
        sig = rsa.sign(tx.transactionAsString().encode('utf-8'), pspriv, 'SHA-256').hex()
        tx.signTransaction(sig)
        self.assertEqual(tx.tSig, sig, "Should be sig")
        
    def test_givenTAS_whenSigned_thenRaiseErrorVerifyingSig(self):
        tx = Transaction(self.pubKey1, self.pubKey2, "100", "SENDTOKENS")
        kspub, pspriv = rsa.newkeys(1024)
        sig = rsa.sign(tx.transactionAsString().encode('utf-8'), pspriv, 'SHA-256').hex()
        tx.signTransaction(sig)
        data = tx.transactionAsString().encode('utf-8')
        with self.assertRaises(rsa.VerificationError) as context:
            rsa.verify(data, bytes.fromhex(tx.tSig), kspub)
            
        self.assertTrue(type(context.exception) == rsa.VerificationError)
        
    def test_givenTAS_whenNotSigned_thenVerifySig(self):
        tx = Transaction(self.pubKey1, self.pubKey2, "100", "SENDTOKENS")
        kspub, pspriv = rsa.newkeys(1024)
        sig = rsa.sign(tx.transactionAsString().encode('utf-8'), pspriv, 'SHA-256').hex()
        tx.signTransaction(sig)
        data = tx.tasOriginalCopy.encode('utf-8')
        self.assertTrue(rsa.verify(data, bytes.fromhex(tx.tSig), kspub))
        
class TestBlockchain(unittest.TestCase):

    def test_givenNewBlockchain_whenCreated_thenAddGenesisBlock(self):
        bchain = Blockchain()
        gBlock = Block.genesisBlock()
        self.assertTrue(len(bchain.chain) == 1)
        self.assertEqual(bchain.chain[-1].index, gBlock.index)
        self.assertEqual(bchain.chain[-1].hash, gBlock.hash)
        self.assertEqual(bchain.chain[-1].validator, gBlock.validator)
        
    def test_givenBlockchain_whenReturningGenesisBlock_thenReturnGenesisBlock(self):
        bchain = Blockchain()
        gBlock = Block.genesisBlock()
        self.assertTrue(len(bchain.chain) == 1)
        self.assertEqual(bchain.genesisBlock().index, gBlock.index)
        self.assertEqual(bchain.genesisBlock().hash, gBlock.hash)
        self.assertEqual(bchain.genesisBlock().validator, gBlock.validator)
        
    def test_givenBlockchain_whenUsingchainLength_thenReturnLength(self):
        bchain = Blockchain()
        self.assertTrue(bchain.chainLength() == 1)
        
    def test_givenBlockchain_whenUsingchainLength_thenReturnLength(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        self.assertTrue(len(bchain.chain) == 2)
        self.assertEqual(bchain.lastBlock().index, block.index)
        self.assertEqual(bchain.lastBlock().hash, block.hash)
        self.assertEqual(bchain.lastBlock().validator, block.validator)
        
    def test_givenBlockchain_whenUsingGettingBlock_thenReturnBlock(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        self.assertTrue(len(bchain.chain) == 2)
        self.assertEqual(bchain.getBlock(1).index, block.index)
        self.assertEqual(bchain.getBlock(1).hash, block.hash)
        self.assertEqual(bchain.getBlock(1).validator, block.validator)
           
    def test_givenNewBlock_whenOnlyGenesisBlock_thenReturnTrue(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        self.assertTrue(bchain.validateNewBlock(bchain.genesisBlock(), block))
        
    def test_givenNewBlock_whenNotGenesisBlock_thenReturnTrue(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        block2 = Block([tx, tx2], bchain.chainLength(), bchain.lastBlock().hash, pubKey2)
        self.assertTrue(bchain.validateNewBlock(bchain.lastBlock(), block2))
        
    def test_givenNewBlock_whenNotValidIndex_thenReturnFalse(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        block2 = Block([tx, tx2], bchain.chainLength(), bchain.lastBlock().hash, pubKey2)
        bchain.lastBlock().index = 2
        self.assertFalse(bchain.validateNewBlock(bchain.lastBlock(), block2))   
        
    def test_givenNewBlock_whenSameAsLastBlock_thenReturnFalse(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        block2 = Block([tx], 1, bchain.genesisBlock().hash , pubKey1)
        self.assertFalse(bchain.validateNewBlock(bchain.lastBlock(), block2))
        
    def test_givenNewBlock_whenNotValidHash_thenReturnFalse(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        block2 = Block([tx, tx2], bchain.chainLength(), bchain.lastBlock().hash, pubKey2)
        bchain.lastBlock().validator = pubKey2
        self.assertFalse(bchain.validateNewBlock(bchain.lastBlock(), block2))   
        
    def test_givenNewBlock_whenNotValidTimestamp_thenReturnFalse(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        block2 = Block([tx, tx2], bchain.chainLength(), bchain.lastBlock().hash, pubKey2)
        time.sleep(0.05)
        bchain.lastBlock().timestamp = time.time_ns()
        self.assertFalse(bchain.validateNewBlock(bchain.lastBlock(), block2))
        
    def test_givenNewBlock_whenFilteringTransactions_thenReturnTrue(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        self.assertTrue(bchain.isExistingTx(tx.tId))
        
    def test_givenNewBlock_whenFilteringTransactions_thenReturnFalse(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        self.assertFalse(bchain.isExistingTx(tx2.tId))
        
    def test_givenNewValidInboundBlock_whenAddingToChainWithGenesisBlock_thenAddBlock(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.addInboundBlock(block)
        self.assertTrue(len(bchain.chain) == 2)
        self.assertEqual(bchain.lastBlock().index, block.index)
        self.assertEqual(bchain.lastBlock().hash, block.hash)
        self.assertEqual(bchain.lastBlock().validator, block.validator)
        
    def test_givenNewValidInboundBlock_whenAddingToChain_thenAddBlock(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        block2 = Block([tx, tx2], bchain.chainLength(), bchain.lastBlock().hash, pubKey2)
        bchain.addInboundBlock(block)
        bchain.addInboundBlock(block2)
        self.assertTrue(len(bchain.chain) == 3)
        self.assertEqual(bchain.lastBlock().index, block2.index)
        self.assertEqual(bchain.lastBlock().hash, block2.hash)
        self.assertEqual(bchain.lastBlock().validator, block2.validator)
        
    def test_givenNewInvalidInboundBlock_whenAddingToChain_thenDontAddBlock(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        block2 = Block([tx, tx2], bchain.chainLength(), bchain.genesisBlock().hash, pubKey2)
        bchain.addInboundBlock(block)
        bchain.addInboundBlock(block2)
        self.assertTrue(len(bchain.chain) == 2)
        self.assertNotEqual(bchain.lastBlock().index, block2.index)
        self.assertNotEqual(bchain.lastBlock().hash, block2.hash)
        self.assertNotEqual(bchain.lastBlock().validator, block2.validator)
        self.assertEqual(bchain.lastBlock().index, block.index)
        self.assertEqual(bchain.lastBlock().hash, block.hash)
        self.assertEqual(bchain.lastBlock().validator, block.validator)
        
    def test_givenNewValidLocalBlock_whenAddingToChainWithGenesisBlock_thenAddBlock(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        txs = []
        txs.append(tx)
        wallet = Wallet()
        bchain.addLocalBlock(txs, wallet)
        self.assertTrue(len(bchain.chain) == 2)
        self.assertEqual(bchain.lastBlock().index, len(bchain.chain) - 1)
        self.assertEqual(bchain.lastBlock().transactions[0].tId, tx.tId)
        self.assertEqual(bchain.lastBlock().validator, wallet.pubKey)
        
    def test_givenNewValidLocalBlock_whenAddingToChain_thenAddBlock(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        bchain.addInboundBlock(block)
        txs = []
        txs.append(tx)
        txs.append(tx2)
        wallet = Wallet()
        bchain.addLocalBlock(txs, wallet)
        self.assertTrue(len(bchain.chain) == 3)
        self.assertEqual(bchain.lastBlock().index, len(bchain.chain) - 1)
        self.assertEqual(bchain.lastBlock().transactions[0].tId, tx.tId)
        self.assertEqual(bchain.lastBlock().transactions[1].tId, tx2.tId)
        self.assertEqual(bchain.lastBlock().validator, wallet.pubKey)
        
    def test_givenNewInvalidLocalBlock_whenAddingToChain_thenDontAddBlock(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        bchain = Blockchain()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], bchain.chainLength(), bchain.lastBlock().hash, pubKey1)
        bchain.chain.append(block)
        block2 = Block([tx, tx2], bchain.chainLength(), bchain.genesisBlock().hash, pubKey2)
        bchain.addInboundBlock(block)
        bchain.addInboundBlock(block2)
        self.assertTrue(len(bchain.chain) == 2)
        self.assertNotEqual(bchain.lastBlock().index, block2.index)
        self.assertNotEqual(bchain.lastBlock().hash, block2.hash)
        self.assertNotEqual(bchain.lastBlock().validator, block2.validator)
        self.assertEqual(bchain.lastBlock().index, block.index)
        self.assertEqual(bchain.lastBlock().hash, block.hash)
        self.assertEqual(bchain.lastBlock().validator, block.validator)
        
class TestStudentData(unittest.TestCase):
    
    def test_givenStudentData_whenCreated_thenProduceJSON(self):
        sd = StudentData("Cameron", "McGreevy", "10", {"Test":"1"})
        sJson = sd.toDict()
        self.assertEqual(sJson['sForename'], "Cameron", "Should be Cameron")
        self.assertEqual(sJson['sSurname'], "McGreevy", "Should be McGreevy")
        self.assertEqual(sJson['sId'], "10", "Should be 10")
        sDict = sJson['sGrades']
        for key in sDict.keys():
            keys = key
        self.assertEqual(keys, "Test", "Should be Test")
        self.assertEqual(sDict[keys], "1", "Should be 1")
        print ("Success")    
        
class TestNodeInfo(unittest.TestCase):
    
    def test_givenNodeInfo_whenCreated_thenProduceJSON(self):
        nodeinfo = NodeInfo(1, 2, 3, "admin")
        nJson = nodeinfo.toJson()
        self.assertEqual(nJson['ip'], 1, "Should be 1")
        self.assertEqual(nJson['port'], 2, "Should be 2")
        self.assertEqual(nJson['nId'], 3, "Should be 3")
        self.assertEqual(nJson['pmLvl'], "admin", "Should be admin")
        print ("Success")    
        
class TestTxPool(unittest.TestCase):
    pool = TxPool()
    
    def test_givenNewPool_whenCreated_thenPoolIsEmpty(self):
        self.assertEqual(self.pool.txs, [], "Should be empty")
        print ("Success")
        
    def test_givenNewValidTx_whenAddingToPool_thenAddToPool(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        self.pool.addTxToPool(tx)
        self.assertEqual(self.pool.txs, [tx], "Should contain tx")
        print ("Success")
        
    def test_givenNewValidTx_whenAlreadyInPool_thenDontAddToPool(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(4, 3)
        pool = TxPool()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        pool.addTxToPool(tx)
        pool.addTxToPool(tx)
        self.assertNotEqual(pool.txs, [tx, tx], "Should contain tx")
        self.assertEqual(pool.txs, [tx], "Should contain tx")
        print ("Success")
        
    def test_givenEmptyPool_whenCheckingIfEmpty_thenReturnFalse(self):
        pool = TxPool()
        self.assertFalse(pool.isNotEmpty())
        print ("Success")
        
    def test_givenNotEmptyPool_whenCheckingIfEmpty_thenReturnTrue(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(4, 3)
        pool = TxPool()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        pool.addTxToPool(tx)
        self.assertTrue(pool.isNotEmpty())
        print ("Success")
        
    def test_givenPool_whenRemovingTransactionsInBlock_thenUpdatePool(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(4, 3)
        pool = TxPool()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "SENDTOKENS")
        pool.addTxToPool(tx)
        pool.addTxToPool(tx2)
        remove = [tx]
        pool.updatePool(remove)
        for transaction in pool.txs:
            self.assertTrue(transaction.tId == tx2.tId)
        self.assertFalse(tx in pool.txs)
        print ("Success")
        
    def test_givenPool_whenNoTxsToRemove_thenKeepPool(self):
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(4, 3)
        pool = TxPool()
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "SENDTOKENS")
        tx3 = Transaction(pubKey2, pubKey1, "10", "ADDSTAKE")
        pool.addTxToPool(tx)
        pool.addTxToPool(tx2)
        remove = [tx, tx2, tx3]
        pool.updatePool(remove)
        self.assertTrue(pool.isNotEmpty())
        tx1In = False
        tx2In = False
        tx3In = False
        for transaction in pool.txs:
            if transaction.tId == tx.tId:
                tx1In = True
            if transaction.tId == tx2.tId:
                tx2In = True
            if transaction.tId == tx3.tId:
                tx3In = True
        self.assertFalse(tx1In)
        self.assertFalse(tx2In)
        self.assertTrue(tx3In)
        print ("Success")
        
class TestPoS(unittest.TestCase):
    
    def test_givenNewPoS_whenInitialising_thenAddNode(self):      
        pubKey1 = rsa.PublicKey(1, 2)
        stake = 10
        pos = PoS(pubKey1, stake)
        self.assertEqual(pos.nodes[pubKey1.n + pubKey1.e], 10)   

    def test_givenNewNode_whenAddingToPool_thenAddNode(self):   
        pubKey1 = rsa.PublicKey(1, 2)
        stake = 10
        pos = PoS(pubKey1, stake)
        pubKey2 = rsa.PublicKey(3, 2)
        stake = 100
        pos.addNode(pubKey2, stake)
        self.assertEqual(pos.nodes[pubKey2.n + pubKey2.e], 100)   

    def test_givenDuplicateNode_whenAddingToPool_thenDontAddNode(self):    
        pubKey1 = rsa.PublicKey(1, 2)
        stake = 10
        pos = PoS(pubKey1, stake)
        pubKey2 = rsa.PublicKey(3, 4)
        stake = 100
        stake2 = 50
        pos.addNode(pubKey2, stake)
        pos.addNode(pubKey2, stake2)
        self.assertEqual(pos.nodes[pubKey2.n + pubKey2.e], 100)
        self.assertTrue(len(pos.nodes) == 2)
    
    def test_givenStakingNode_whenAddingStake_thenAddStake(self):    
        pubKey1 = rsa.PublicKey(1, 2)
        stake = 10
        pos = PoS(pubKey1, stake)
        addStake = 10
        pos.addStake(pubKey1, addStake)
        self.assertEqual(pos.nodes[pubKey1.n + pubKey1.e], 20)
    
    def test_givenNotStakingNode_whenAddingStake_thenDontAddStake(self):    
        pubKey1 = rsa.PublicKey(1, 2)
        stake = 10
        pos = PoS(pubKey1, stake)
        pubKey2 = rsa.PublicKey(3, 4)
        addStake = 10
        pos.addStake(pubKey2, addStake)
        #self.assertTrue(pos.nodes[pubKey1.n + pubKey1.e], 20)

    def test_givenStakingNode_whenSubbingStake_thenSubtractStake(self):    
        pubKey1 = rsa.PublicKey(1, 2)
        stake = 10
        pos = PoS(pubKey1, stake)
        subStake = 5
        pos.subStake(pubKey1, subStake)
        self.assertEqual(pos.nodes[pubKey1.n + pubKey1.e], 5)

    def test_givenStakingNode_whenGettingStake_thenReturnStake(self):    
        pubKey1 = rsa.PublicKey(1, 2)
        stake = 10
        pos = PoS(pubKey1, stake)
        self.assertTrue(pos.getStake(pubKey1) == 10)
        
    def test_givenNotStakingNode_whenGettingStake_thenReturn0(self):    
        pubKey1 = rsa.PublicKey(1, 2)
        stake = 10
        pos = PoS(pubKey1, stake)
        pubKey2 = rsa.PublicKey(3, 4)
        self.assertTrue(pos.getStake(pubKey2) == 0)
        
    def test_givenStakingPool_whenChoosingValidator_thenReturnValidator(self):    
        pubKey1 = rsa.PublicKey(1, 2)
        stake = 1
        pos = PoS(pubKey1, stake)
        pubKey2 = rsa.PublicKey(3, 4)
        stake2 = 1
        pos.addStake(pubKey2, stake2)
        pubKey3 = rsa.PublicKey(5, 6)
        stake3 = 1
        pos.addStake(pubKey3, stake3)
        val = pos.generateValidator("10")
        self.assertEqual((pubKey1.n + pubKey1.e),  val)

class TestAWSKMS(unittest.TestCase):
    
    def test_givenReadingConfigFile_whenInitialising_thenStoreCredentials(self):      
        kms = KMS()
        self.assertEqual(kms.kmsAccessKey, "AKIAUO3TR7MONUBXVAMM")
        self.assertEqual(kms.kmsSecretAccessKey, "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")
        self.assertEqual(kms.keyARN, "arn:aws:kms:eu-north-1:306795641628:key/mrk-e18c864059a644e898e71af9a4a3acf0")
        self.assertEqual(kms.arnRegion, "eu-north-1")
        
    def test_givenUnencryptedString_whenEncrypting_thenEncryptString(self):      
        kms = KMS()
        teststring = "This is a test string"
        cipher = kms.encrypt(teststring)
        self.assertNotEqual(teststring, cipher)
        
    def test_givenEncryptedJSON_whenUnencrypting_thenDecryptJSON(self):      
        kms = KMS()
        testdict = {"TEST" : "KEY"}
        cipher = kms.encrypt(testdict)
        self.assertNotEqual(testdict, cipher)
        unencryptedcipher = kms.decrypt(cipher)
        self.assertEqual(unencryptedcipher, testdict)
        
class TestAWSKMS(unittest.TestCase):
    
    def test_givenReadingConfigFile_whenInitialising_thenStoreCredentials(self):      
        kms = KMS()
        self.assertEqual(kms.kmsAccessKey, "AKIAUO3TR7MONUBXVAMM")
        self.assertEqual(kms.kmsSecretAccessKey, "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")
        self.assertEqual(kms.keyARN, "arn:aws:kms:eu-north-1:306795641628:key/mrk-e18c864059a644e898e71af9a4a3acf0")
        self.assertEqual(kms.arnRegion, "eu-north-1")
        
class TestWallet(unittest.TestCase):
    
    def test_givenNewWallet_whenNotAdmin_thenCreateNonAdminWallet(self):      
        wallet = Wallet()
        self.assertEqual(wallet.balance, 0)
        self.assertEqual(wallet.adminKey, None)
        self.assertEqual(type(wallet.privKey), rsa.PrivateKey)
        
    def test_givenNewWallet_whenNotAdmin_thenCreateNonAdminWallet(self):      
        kms = KMS()
        wallet = Wallet(kms)
        self.assertEqual(wallet.balance, 0)
        self.assertEqual(wallet.adminKey, kms)
        self.assertEqual(type(wallet.privKey), rsa.PrivateKey)
        
    def test_givenSignature_whenUsingsigSignFunction_thenReturnSignature(self):      
        wallet = Wallet()
        data = "test data"
        sig = wallet.sigSign(data.encode('utf-8'))
        self.assertTrue(rsa.verify(data.encode('utf-8'), bytes.fromhex(sig), wallet.pubKey))
               
    def test_givenAdminWallet_whenCreatingRecordTransaction_thenCreateRecordTransaction(self):      
        kms = KMS()
        wallet = Wallet(kms)
        self.assertEqual(wallet.adminKey, kms)  
        receiver = rsa.PublicKey(3, 4)
        amount = "10"
        type = "NEWRECORD"
        data = StudentData("Cameron", "McGreevy", "9", {"TEST" : "CASE"})
        tx = wallet.createTransaction(receiver, amount, type, data)
        self.assertTrue(rsa.verify(tx.tasOriginalCopy.encode('utf-8'), bytes.fromhex(tx.tSig), wallet.pubKey))
        self.assertNotEqual(data.toDict(), tx.data)
        self.assertEqual(receiver, tx.receiverPK)
        self.assertEqual(amount, tx.amount)
        self.assertEqual(tx.type, "NEWRECORD")
        
    def test_givenStudentWallet_whenCreatingRecordTransaction_thenCreateRecordTransactionWithNoRecord(self):      
        wallet = Wallet() 
        receiver = rsa.PublicKey(3, 4)
        amount = "10"
        type = "NEWRECORD"
        data = StudentData("Cameron", "McGreevy", "9", {"TEST" : "CASE"})
        tx = wallet.createTransaction(receiver, amount, type, data)
        self.assertTrue(rsa.verify(tx.tasOriginalCopy.encode('utf-8'), bytes.fromhex(tx.tSig), wallet.pubKey))
        self.assertEqual(data, tx.data)
        self.assertEqual(receiver, tx.receiverPK)
        self.assertEqual(amount, tx.amount)
        self.assertEqual(tx.type, "NEWRECORD")
        
    def test_givenAdminWallet_whenCreatingTokenTransaction_thenCreateTokenTransaction(self):      
        kms = KMS()
        wallet = Wallet(kms)
        self.assertEqual(wallet.adminKey, kms)  
        receiver = rsa.PublicKey(3, 4)
        amount = "10"
        type = "SENDTOKENS"
        tx = wallet.createTransaction(receiver, amount, type)
        self.assertTrue(rsa.verify(tx.tasOriginalCopy.encode('utf-8'), bytes.fromhex(tx.tSig), wallet.pubKey))
        self.assertEqual(None, tx.data)
        self.assertEqual(receiver, tx.receiverPK)
        self.assertEqual(amount, tx.amount)
        self.assertEqual(tx.type, "SENDTOKENS")
        
    def test_givenStudentWallet_whenCreatingTokenTransaction_thenCreateTokenTransaction(self):
        wallet = Wallet()
        self.assertEqual(wallet.adminKey, None)  
        receiver = rsa.PublicKey(3, 4)
        amount = "10"
        type = "SENDTOKENS"
        tx = wallet.createTransaction(receiver, amount, type)
        self.assertTrue(rsa.verify(tx.tasOriginalCopy.encode('utf-8'), bytes.fromhex(tx.tSig), wallet.pubKey))
        self.assertEqual(None, tx.data)
        self.assertEqual(receiver, tx.receiverPK)
        self.assertEqual(amount, tx.amount)
        self.assertEqual(tx.type, "SENDTOKENS")
    
    def test_givenAdminWallet_whenCreatingBlock_thenCreateBlock(self):      
        kms = KMS()
        wallet = Wallet(kms)
        self.assertEqual(wallet.adminKey, kms)  
        receiver = rsa.PublicKey(3, 4)
        amount = "10"
        type = "SENDTOKENS"
        tx = wallet.createTransaction(receiver, amount, type)
        block = wallet.createBlock([tx], 3049, "test", wallet.pubKey)
        self.assertTrue(rsa.verify(block.basOriginalCopy.encode('utf-8'), bytes.fromhex(block.signature), wallet.pubKey))
        self.assertEqual(3049, block.index)
        self.assertEqual("test", block.prevhash)
        self.assertEqual(wallet.pubKey, block.validator)
        self.assertEqual([tx], block.transactions)
            
    def test_givenStudentWallet_whenCreatingBlock_thenCreateBlock(self):    
        wallet = Wallet()
        self.assertEqual(wallet.adminKey, None)  
        receiver = rsa.PublicKey(3, 4)
        amount = "10"
        type = "SENDTOKENS"
        tx = wallet.createTransaction(receiver, amount, type)
        block = wallet.createBlock([tx], 3049, "test", wallet.pubKey)
        self.assertTrue(rsa.verify(block.basOriginalCopy.encode('utf-8'), bytes.fromhex(block.signature), wallet.pubKey))
        self.assertEqual(3049, block.index)
        self.assertEqual("test", block.prevhash)
        self.assertEqual(wallet.pubKey, block.validator)
        self.assertEqual([tx], block.transactions)
        
    def test_givenSignature_whenUsingValidateSigFunction_thenReturnSignature(self):      
        wallet = Wallet()
        data = "test data"
        sig = wallet.sigSign(data.encode('utf-8'))
        self.assertTrue(wallet.validateSig(data, sig, wallet.pubKey))
        
    def test_givenInvalidSignature_whenUsingsigSignFunction_thenReturnFalse(self):      
        wallet = Wallet()
        data = "test data"
        data2 = "tets data"
        sig = wallet.sigSign(data.encode('utf-8'))
        with self.assertRaises(rsa.VerificationError) as context:
            wallet.validateSig(data2, sig, wallet.pubKey)
            
        self.assertTrue(type(context.exception) == rsa.VerificationError)

    def test_givenNewBalance_whenBalanceIs0_thenUpdateBalance(self):      
        wallet = Wallet()
        self.assertTrue(wallet.balance == 0)
        wallet.updateBalance(10)
        self.assertTrue(wallet.balance == 10)

    def test_givenNegativeBalance_whenBalanceIs0_thenUpdateBalanceToZero(self):      
        wallet = Wallet()
        wallet.balance = 10
        self.assertTrue(wallet.balance == 10)
        wallet.updateBalance(-20)
        self.assertTrue(wallet.balance == 10)

class TestValNode(unittest.TestCase):
    
    def test_givenNewAdminNode_whenInitialising_thenCreateAdminNode(self):      
        node = ValNode("localhost", 2, "admin", 20)
        self.assertEqual(node.nId, 20)
        self.assertEqual(node.ip, "localhost")
        self.assertEqual(node.port, 2)
        self.assertEqual(node.permissionLvl, "admin")
        self.assertEqual(node.knownAdmins, {})
        self.assertEqual(node.knownStudents, {})
        self.assertEqual(node.nodeBalances, {})
        self.assertEqual(node.nodeKeys, {node.wallet.pubKey: 20})
        self.assertEqual(node.recordIndex, {})
        self.assertEqual(node.invalidCreatorIDs, [])
        self.assertEqual(type(node.kms), KMS)
        self.assertEqual(type(node.bchain), Blockchain)
        self.assertEqual(type(node.wallet), Wallet)
        self.assertEqual(type(node.wallet.adminKey), KMS)
        self.assertEqual(type(node.consensus), PoS)
        self.assertEqual(node.wallet.balance, 50)
        self.assertEqual(node.consensus.getStake(node.wallet.pubKey), 50)
        
    def test_givenNewStudentNode_whenInitialising_thenCreateStudentNode(self):      
        node = ValNode("localhost", 2, "student", 20)
        self.assertEqual(node.nId, 20)
        self.assertEqual(node.ip, "localhost")
        self.assertEqual(node.port, 2)
        self.assertEqual(node.permissionLvl, "student")
        self.assertEqual(node.knownAdmins, {})
        self.assertEqual(node.knownStudents, {})
        self.assertEqual(node.nodeBalances, {})
        self.assertEqual(node.nodeKeys, {node.wallet.pubKey: 20})
        self.assertEqual(node.recordIndex, {})
        self.assertEqual(node.invalidCreatorIDs, [])
        self.assertEqual(node.kms, None)
        self.assertEqual(type(node.bchain), Blockchain)
        self.assertEqual(type(node.wallet), Wallet)
        self.assertEqual(node.wallet.adminKey, None)
        self.assertEqual(type(node.consensus), PoS)
        self.assertEqual(node.wallet.balance, 15)
        self.assertEqual(node.consensus.getStake(node.wallet.pubKey), 5)
        
    def test_givenCheckingIfNodeIsKnown_whenListIsEmpty_thenReturnTrue(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        msg = {'ip':"localhost", 'port':200, 'nId':100}
        self.assertTrue(node.searchNodes(node.knownAdmins, msg))
    
    def test_givenCheckingIfNodeIsKnown_whenAdminNodeIsKnown_thenReturnFalse(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        msg = {'ip':"localhost", 'port':200, 'nId':100}
        node.knownAdmins[200] = NodeInfo("localhost", 200, 100, "admin")
        self.assertFalse(node.searchNodes(node.knownAdmins, msg))
        
    def test_givenCheckingIfNodeIsKnown_whenNodeFindsItself_thenReturnFalse(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        msg = {'admins':[{'ip':"localhost", 'port':5001, 'nId':20}]}
        self.assertFalse(node.searchStoredNodes(node.knownAdmins, 'admins', msg))
    
    def test_givenCheckingIfNodeIsKnown_whenNodeIsKnown_thenReturnFalse(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node.knownAdmins[200] = NodeInfo("localhost", 201, 100, "admin")
        msg = {'admins':[{'ip':"localhost", 'port':5001, 'nId':220}]}
        self.assertFalse(node.searchStoredNodes(node.knownAdmins, 'admins', msg))
    
    def test_givenCheckingIfNodeIsKnown_whenNodeIsKnown_thenReturnFalse(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        msg = {'admins':[{'ip':"localhost", 'port':5002, 'nId':202}]}
        with self.assertRaises(AttributeError) as context:
            node.searchStoredNodes(node.knownAdmins, 'admins', msg)
            
        self.assertTrue(type(context.exception) == AttributeError)
    
    def test_givenNode_whenAddingNewNode_thenAddNode(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        msg = {'ip':"localhost", 'port':5002, 'nId':202, 'pmLvl':"admin", 'bal':100}
        node.addNewNode(node.knownAdmins, msg)
        self.assertTrue(202 in node.knownAdmins.keys())
        self.assertTrue(node.knownAdmins[202].ip == "localhost")
        self.assertTrue(node.knownAdmins[202].port == 5002)
        self.assertTrue(node.knownAdmins[202].nId == 202)
        self.assertTrue(node.knownAdmins[202].pmLvl == "admin")
        self.assertTrue(node.nodeBalances[202] == 100)
        
    def test_givenNode_whenAddingNewAdminNode_thenAddAdminNode(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        msg = {'ip':"localhost", 'port':5002, 'nId':202, 'pmLvl':"admin", 'bal':100, 'pubKeyN':1, 'pubKeyE':2, 'stake':1, 'blockchain':None, 'adminNodes':[], 'studentNodes':[]}
        node.newNode(msg)
        self.assertTrue(202 in node.knownAdmins.keys())    
        self.assertTrue(202 not in node.knownStudents.keys())  
        self.assertTrue(node.knownAdmins[202].ip == "localhost")
        self.assertTrue(node.knownAdmins[202].port == 5002)
        self.assertTrue(node.knownAdmins[202].nId == 202)
        self.assertTrue(node.knownAdmins[202].pmLvl == "admin")
        self.assertTrue(node.nodeBalances[202] == 100)  
        self.assertTrue(node.nodeKeys[rsa.PublicKey(1, 2)] == 202)
        self.assertTrue(node.consensus.getStake(rsa.PublicKey(1, 2)) == 1)
        
    def test_givenNode_whenAddingNewStuedntNode_thenAddStudentNode(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        msg = {'ip':"localhost", 'port':5002, 'nId':202, 'pmLvl':"student", 'bal':100, 'pubKeyN':1, 'pubKeyE':2, 'stake':1, 'blockchain':None, 'adminNodes':[], 'studentNodes':[]}
        node.newNode(msg)
        self.assertTrue(202 not in node.knownAdmins.keys())
        self.assertTrue(202 in node.knownStudents.keys())
        self.assertTrue(node.knownStudents[202].ip == "localhost")
        self.assertTrue(node.knownStudents[202].port == 5002)
        self.assertTrue(node.knownStudents[202].nId == 202)
        self.assertTrue(node.knownStudents[202].pmLvl == "student")
        self.assertTrue(node.nodeBalances[202] == 100)  
        self.assertTrue(node.nodeKeys[rsa.PublicKey(1, 2)] == 202)
        self.assertTrue(node.consensus.getStake(rsa.PublicKey(1, 2)) == 1)
        
    def test_givenMessage_whenMessageContainsTx_thenRecreateTX(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        msg = {'sendPKN':1, 'sendPKE':2, 'receiverPKN':3, 'receiverPKE':4, 'amount':10, 'type':"SENDTOKENS", 'data':None, 'tId':100, 'tTimestamp':20, 'tasCopy':'transaction','tSig':"Signature"}
        tx = node.recreateTx(msg)
        self.assertTrue(tx.senderPK == rsa.PublicKey(1,2))
        self.assertTrue(tx.receiverPK == rsa.PublicKey(3,4))
        self.assertTrue(tx.amount == 10)
        self.assertTrue(tx.type == "SENDTOKENS")
        self.assertTrue(tx.data == None)
        self.assertTrue(tx.tId == 100)
        self.assertTrue(tx.tTimestamp == 20)
        self.assertTrue(tx.tasOriginalCopy == "transaction")
        self.assertTrue(tx.tSig == "Signature")
        
    def test_givenMessage_whenMessageContainsBlock_thenRecreateBlock(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        txmsg = {'sendPKN':1, 'sendPKE':2, 'receiverPKN':3, 'receiverPKE':4, 'amount':10, 'type':"SENDTOKENS", 'data':None, 'tId':100, 'tTimestamp':20, 'tasCopy':'transaction','tSig':"Signature"}
        tx = node.recreateTx(txmsg)
        blockmsg = {'index':1, 'prevhash':"hash", 'validatorN':3, 'validatorE':4, 'timestamp':233, 'hash':"bhash", 'signature':"Signature"}
        block = node.recreateBlock(blockmsg, [tx])
        self.assertTrue(tx in block.transactions)
        self.assertTrue(block.index == 1)
        self.assertTrue(block.prevhash == "hash")
        self.assertTrue(block.validator == rsa.PublicKey(3,4))
        self.assertTrue(block.timestamp == 233)
        self.assertTrue(block.hash == "bhash")
        self.assertTrue(block.signature == "Signature")
        
    def test_givenMessage_whenMessageContainsGenesisBlock_thenRecreateGenesisBlock(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        blockmsg = {'index':0, 'prevhash':"hash", 'validatorN':"3", 'timestamp':233, 'hash':"bhash", 'signature':"Signature"}
        block = node.recreateBlock(blockmsg, [])
        self.assertTrue(len(block.transactions) == 0)
        self.assertTrue(block.index == 0)
        self.assertTrue(block.prevhash == "hash")
        self.assertTrue(block.validator == "3")
        self.assertTrue(block.timestamp == 233)
        self.assertTrue(block.hash == "bhash")
        self.assertTrue(block.signature == "Signature")
        
    def test_givenMessage_whenMessageContainsInvalidBlockCreator_thenPunishOffender(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        msg = {'id':200}
        testKey = rsa.PublicKey(3,4)
        node.nodeKeys[testKey] = 200
        node.consensus.addNode(testKey, 100)
        self.assertTrue(node.consensus.getStake(testKey) == 100)
        node.handleInvalidBlock(msg)
        self.assertTrue(node.consensus.getStake(testKey) == 0)
        self.assertTrue(200 in node.invalidCreatorIDs) 
    
    def test_givenNode_whenGettingBalance_thenReturnBalance(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node.wallet.balance = 200
        self.assertEqual(node.getBalance(), 200)
        
    def test_givenValidSendTransaction_whenCheckingIfTheTxCanBeExecuted_thenReturnTrue(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        node.nodeKeys[node2.wallet.pubKey] = 10
        node.wallet.balance = 200
        tx = Transaction(node.wallet.pubKey, node2.wallet.pubKey, 100, "SENDTOKENS")
        self.assertTrue(node.checkTxValid(tx))

    def test_givenInvalidSendTransaction_whenCheckingIfTheTxCanBeExecuted_thenReturnFalse(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        node.nodeKeys[node2.wallet.pubKey] = 10
        node.wallet.balance = 20
        tx = Transaction(node.wallet.pubKey, node2.wallet.pubKey, 100, "SENDTOKENS")
        self.assertFalse(node.checkTxValid(tx))
    
    def test_givenValidSubTransaction_whenCheckingIfTheTxCanBeExecuted_thenReturnTrue(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        node.nodeKeys[node2.wallet.pubKey] = 10
        node.wallet.balance = 200
        tx = Transaction(node.wallet.pubKey, node2.wallet.pubKey, 100, "SUBSTAKE")
        self.assertTrue(node.checkTxValid(tx))
        
    def test_givenInvalidSubTransaction_whenCheckingIfTheTxCanBeExecuted_thenReturnFalse(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        node.nodeKeys[node2.wallet.pubKey] = 10
        node.wallet.balance = 99
        tx = Transaction(node.wallet.pubKey, node2.wallet.pubKey, 100, "SUBSTAKE")
        self.assertFalse(node.checkTxValid(tx))   
        
    def test_givenNewStakeTransaction_whenTxIsValid_thenAddStake(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        node.nodeKeys[node2.wallet.pubKey] = 10
        node.nodeBalances[10] = 100
        tx = Transaction(node2.wallet.pubKey, node.wallet.pubKey, 5, "NEWSTAKE")
        node.handleTransaction(tx)
        self.assertEqual(node.consensus.getStake(node2.wallet.pubKey), 5)
        
    def test_givenAddStakeTransaction_whenTxIsValid_thenAddStake(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        tx = Transaction(node.wallet.pubKey, node2.wallet.pubKey, 5, "ADDSTAKE")
        node.handleTransaction(tx)
        self.assertEqual(node.consensus.getStake(node.wallet.pubKey), 55)
    
    
    def test_givenAddStakeTransaction_whenTxIsValidFromDifferentNode_thenAddStake(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        node.nodeKeys[node2.wallet.pubKey] = 10
        node.nodeBalances[10] = 100
        node.consensus.addNode(node2.wallet.pubKey, 1)
        tx = Transaction(node2.wallet.pubKey, node.wallet.pubKey, 5, "ADDSTAKE")
        node.handleTransaction(tx)
        self.assertEqual(node.nodeBalances[10], 95)
        self.assertEqual(node.consensus.nodes[node2.wallet.pubKey.n + node2.wallet.pubKey.e], 6)
    
    def test_givenSubStakeTransaction_whenTxIsValid_thenSubStake(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        tx = Transaction(node.wallet.pubKey, node2.wallet.pubKey, 5, "SUBSTAKE")
        node.handleTransaction(tx)
        self.assertEqual(node.consensus.getStake(node.wallet.pubKey), 45)
    
    def test_givenSubStakeTransaction_whenTxIsValidFromDifferentNode_thenSubStake(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        node.nodeKeys[node2.wallet.pubKey] = 10
        node.nodeBalances[10] = 100
        node.consensus.addNode(node2.wallet.pubKey, 10)
        tx = Transaction(node2.wallet.pubKey, node.wallet.pubKey, 5, "SUBSTAKE")
        node.handleTransaction(tx)
        self.assertEqual(node.consensus.getStake(node2.wallet.pubKey), 5)
    
    def test_givenSendTransaction_whenTxIsValidFromDifferentNode_thenAddToLocalBalanceSubFromNodes(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        node.nodeKeys[node2.wallet.pubKey] = 10
        node.nodeBalances[10] = 100
        tx = Transaction(node2.wallet.pubKey, node.wallet.pubKey, 5, "SENDTOKENS")
        node.handleTransaction(tx)
        self.assertEqual(node.nodeBalances[10], 95)
        self.assertEqual(node.wallet.balance, 55)
        
    def test_givenSendTransaction_whenTxIsValidToDifferentNode_thenAddToNodeBalanceSubFromLocal(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "admin", 10)
        node.nodeKeys[node2.wallet.pubKey] = 10
        node.nodeBalances[10] = 100
        tx = Transaction(node.wallet.pubKey, node2.wallet.pubKey, 5, "SENDTOKENS")
        node.handleTransaction(tx)
        self.assertEqual(node.nodeBalances[10], 105)
        self.assertEqual(node.wallet.balance, 45)
        
    def test_givenBlockchain_whenBlockchainIsValid_thenReturnTrue(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey1)
        node.bchain.chain.append(block)
        block2 = Block([tx, tx2], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block2)
        self.assertTrue(node.validateChain())
        
    def test_givenBlockchain_whenBlockchainIsInvalid_thenReturnFalse(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey1)
        node.bchain.chain.append(block)
        block2 = Block([tx, tx2], node.bchain.chainLength(), node.bchain.genesisBlock().hash, pubKey2)
        node.bchain.chain.append(block2)
        with self.assertRaises(AttributeError) as context:
            self.assertFalse(node.validateChain())
            
        self.assertTrue(type(context.exception) == AttributeError)
    
    def test_givenNewBlockchain_whenBlockchainIsValid_thenReturnTrue(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        newchain = [Block.genesisBlock()]
        block = Block([tx], len(newchain), Block.genesisBlock().hash, pubKey1)
        newchain.append(block)
        block2 = Block([tx, tx2], len(newchain), block.hash, pubKey2)
        newchain.append(block2)
        self.assertTrue(node.validateNewChain(newchain))
        
    def test_givenNewBlockchain_whenBlockchainIsInvalid_thenReturnFalse(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        newchain = [Block.genesisBlock()]
        block = Block([tx], len(newchain), Block.genesisBlock().hash, pubKey1)
        newchain.append(block)
        block2 = Block([tx, tx2], len(newchain), Block.genesisBlock().hash, pubKey2)
        newchain.append(block2)
        self.assertFalse(node.validateNewChain(newchain))
        
    def test_givenNewBlockchain_whenBlockchainIsValid_thenUpdateToChain(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        newchain = [Block.genesisBlock()]
        block = Block([tx], len(newchain), Block.genesisBlock().hash, pubKey1)
        newchain.append(block)
        block2 = Block([tx, tx2], len(newchain), block.hash, pubKey2)
        newchain.append(block2)
        node.updateToValidChain(newchain)
        self.assertEqual(node.bchain.chain, newchain)
        
    def test_givenNewBlockchain_whenBlockchainIsInvalid_thenDontUpdateToChain(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        newchain = [Block.genesisBlock()]
        block = Block([tx], len(newchain), Block.genesisBlock().hash, pubKey1)
        newchain.append(block)
        block2 = Block([tx, tx2], len(newchain), Block.genesisBlock(), pubKey2)
        newchain.append(block2)
        node.updateToValidChain(newchain)
        self.assertNotEqual(node.bchain.chain, newchain)
        
    def test_givenNewBlockchain_whenBlockchainIsValidButShorter_thenDontUpdateToChain(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        block = Block([tx], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey1)
        node.bchain.chain.append(block)
        block2 = Block([tx, tx2], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block2)
        block3 = Block([tx], 1, Block.genesisBlock().hash, pubKey2)
        newchain = [Block.genesisBlock(), block3]
        self.assertNotEqual(node.bchain.chain, newchain)
        
    def test_givenNewValidator_whenValidatorIsValid_thenReturnTrue(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "student", 210)
        node.consensus.addNode(node2.wallet.pubKey, 10)
        validator = node.wallet.pubKey
        self.assertTrue(node.validatorValid(validator))
        
    def test_givenNewValidator_whenValidatorIsInvalid_thenReturnFalse(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        node2 = ValNode("localhost", 5002, "student", 210)
        node.consensus.addNode(node2.wallet.pubKey, 10)
        validator = node2.wallet.pubKey
        self.assertFalse(node.validatorValid(validator))
        
    def test_givenRecordRequestAsAdminNode_whenRequestIsValidAndIDInIndex_thenReturnRecord(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        sd = StudentData("Cameron", "McGreevy", "19", {"Test":100})
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "0", "NEWRECORD", sd)
        tx3 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        data = tx2.data.toDict()
        encdata = node.kms.encrypt(data) 
        tx2.data = encdata.decode('latin-1')
        tx2.encrypted = True
        block = Block([tx], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey1)
        node.bchain.chain.append(block)
        block2 = Block([tx2], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block2)
        block3 = Block([tx3], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block3)
        node.recordIndex["19"] = 2
        record = node.recordSearch(node.bchain.chain, "19")
        self.assertEqual(record['sId'], "19")
        
    def test_givenRecordRequestAsAdminNode_whenRequestIsValidAndNotIndexed_thenReturnRecord(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        sd = StudentData("Cameron", "McGreevy", "19", {"Test":100})
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "0", "NEWRECORD", sd)
        tx3 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        data = tx2.data.toDict()
        encdata = node.kms.encrypt(data) 
        tx2.data = encdata.decode('latin-1')
        tx2.encrypted = True
        block = Block([tx], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey1)
        node.bchain.chain.append(block)
        block2 = Block([tx2], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block2)
        block3 = Block([tx3], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block3)
        record = node.recordSearch(node.bchain.chain, "19")
        self.assertEqual(record['sId'], "19")
        
    def test_givenRecordRequestAsAdminNode_whenRequestIsInvalidAndNotIndexed_thenReturnNone(self):      
        node = ValNode("localhost", 5001, "admin", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        sd = StudentData("Cameron", "McGreevy", "21", {"Test":100})
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "0", "NEWRECORD", sd)
        tx3 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        data = tx2.data.toDict()
        encdata = node.kms.encrypt(data) 
        tx2.data = encdata.decode('latin-1')
        tx2.encrypted = True
        block = Block([tx], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey1)
        node.bchain.chain.append(block)
        block2 = Block([tx2], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block2)
        block3 = Block([tx3], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block3)
        record = node.recordSearch(node.bchain.chain, "19")
        self.assertEqual(record, None)
        
    def test_givenRecordRequestAsStudentNode_whenRequestIsValidAndIndexed_thenReturnEncryptedData(self):      
        node = ValNode("localhost", 5001, "student", 20)
        pubKey1 = rsa.PublicKey(1, 2)
        pubKey2 = rsa.PublicKey(3, 4)
        sd = StudentData("Cameron", "McGreevy", "19", {"Test":100})
        tx = Transaction(pubKey1, pubKey2, "100", "SENDTOKENS")
        tx2 = Transaction(pubKey2, pubKey1, "0", "NEWRECORD", sd)
        tx3 = Transaction(pubKey2, pubKey1, "50", "ADDSTAKE")
        data = tx2.data.toDict()
        kms = KMS()
        encdata = kms.encrypt(data) 
        tx2.data = encdata.decode('latin-1')
        tx2.encrypted = True
        block = Block([tx], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey1)
        node.bchain.chain.append(block)
        block2 = Block([tx2], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block2)
        block3 = Block([tx3], node.bchain.chainLength(), node.bchain.lastBlock().hash, pubKey2)
        node.bchain.chain.append(block3)
        record = node.recordSearch(node.bchain.chain, "19")
        self.assertNotEqual(record, None)
        self.assertEqual(record, False)
        
if __name__ == '__main__':
    unittest.main()