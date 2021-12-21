from service.DatabaseAccess import DatabaseAccess
from model.ProduceQueries import ProduceQueries


class ManagePersistence:
    def __init__(self):
        self.produceQueries = ProduceQueries()

    def init_connection(self, uri, userName, password):
        self.projectDatabaseAccess = DatabaseAccess(uri, userName, password)

    def process_dependency_persisting(self, pathToDependencymatrix):
        # produce a project database query for each dependency and save in array "queries"
        queries = self.produceQueries.create_dependencies_queries(pathToDependencymatrix)
        # iterate through query array
        for i in range(len(queries)):
            # execute query at i
            self.projectDatabaseAccess.executequery(queries[i])

    def process_patterns_persisting(self):
        # produce a project database query for each pattern and save in array "queries"
        queries = self.produceQueries.create_patterns_queries()
        # iterate through query array
        for i in range(len(queries)):
            # execute query at i
            self.projectDatabaseAccess.executequery(queries[i])

    def deleteProject(self):
        # cleanup Database
        query = "match(n) detach delete(n)"
        self.projectDatabaseAccess.executequery(query)

    def handleDeletedOrMovedFiles(self, pathToRawRepDataCsv, projectLastTrace):
        queries, lasttrace = self.produceQueries.createDeleteFileQueries(pathToRawRepDataCsv, projectLastTrace)
        for query in queries:
            self.projectDatabaseAccess.executequery(query)
        return lasttrace

    def persistPackageFileStructure(self, pathToRawRepDataCsv):
        queries, projectLastTrace = self.produceQueries.createPackageStructureQueries(pathToRawRepDataCsv)
        for query in queries:
            self.projectDatabaseAccess.executequery(query)
        return projectLastTrace

    def deleteLonelyPackages(self):
        query = self.produceQueries.createQueriesToDeleteLonelyPackageNodes()
        self.projectDatabaseAccess.executequery(query)

    def checkRelationExists(self, filepath):
        # produce match queries to find out if a relation already exists
        checkRelationExistQueries = self.produceQueries.createCheckRelationExistsQueries(filepath)
        for i in range(len(checkRelationExistQueries)):
            query = checkRelationExistQueries[i][3]
            # default expection: dependency does not yet exist in project database
            dependencyExists = False
            # if we find a record for this dependency, variable is set to true
            for record in self.projectDatabaseAccess.executeQueryWithResult(query):
                # if record is not empty (a relation exists)
                dependencyExists = True
                # if record is empty
            if dependencyExists == False:
                # create new dependency there
                class1 = checkRelationExistQueries[i][0]
                class2 = checkRelationExistQueries[i][1]
                relation = checkRelationExistQueries[i][2]
                self.persistDependency(class1, class2, relation)

    def persistDependency(self, class1, class2, relation):
        query = "MERGE (file:File {filename:'" + class1 + "'}) " \
                                                          "MERGE (filetwo:File {filename:'" + class2 + "'}) " \
                                                                                                       "CREATE (file)-[:`" + relation + "`]->(filetwo)"
        self.projectDatabaseAccess.executequery(query)

    def persistPackageStructure(self, oldpath, newpath, file):
        query = ""
        print("persisted package structure")
        self.projectDatabaseAccess.executequery(query)
