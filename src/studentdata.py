import json


class StudentData:
    def __init__(self, sForename, sSurname, sId, sModules, sGrades):
        self.sForename = sForename
        self.sSurname = sSurname
        self.sId = sId
        self.sModules = sModules
        self.sGrades = sGrades
        
    def toDict(self):
        jsonRep = {}
        jsonRep['sForename'] = self.sForename
        jsonRep['sSurname'] = self.sSurname
        jsonRep['sId'] = self.sId
        jsonRep['sModules'] = self.sModules
        jsonRep['sGrades'] = self.sGrades
        return jsonRep
            