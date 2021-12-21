from service.globalDatabaseAccess import GlobalDatabaseAccess
from executeProjectCreationControl import ExecuteProjectCreationControl


class CreateProjectControl:
    def __init__(self, project_id):
        self.project_id = project_id
        self.globalDatabaseAccess = GlobalDatabaseAccess()

    def createProject(self):
        try:
            print("start")
            projectDatabaseURL = self.getProjectDatabaseURL()
            projectDatabaseUsername = self.getProjectDatabaseUsername()
            projectDatabasePassword = self.getProjectDatabasePassword()
            #projectLastHash = self.getProjectLastHash()

            # +++++++++++ preparations +++++++++++++++
            projectGitURL = self.getProjectGitURL()
            print("Step 0: connected to global database to get credentials and link to git repository")
            # manage all operations to create project
            executeProjectCreation = ExecuteProjectCreationControl(projectDatabaseURL, projectDatabaseUsername,
                                                                   projectDatabasePassword)
            # clean project database
            executeProjectCreation.deleteDataFromProjectDatabase()
            print("Step 1: cleaned project database")
            # download source and save locally

            # +++++++++++ download and analyse Github project +++++++++++++++
            executeProjectCreation.getSourceCode(projectGitURL)
            print("Step 2: cloned git repository to temporary local folder")
            # extract project data from cloned repo into csv file "rawrepdatacsv.csv"
            # check if .class files are there (necessary for dependency analysis)
            executeProjectCreation.extractProjectData(projectGitURL)
            print("Step 3: extracted project data from cloned repo into csv file 'rawrepdatacsv.csv'")
            # extract dependency data from cloned repo into csv file "dependencymatrix.csv"
            executeProjectCreation.analyseDependencies()
            print("Step 4: extracted dependencies from cloned repo into csv file 'dependencymatrix.csv'")

            # +++++++++++ import data in project database +++++++++++++++
            # persist projectdata in projectdatabase
            projectLastTrace = executeProjectCreation.persistProjectData()
            self.updateLastTrace(projectLastTrace)
            print("Step 5: persisted project data in project database")
            # persist pattern data in projectdatabase
            # executeProjectCreation.persistPatternData()
            print("Step 6: persisted pattern data in project database")
            executeProjectCreation.deleteLocalProjectFolder()
            print("Step 7: cleaned up temporary local project data")
        except(Exception) as error:
            print(error)
        finally:
            self.globalDatabaseAccess.close()

    def getProjectGitURL(self):
        query = "SELECT PROJECT_GITURL FROM PROJECT WHERE PROJECT_ID = {}".format(self.project_id)
        return self.globalDatabaseAccess.executeQuery(query)

    def getProjectDatabaseURL(self):
        query = "SELECT PROJECTDATABASE_URL FROM PROJECTDATABASE WHERE PROJECT_ID = {};".format(self.project_id)
        return self.globalDatabaseAccess.executeQuery(query)

    def getProjectDatabaseUsername(self):
        query = "SELECT PROJECTDATABASE_USER FROM PROJECTDATABASE WHERE PROJECT_ID = {};".format(self.project_id)
        return self.globalDatabaseAccess.executeQuery(query)

    def getProjectDatabasePassword(self):
        query = "SELECT PROJECTDATABASE_PASSWORD FROM PROJECTDATABASE WHERE PROJECT_ID = {};".format(self.project_id)
        return self.globalDatabaseAccess.executeQuery(query)

    def getProjectLastHash(self):
        query = "SELECT PROJECT_LASTHASH FROM PROJECT WHERE PROJECT_ID = {}".format(self.project_id)
        return self.globalDatabaseAccess.executeQuery(query)

    def updateLastTrace(self, newprojectLastTrace):
        query = "UPDATE PROJECT SET PROJECT_LASTTRACE = '" + newprojectLastTrace + "' WHERE PROJECT_ID = {}".format(
            self.project_id)
        self.globalDatabaseAccess.executeUpdateQuery(query)
