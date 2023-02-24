import json


class NodeInfo:
    def __init__(self, ip, port, id, pmLvl):
        self.ip = ip
        self.port = port
        self.id = id
        self.pmLvl = pmLvl
        
    def toJson(self):
        jsonRep = {}
        jsonRep['ip'] = self.ip
        jsonRep['port'] = self.port
        jsonRep['id'] = self.id
        jsonRep['pmLvl'] = self.pmLvl
        jsonRep = json.dumps(jsonRep)
        jsonRep = jsonRep.encode('utf-8')
        return jsonRep