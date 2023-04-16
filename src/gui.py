from functools import partial
import json
import textwrap
import threading
import time
import tkinter
from studentdata import StudentData 
from valnode import ValNode

class GUI(tkinter.Frame):
    def __init__(self, ip, port, pmLvl, id, master=None):
        super().__init__(master)
        self.node = ValNode(ip, port, pmLvl, id)
        threading.Thread(target=self.node.startFunctions()).start()
        self.master = master
        self.pack()
        self.menu()
        self.amount = tkinter.StringVar()
        self.receiver = tkinter.StringVar()
        self.forename = tkinter.StringVar()
        self.surname = tkinter.StringVar()
        self.sId = tkinter.StringVar()
        self.modules = []
        self.grades = []
        self.modgrades = {}


    def menu(self):
        button_style = {
            "font": ("Arial", 14),
            "width": 30,
            "height": 5,
            "bd": 3,
            "relief": "raised",
            "bg": "white",
            "activebackground": "white"
        }

        row1 = tkinter.Frame(self, bg="red")
        row2 = tkinter.Frame(self, bg="red")
        row3 = tkinter.Frame(self, bg="red")
        row4 = tkinter.Frame(self)

        blockchainButton = tkinter.Button(row1, text="Blockchain", command=self.displayChain, **button_style)
        blockchainButton.pack(side="left", padx=10, pady=10)
        
        txPoolButton = tkinter.Button(row1, text="Staking Pool", command=self.displayStakingPool, **button_style)
        txPoolButton.pack(side="left", padx=10, pady=10)
        
        balanceButton = tkinter.Button(row1, text="Balance", command=self.displayBalances, **button_style)
        balanceButton.pack(side="left", padx=10, pady=10)

        sendTokensButton = tkinter.Button(row2, text="Send Tokens", command=self.sendTokens, **button_style)
        sendTokensButton.pack(side="left", padx=10, pady=10)

        createRecordButton = tkinter.Button(row2, text="Create Record", command=self.createRecord, **button_style)
        createRecordButton.pack(side="left", padx=10, pady=10)

        searchButton = tkinter.Button(row2, text="Search", command=self.search, **button_style)
        searchButton.pack(side="left", padx=10, pady=10)

        myRecordsButton = tkinter.Button(row3, text="My Records", command=self.myRecords, **button_style)
        myRecordsButton.pack(side="left", padx=10, pady=10)

        connectionsButton = tkinter.Button(row3, text="Connections", command=self.connections, **button_style)
        connectionsButton.pack(side="left", padx=10, pady=10)

        resendBroadcastButton = tkinter.Button(row3, text="Resend Broadcast", command=self.resendBroadcast, **button_style)
        resendBroadcastButton.pack(side="left", padx=10, pady=10)

        quitButton = tkinter.Button(row4, text="Quit", command=self.quitApp, **button_style)
        quitButton.pack(side="left", padx = 20, pady=20)

        accountButton = tkinter.Button(row4, text=str(self.node.nId), command=self.displayAccount, **button_style)
        accountButton.pack(side="right", padx = 20, pady=20)
        
        row1.pack()
        row2.pack()
        row3.pack()
        row4.pack()
        
    def returnToMenu(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        self.menu()
        
    def quitApp(self):
        self.node.stopNode()
        self.master.destroy()
        
    def displayAccount(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        string = "Network: " + str(self.node.host) + "\nPort: " + str(self.node.port) + "\nID: " + str(self.node.nId) + "\nAccess: " + self.node.permissionLvl
        label = tkinter.Label(self, text=string, relief=tkinter.RAISED)
        label.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()
        
    def displayChain(self):
        button_style = {
            "font": ("Arial", 14),
            "width": 15,
            "height": 3,
            "bd": 3,
            "relief": "raised",
            "bg": "white",
            "activebackground": "white"
        }
        for widgets in self.winfo_children():
            widgets.destroy()
        row = tkinter.Frame(self)
        for block in self.node.bchain.chain:
            btn = tkinter.Button(self, text="Block " + str(block.index), command=partial(self.displayBlock, block.index), **button_style)
            btn.pack(side="top", padx=10, pady=10)
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()
        
    def displayBlock(self, index):
        for widgets in self.winfo_children():
            widgets.destroy()
        block = self.node.bchain.getBlock(index)
        x = block.toJson()
        string = json.loads(x)
        string = json.dumps(string, indent=4)
        string = textwrap.fill(string, width = 200)
        label = tkinter.Label(self, text=string, relief=tkinter.RAISED)
        label.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.displayChain)
        returnButton.pack()
            
    def displayStakingPool(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        label = tkinter.Label(self, text="Balances", relief=tkinter.RAISED)
        label.pack()
        for node in self.node.consensus.nodes:
            for pk in self.node.nodeKeys:
                if node == pk.e + pk.n:  
                    string = str(self.node.nodeKeys[pk]) + ": " + str(self.node.consensus.nodes[node])
                    label = tkinter.Label(self, text=string, relief=tkinter.RAISED)
                    label.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()
            
    def displayBalances(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        yourbalance = "Your balance: " + str(self.node.wallet.balance)
        label = tkinter.Label(self, text=yourbalance, relief=tkinter.RAISED)
        label.pack()
        for id in self.node.nodeBalances:
            balance = str(id) + " : " + str(self.node.nodeBalances[id])
            nlabel = tkinter.Label(self, text=balance, relief=tkinter.RAISED)
            nlabel.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()
            
    def sendTokens(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        text1 = "Enter Amount To Send"
        text2 = "Enter ID of receiver"
        label = tkinter.Label(self, text=text1, relief=tkinter.RAISED)
        amount = tkinter.Entry(self, textvariable=self.amount, relief=tkinter.SUNKEN)
        label2 = tkinter.Label(self, text=text2, relief=tkinter.RAISED)
        receiver = tkinter.Entry(self, textvariable=self.receiver, relief=tkinter.SUNKEN)
        send = tkinter.Button(self, text="Send", command=lambda: self.verifyTx(self.amount.get(), self.receiver.get()))
        label.pack()
        amount.pack()
        label2.pack()
        receiver.pack()
        send.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()
        
    def verifyTx(self, amount, receiver):
        for key in self.node.nodeKeys:
            if receiver == str(self.node.nodeKeys[key]):
                # Create transaction and send it to other nodes
                t = self.node.wallet.createTransaction(key, int(amount), "SENDTOKENS")
                self.node.incomingTransaction(t, t.tSig)
                msgJson = t.toJson()
                self.node.send_to_nodes(msgJson)
                for widgets in self.winfo_children():
                    widgets.destroy()
                label = tkinter.Label(self, text="Transaction Sent!", relief=tkinter.RAISED)
                label.pack()
                self.amount.set("")
                self.receiver.set("")
                returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
                returnButton.pack()
                break
        
    def createRecord(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        if self.node.permissionLvl == "admin":
            text1 = "Forename"
            text2 = "Surname"
            text3 = "ID"
            text4 = "Module Code"
            text5 = "Grade"
            label = tkinter.Label(self, text=text1, relief=tkinter.RAISED)
            name = tkinter.Entry(self, textvariable=self.forename, relief=tkinter.SUNKEN)
            label2 = tkinter.Label(self, text=text2, relief=tkinter.RAISED)
            surname = tkinter.Entry(self, textvariable=self.surname, relief=tkinter.SUNKEN)
            label3 = tkinter.Label(self, text=text3, relief=tkinter.RAISED)
            sId = tkinter.Entry(self, textvariable=self.sId, relief=tkinter.SUNKEN)
            self.modules.append(tkinter.StringVar())
            self.grades.append(tkinter.StringVar())
            label4 = tkinter.Label(self, text=text4, relief=tkinter.RAISED)
            modCode = tkinter.Entry(self, textvariable=self.modules[len(self.modules) - 1], relief=tkinter.SUNKEN)
            label5 = tkinter.Label(self, text=text5, relief=tkinter.RAISED)
            grade = tkinter.Entry(self, textvariable=self.grades[len(self.grades) - 1], relief=tkinter.SUNKEN)
            returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
            add = tkinter.Button(self, text="+", command=lambda: self.addBox(send, add, returnButton))
            send = tkinter.Button(self, text="Send", command=self.createNewRecord)
            label.pack()
            name.pack()
            label2.pack()
            surname.pack()
            label3.pack()
            sId.pack()
            label4.pack()
            modCode.pack()
            label5.pack()
            grade.pack()
            add.pack()
            send.pack()
        else:
            label = tkinter.Label(self, text="Insufficient privilege", relief=tkinter.RAISED)
            label.pack()
        
        returnButton.pack()
            
    def addBox(self, send, add, returnButton):
        self.modules.append(tkinter.StringVar())
        self.grades.append(tkinter.StringVar())
        label4 = tkinter.Label(self, text="Module Code", relief=tkinter.RAISED)
        modCode = tkinter.Entry(self, textvariable=self.modules[len(self.modules) - 1], relief=tkinter.SUNKEN)
        label5 = tkinter.Label(self, text="Grade", relief=tkinter.RAISED)
        grade = tkinter.Entry(self, textvariable=self.grades[len(self.grades) - 1], relief=tkinter.SUNKEN)
        send.pack_forget()
        add.pack_forget()
        returnButton.pack_forget()
        label4.pack()
        modCode.pack()
        label5.pack()
        grade.pack()
        add.pack()
        send.pack()
        returnButton.pack()
        
    def createNewRecord(self):
        for x in range(0,len(self.modules)):
            self.modgrades[self.modules[x].get()] = self.grades[x].get()
        sd = StudentData(self.forename.get(), self.surname.get(), self.sId.get(), self.modgrades)
        self.node.createNewRecord(sd)
        self.forename.set("")
        self.surname.set("")
        self.sId.set("")
        self.modules.clear()
        self.grades.clear()
        self.modgrades.clear()
        for widgets in self.winfo_children():
            widgets.destroy()
        self.createRecord()
            
    def search(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        if self.node.permissionLvl == "admin":
            text1 = "Enter Student's ID"
            label = tkinter.Label(self, text=text1, relief=tkinter.RAISED)
            id = tkinter.Entry(self, textvariable=self.sId, relief=tkinter.SUNKEN)
            send = tkinter.Button(self, text="Send", command=lambda: self.searchStudent(self.sId.get()))
            label.pack()
            id.pack()
            send.pack()
        else:
            label = tkinter.Label(self, text="Insufficient privilege", relief=tkinter.RAISED)
            label.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()
        
    def searchStudent(self, id):
        for widgets in self.winfo_children():
            widgets.destroy()
        record = self.node.recordSearch(self.node.bchain.chain, id)
        if record == None:
            label = tkinter.Label(self, text="Student Record Not Found", relief=tkinter.RAISED)
            label.pack()
        else:
            string = "Forename: " + record['sForename'] + "\nSurname: " + record['sSurname'] + "\nID: " + record['sId'] + "\n------------\nModule Grades\n------------"
            for grade in record['sGrades']:
                string += "\n" + str(grade) + ": " + str(record['sGrades'][grade])
            label = tkinter.Label(self, text=string, relief=tkinter.RAISED)
            label.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()
        
    def myRecords(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        if self.node.permissionLvl == "student":
            label = tkinter.Label(self, text="Retrieving...", relief=tkinter.RAISED)
            label.pack()
            self.node.requestRecords()
            while self.node.reply == False:
                continue
            record = self.node.getStudentRecord()
            for widgets in self.winfo_children():
                widgets.destroy()
            if record == None:
                label = tkinter.Label(self, text="Records not found - please contact administrator", relief=tkinter.RAISED)
                label.pack()
            else:
                string = "Forename: " + record['sForename'] + "\nSurname: " + record['sSurname'] + "\nID: " + record['sId'] + "\n------------\nModule Grades\n------------"
                for grade in record['sGrades']:
                    string += "\n" + str(grade) + ": " + str(record['sGrades'][grade])
                label = tkinter.Label(self, text=string, relief=tkinter.RAISED)
                label.pack()
            self.node.reply = False
                
        else:
            label = tkinter.Label(self, text="Please use search function to find student records", relief=tkinter.RAISED)
            label.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()
            
    def connections(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        admin = "**** ADMINS ****"
        label = tkinter.Label(self, text=admin, relief=tkinter.RAISED)
        label.pack()
        for peer in self.node.knownAdmins:
            admins = str(self.node.knownAdmins[peer].ip) + ":" + str(self.node.knownAdmins[peer].port) + " (" + str(self.node.knownAdmins[peer].nId) + ")"
            nlabel = tkinter.Label(self, text=admins, relief=tkinter.RAISED)
            nlabel.pack()
        student = "**** STUDENTS ****"
        label = tkinter.Label(self, text=student, relief=tkinter.RAISED)
        label.pack()
        for peer in self.node.knownStudents:
            students = str(self.node.knownStudents[peer].ip) + ":" + str(self.node.knownStudents[peer].port) + " (" + str(self.node.knownStudents[peer].nId) + ")"
            nlabel = tkinter.Label(self, text=students, relief=tkinter.RAISED)
            nlabel.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()
        
    def resendBroadcast(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        enterPort = "Enter Port"
        portVar = tkinter.StringVar()
        label = tkinter.Label(self, text=enterPort, relief=tkinter.RAISED)
        port = tkinter.Entry(self, textvariable=portVar, relief=tkinter.SUNKEN)
        send = tkinter.Button(self, text="Send", command=self.sendTokens)
        label.pack()
        port.pack()
        send.pack()
        returnButton = tkinter.Button(self, text="Return To Menu", command=self.returnToMenu)
        returnButton.pack()