from service.globalDatabaseAccess import GlobalDatabaseAccess
from executeProjectCreationControl import ExecuteProjectCreationControl
from datetime import datetime


class UpdateProjectControl:
    def __init__(self, project_id):
        self.project_id = project_id
        self.globalDatabaseAccess = GlobalDatabaseAccess()

    def updateProject(self):
        try:
            # get project database environment
            projectDatabaseURL = self.getProjectDatabaseURL()
            projectDatabaseUsername = self.getProjectDatabaseUsername()
            projectDatabasePassword = self.getProjectDatabasePassword()
            projectLastTrace = self.getProjectLastTrace()
            newprojectLastTrace = self.getProjectLastTrace()

            # get project git environment
            projectGitURL = self.getProjectGitURL()
            print("Step 1: connected to global database to get credentials and link to git repository")

            # manage all operations to create project in one object
            executeProjectCreation = ExecuteProjectCreationControl(projectDatabaseURL, projectDatabaseUsername,
                                                                   projectDatabasePassword)

            # +++++++++++ download and analyse Github project +++++++++++++++
            # download source and save locally
            executeProjectCreation.getSourceCode(projectGitURL)
            print("Step 2: cloned git repository to temporary local folder")
            # extract project data from cloned repo into csv file "rawrepdatacsv.csv"
            # check if .class files are there (necessary for dependency analysis)
            executeProjectCreation.extractProjectData(projectGitURL)
            print("Step 3: extracted project data from cloned repo into csv file 'rawrepdatacsv.csv'")
            # extract dependency data from cloned repo into csv file "dependencymatrix.csv"
            executeProjectCreation.analyseDependencies()
            print("Step 4: extracted dependencies from cloned repo into csv file 'dependencymatrix.csv'")

            # +++++++++++ update data in project database +++++++++++++++
            # persist projectdata in projectdatabase
            newprojectLastTrace = executeProjectCreation.updateProjectFiles(projectLastTrace)
            if newprojectLastTrace != 0:
                self.updateLastTrace(newprojectLastTrace)
            print("Step 5: updated file data in project database")
            # persist new dependencies
            executeProjectCreation.updateProjectDependencies()
            print("Step 6: updated dependencies in project database")
            # clean up local project data
            executeProjectCreation.deleteLocalProjectFolder()
            print("Step 7: cleaned up temporary local project data")
        except(Exception) as error:
            print(error)
        finally:
            # close global database connection
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

    def getProjectLastTrace(self):
        query = "SELECT PROJECT_LASTTRACE FROM PROJECT WHERE PROJECT_ID = {}".format(self.project_id)
        date = self.globalDatabaseAccess.executeQuery(query)
        return date

    def updateLastTrace(self, newprojectLastTrace):
        query = "UPDATE PROJECT SET PROJECT_LASTTRACE = '" + newprojectLastTrace + "' WHERE PROJECT_ID = {}".format(
            self.project_id)
        self.globalDatabaseAccess.executeUpdateQuery(query)
