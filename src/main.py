from hashlib import sha256
from transaction import Transaction
from wallet import Wallet
from txpool import TxPool
from block import Block
from blockchain import Blockchain
from pos import PoS
from valnode import ValNode
import sys, rsa

if __name__ == '__main__':
    ip = sys.argv[1]
    port = int(sys.argv[2])
    pmLvl = sys.argv[3]
    id = int(sys.argv[4])
    node = ValNode(ip, port, pmLvl, id)
    """ w = Wallet()
    w2 = Wallet()
    p = TxPool()
    bl = Blockchain()
    bl.updateNodeBalance(w.pubKey, 100)
    bl.updateNodeBalance(w2.pubKey, 100)
    t = w.createTransaction(w2.pubKey, 2, "SEND")
    if (p.notInPool(t)):
        p.addTxToPool(t)
    
    h = sha256(bl.lastBlock().basOriginalCopy.encode("utf-8")).hexdigest()
    bc = bl.lastBlock().index + 1
    x = p.txs
    b = w.createBlock(x, bc, h, w.pubKey)
    if (bl.validateNewBlock(bl.lastBlock(), b)):
        bl.testAdd(b)
    p.updatePool(bl.lastBlock().transactions)
    
    t2 = w.createTransaction(w2.pubKey, 5, "SEND")
    if (p.notInPool(t2)):
        p.addTxToPool(t2)
    h2 = sha256(bl.lastBlock().basOriginalCopy.encode("utf-8")).hexdigest()
    bc2 = bl.lastBlock().index + 1
    b2 = w2.createBlock(p.txs, bc2, h2, w2.pubKey)
    if (bl.validateNewBlock(bl.lastBlock(), b2)):
        bl.testAdd(b2)
    p.updatePool(bl.lastBlock().transactions)
    
    w.balance = 5
    w2.balance = 5
    pos = PoS(w.pubKey, w.balance)
    pos.addNode(w2.pubKey, w2.balance)
    wcount = 0
    w2count = 0
    for i in range(10):
        forger = pos.generateValidator(bl.lastBlock().hash)
        if (forger == (w.pubKey.e + w.pubKey.n)):
            wcount += 1
        elif (forger == (w2.pubKey.e + w2.pubKey.n)):
            w2count += 1
    print("W", wcount)
    print("W2", w2count) """
    node.startFunctions()