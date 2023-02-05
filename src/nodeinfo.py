class NodeInfo:
    def __init__(self, ip, port, id, pmLvl):
        self.ip = ip
        self.port = port
        self.id = id
        self.pmLvl = pmLvl
        
    def toJson(self):
         return json.dumps(self, indent = 4, default=lambda o: o.__dict__)