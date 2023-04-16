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
    gui = sys.argv[4]
    if gui == "cmd" or gui == "CMD":  
        node = ValNode(ip, port, pmLvl, id)
        node.cmd = True
        node.startFunctions()
    else:
        root = tkinter.Tk()
        root.title("QUBerium")
        node = GUI(ip, port, pmLvl, id, master=root)
        node.mainloop()
    