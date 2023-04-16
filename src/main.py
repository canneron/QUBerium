from hashlib import sha256
import tkinter
from gui import GUI
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
    gui = sys.argv[5]
    if gui == "cmd":
        node = ValNode(ip, port, pmLvl, id)
        node.cmd = True
        node.startFunctions()
    else:
        tk = tkinter.Tk()
        GUI(ip, port, pmLvl, id, tk)
        tk.mainloop()