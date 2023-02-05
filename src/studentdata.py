import json


class StudentData:
    def __init__(self, sForename, sSurname, sModules, sGrades):
        self.sForename = sForename
        self.sSurname = sSurname
        self.sModules = sModules
        self.sGrades = sGrades
        
    def toJson(self):
         return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
            