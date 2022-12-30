class StudentData:
    def __init__(self, sForename, sSurname, sModules, sGrades):
        self.sForename = sForename
        self.sSurname = sSurname
        self.storedData = {}
        self.sModules = sModules
        self.sGrades = sGrades
        
    def readGrades(self):
        student = "Results for {0} {1}"
        print(student.format(self.sForename, self.sSurname))
        for m, g in zip(self.sModules, self.sGrades):
            modgrade = "Module: {0} - Grade: {1}"
            print(modgrade.format(m, g))
            