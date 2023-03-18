import json

# Class for encapsulating node details to be held in a dictionary
class NodeInfo:
    def __init__(self, ip, port, nId, pmLvl):
        self.ip = ip
        self.port = port
        self.nId = nId
        self.pmLvl = pmLvl
    
    # JSON representation of each node    
    def toJson(self):
        jsonRep = {}
        jsonRep['ip'] = self.ip
        jsonRep['port'] = self.port
        jsonRep['nId'] = self.nId
        jsonRep['pmLvl'] = self.pmLvl
        return jsonRep