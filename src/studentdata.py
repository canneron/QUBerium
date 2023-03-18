import json

# Class for encapsulating student data
class StudentData:
    def __init__(self, sForename, sSurname, sId, sModuleGrades):
        self.sForename = sForename
        self.sSurname = sSurname
        self.sId = sId
        self.sGrades = sModuleGrades
        
    # Dictionary representation of each student
    def toDict(self):
        jsonRep = {}
        jsonRep['sForename'] = self.sForename
        jsonRep['sSurname'] = self.sSurname
        jsonRep['sId'] = self.sId
        jsonRep['sGrades'] = self.sGrades
        return jsonRep
            