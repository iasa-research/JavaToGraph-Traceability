import csv
import platform

from datetime import datetime


class ProduceQueries:
    # imports all dependencies from the dependencymatrix.csv file
    # straight into the database; no check if they already exist
    def create_dependencies_queries(self, pathToDependencymatrix):
        with open(pathToDependencymatrix, 'r', encoding="utf-8") as f:
            csvreader = csv.reader(f, delimiter=';')
            # store queries in array
            dependencyqueries = []
            # iterate through rows in csv file
            for row in csvreader:
                class1 = row[0]
                class2 = row[1]
                relation = row[2]
                relationup = relation.upper()
                query = "MERGE (file:File {filename:'" + class1 + "'}) " \
                                                                  "MERGE (filetwo:File {filename:'" + class2 + "'}) " \
                                                                                                               "CREATE (file)-[:`" + relationup + "`]->(filetwo)"
                dependencyqueries.append(query)
            # return array with all queries
            return dependencyqueries

    # create match queries to find existing dependency relations between file nodes
    def createCheckRelationExistsQueries(self, pathToDependencymatrixcsv):
        with open(pathToDependencymatrixcsv, 'r', encoding="utf-8") as f:
            csvreader = csv.reader(f, delimiter=';')
            # store queries in array
            queries = []
            # iterate through rows in csv file
            for row in csvreader:
                class1 = row[0]
                class2 = row[1]
                relation = row[2]
                relationup = relation.upper()
                # query = "match(n:File {filename:'" + class1 + "'})" \
                #                                            "-[r:" + relationup + "]->(m:File {filename:'" + class2 + "'}) return n,r,m"
                query = "match(n:File)-[r:" + relationup + "]->(m:File) WHERE n.filename = '" + class1 + "' AND m.filename = '" + class2 + "' return n.filename, type(r), m.filename"
                list = [class1, class2, relationup, query]
                queries.append(list)
            # return array with all queries
            return queries

    # method creates queries to import/update the package/file subgraph in the graph
    # infos about the package/file subgraph:
    # The graph model stores the packages. Each package gets a different node type,
    # depending on its level in the package hierarchy. The first level is the project node,
    # then level zero is the first package e.g. 'src' which can contain a level 1 package
    # e.g. 'control' and so on.
    # The relation names differ in a similar way: The root node, project has a CONTAINSPACKAGE
    # relation to the  zero level package. All other relations between packages are called
    # CONTAINSSUBPACKAGE. The relation between a package/subpackage and a file is called CONTAINSFILE.
    def createPackageStructureQueries(self, pathToRawRepDataCsv):
        # array to store queries
        queries = []
        # array to store all files that were already processed
        filesAlreadyProcessed = []

        # variables to create relationQueries
        merge = "MERGE"
        projectNode = "(project)"
        fileNode = "(file)"
        packageBeginn = "(package"
        packageEnd = ")"
        containsFile = "-[:`CONTAINSFILE`]->"
        containsPackage = "-[:`CONTAINSPACKAGE`]->"
        containsSubpackage = "-[:`CONTAINSSUBPACKAGE`]->"
        whiteSpace = " "
        date = 0

        with open(pathToRawRepDataCsv, 'r', encoding="utf-8") as f:
            csvreader = csv.reader(f, delimiter=';')
            # iterate through rows in csv file
            next(csvreader, None)  # skip headers
            for row in csvreader:
                filename = row[0]
                # filter for files we did not process yet
                if filename not in filesAlreadyProcessed:
                    # filter for .java files
                    if filename.__contains__('.java'):
                        # find latest update of file in csv rows
                        latestRow = self.findLatestRow(pathToRawRepDataCsv, filename)
                        # assign variables for each cell value
                        newpath = latestRow[3]
                        realpath = latestRow[7]
                        changetype = latestRow[4]
                        projectname = latestRow[6]
                        commitdate = latestRow[2]
                        date = commitdate

                        # filter for files that were added or renamed
                        if changetype != "ModificationType.DELETE":
                            # e.g. src/command/loadCommand.java
                            if platform.system() == "Windows":
                                packages = newpath.rsplit("\\")
                            elif platform.system() == "Linux":
                                packages = newpath.rsplit("/")

                            # packages = ["src", "command", "loadCommand.java"]
                            # so there are two packages and one file in the array,
                            # therefore the number of packages in arrayLength-1

                            countPackages = len(packages) - 1
                            countSubpackages = len(packages) - 2

                            # create project/package/subpackage/file nodes
                            packageLevelCount = 0
                            query = "MERGE (project:Project {projectname: '" + projectname + "'})"
                            for package in packages:
                                if packageLevelCount == countPackages:
                                    query = query + " MERGE (file:File {filename:'" + package + "', lastcommit: '" + commitdate + "', path: '" + realpath + "'})"
                                    break
                                query = query + " MERGE (package" + str(packageLevelCount) + ":Level" + str(
                                    packageLevelCount) + "Package {packagename:'" + package + "'})"
                                packageLevelCount = packageLevelCount + 1

                            # create relations
                            # "MERGE (project)-[:`CONTAINSFILE`]->(file)"
                            if len(packages) == 1:
                                query = query + whiteSpace + merge + whiteSpace + projectNode + containsFile + fileNode + whiteSpace

                            # "MERGE (project)-[:`CONTAINSPACKAGE`]->(package0) " \
                            # "MERGE (package0)-[:`CONTAINSFILE`]->(file)"
                            elif len(packages) == 2:
                                query = query + whiteSpace + merge + whiteSpace + projectNode + containsPackage + packageBeginn + "0" + packageEnd + whiteSpace \
                                        + merge + whiteSpace + packageBeginn + "0" + packageEnd + containsFile + fileNode

                            # "MERGE (project)-[:`CONTAINSPACKAGE`]->(package0) " \
                            # "MERGE (package0)-[:`CONTAINSSUBPACKAGE`]->(package1)" \
                            # "MERGE (package1)-[:`CONTAINSFILE`]->(file)"
                            elif len(packages) == 3:
                                query = query + whiteSpace + merge + whiteSpace + projectNode + containsPackage + packageBeginn + "0" + packageEnd \
                                        + whiteSpace + merge + packageBeginn + "0" + packageEnd + containsSubpackage + packageBeginn + "1" + packageEnd \
                                        + whiteSpace + merge + packageBeginn + "1" + packageEnd + containsFile + fileNode

                            # len(packages) > 3
                            else:
                                relationQueryBeginn = whiteSpace + merge + whiteSpace + projectNode + containsPackage + packageBeginn + "0" + packageEnd + whiteSpace
                                relationQueryEnd = containsFile + fileNode
                                query = query + relationQueryBeginn
                                packageLevel = 0
                                for package in packages:
                                    if packageLevel < countSubpackages:
                                        query = query + whiteSpace + merge + packageBeginn + str(
                                            packageLevel) + packageEnd + containsSubpackage + packageBeginn \
                                                + str(packageLevel + 1) + packageEnd

                                    elif packageLevel == countSubpackages:
                                        query = query + whiteSpace + merge + whiteSpace + packageBeginn + str(
                                            packageLevel) + packageEnd + relationQueryEnd
                                    packageLevel = packageLevel + 1
                            queries.append(query)
                    filesAlreadyProcessed.append(filename)
        return queries, date

    # git does not store directories; if an directory is emptied before the next commit,
    # the directory is deleted in git. Therefore, package nodes that have no relation to a file or
    # a subpackage must be deleted (this action is necessary after each update)
    def createQueriesToDeleteLonelyPackageNodes(self):
        # give me all nodes that have the property packagename (true for all kind of packages) and that do not have an outgoing relationship
        query = "MATCH (package) " \
                "WHERE EXISTS(package.packagename) and not (package)-->() " \
                "DETACH DELETE package"
        return query

    # finds all files that were deleted or renamed (moved) in the lastest commit
    # creates the queries to delete them and their relations from database
    def createDeleteFileQueries(self, pathToRawRepDataCsv, projectLastTrace):
        # array to store the returned queries
        queries = []
        # array to store all files that were already processed
        filesAlreadyProcessed = []
        with open(pathToRawRepDataCsv, 'r', encoding="utf-8") as f:
            csvreader = csv.reader(f, delimiter=';')
            # iterate through rows in csv file
            next(csvreader, None)  # skip headers
            for row in csvreader:
                filename = row[0]
                commitdate = row[2]
                realpath = row[7]
                date = 0
                # filter for files we did not process yet
                if datetime.strptime(commitdate, "%Y-%m-%d %H:%M:%S%z") > projectLastTrace:
                    if filename not in filesAlreadyProcessed:
                        # filter for .java files
                        if filename.__contains__('.java'):
                            date = commitdate
                            # find latest update of file in csv rows
                            latestRow = self.findLatestRow(pathToRawRepDataCsv, filename)
                            # assign variables for each cell value
                            changetype = latestRow[4]
                            # filter for files that were deleted or renamed
                            # files that were moved to another package do have the type RENAME
                            # Mark requirements that are connected to changed/deleted files
                            if changetype == "ModificationType.MODIFY":
                                statequery = "MATCH(n:File)-[r:implements]->(m:Requirement) WHERE n.filename = '" + filename + "' SET m.review = 'true'"
                                queries.append(statequery)
                            if changetype == "ModificationType.DELETE":
                                # queryRelationships = "MATCH(n:File)-[r.implements]->(m:Requirement) WHERE n.filename = '" + filename + "' RETURN m.key as key, m.summary as summary, m.review as review"
                                # result = self.projectDatabaseAccess.executeQueryWithResult(queryRelationships)
                                statequery = "MATCH(n:File)-[r:implements]->(m:Requirement) WHERE n.filename = '" + filename + "' SET m.review = 'true'"
                                queries.append(statequery)
                                query = "MATCH (file:File) WHERE file.filename = '" + filename + "' DETACH DELETE file"
                                queries.append(query)
        return queries, date

    # ++++++++++++++ helper functions +++++++++++++++++++++++++++++++
    def findLatestRow(self, filepath, filename):
        with open(filepath, 'r', encoding="utf-8") as f:
            csvreader = csv.reader(f, delimiter=';')
            # iterate through rows in csv file
            next(csvreader, None)  # skip headers
            rownumber = 0
            for row in csvreader:
                # assign variables to cells in columns
                if filename == row[0]:
                    rownumber = row
        return rownumber

    # +++++++++++++ static queries to create the pattern subgraphs ++++
    def create_patterns_queries(self):
        patternsqueries = []
        # Singleton Pattern
        singleton_pattern = "CREATE (singleton:Pattern {patternname:'Singleton'})" \
                            + " MERGE (usingclass:Patterncomponent {componentname:'usingClass'})" \
                            + " MERGE (singletonclass:Patterncomponent {componentname:'SingletonClass'})" \
                            + " CREATE (singleton)-[:HASCOMPONENT]->(usingclass)" \
                            + " CREATE (singleton)-[:HASCOMPONENT]->(singletonclass)" \
                            + " CREATE (usingclass)-[:USES]->(singletonclass)"
        patternsqueries.append(singleton_pattern)
        # Strategy Pattern
        strategy_pattern = "CREATE (strategy:Pattern {patternname:'Strategy'})" \
                           + " MERGE (strategyclient:Patterncomponent {componentname:'StrategyClient'})" \
                           + " MERGE (abstractstrategy:Patterncomponent {componentname:'AbstractStrategy'})" \
                           + " MERGE (concretestrategy:Patterncomponent {componentname:'ConcreteStrategy'})" \
                           + " CREATE (strategy)-[:HASCOMPONENT]->(strategyclient)" \
                           + " CREATE (strategy)-[:HASCOMPONENT]->(concretestrategy)" \
                           + " CREATE (strategy)-[:HASCOMPONENT]->(abstractstrategy)" \
                           + " CREATE (concretestrategy)-[:EXTENDS]->(abstractstrategy)" \
                           + " CREATE (strategyclient)-[:USES]->(abstractstrategy)"
        patternsqueries.append(strategy_pattern)

        # Command Pattern
        command_pattern = "CREATE (command:Pattern {patternname:'Command'})" \
                          + " MERGE (commandcaller:Patterncomponent {componentname:'CommandCaller'})" \
                          + " MERGE (commandclient:Patterncomponent {componentname:'CommandClient'})" \
                          + " MERGE (abstractcommand:Patterncomponent {componentname:'AbstractCommand'})" \
                          + " MERGE (concretecommand:Patterncomponent {componentname:'ConcreteCommand'})" \
                          + " MERGE (commandreceiver:Patterncomponent {componentname:'CommandReceiver'})" \
                          + " CREATE (command)-[:HASCOMPONENT]->(commandclient)" \
                          + " CREATE (command)-[:HASCOMPONENT]->(commandcaller)" \
                          + " CREATE (command)-[:HASCOMPONENT]->(abstractcommand)" \
                          + " CREATE (command)-[:HASCOMPONENT]->(concretecommand)" \
                          + " CREATE (command)-[:HASCOMPONENT]->(commandreceiver)" \
                          + " CREATE (concretecommand)-[:EXTENDS]->(abstractcommand)" \
                          + " CREATE (commandclient)-[:USES]->(concretecommand)" \
                          + " CREATE (concretecommand)-[:USES]->(commandreceiver)" \
                          + " CREATE (commandclient)-[:USES]->(commandreceiver)" \
                          + " CREATE (commandcaller)-[:USES]->(abstractcommand)"
        patternsqueries.append(command_pattern)

        # Observer Pattern
        observer_pattern = "CREATE (observer:Pattern {patternname:'Observer'})" \
                           + " MERGE (publisher:Patterncomponent {componentname:'Publisher'})" \
                           + " MERGE (concretepublisher:Patterncomponent {componentname:'ConcretePublisher'})" \
                           + " MERGE (subscriber:Patterncomponent {componentname:'Subscriber'})" \
                           + " MERGE (concretesubscriber:Patterncomponent {componentname:'ConcreteSubscriber'})" \
                           + " CREATE (observer)-[:HASCOMPONENT]->(publisher)" \
                           + " CREATE (observer)-[:HASCOMPONENT]->(concretepublisher)" \
                           + " CREATE (observer)-[:HASCOMPONENT]->(subscriber)" \
                           + " CREATE (observer)-[:HASCOMPONENT]->(concretesubscriber)" \
                           + " CREATE (concretepublisher)-[:IMPLEMENTS]->(publisher)" \
                           + " CREATE (concretesubscriber)-[:IMPLEMENTS]->(subscriber)" \
                           + " CREATE (publisher)-[:USES]->(subscriber)" \
                           + " CREATE (concretesubscriber)-[:USES]->(concretepublisher)"
        patternsqueries.append(observer_pattern)

        # Proxy Pattern
        proxy_pattern = "CREATE (proxy:Pattern {patternname:'Proxy'})" \
                        + " MERGE (client:Patterncomponent {componentname:'Client'})" \
                        + " MERGE (proxy_class:Patterncomponent {componentname: 'Proxy Class'})" \
                        + " MERGE (realsubject:Patterncomponent {componentname: 'RealSubject'})" \
                        + " MERGE (subject:Patterncomponent {componentname:'Subject'})" \
                        + " CREATE (proxy)-[:HASCOMPONENT]->(client)" \
                        + " CREATE (proxy)-[:HASCOMPONENT]->(proxy_class)" \
                        + " CREATE (proxy)-[:HASCOMPONENT]->(realsubject)" \
                        + " CREATE (proxy)-[:HASCOMPONENT]->(subject)" \
                        + " CREATE (realsubject)-[:IMPLEMENTS]->(subject)" \
                        + " CREATE (proxy_class)-[:IMPLEMENTS]->(subject)" \
                        + " CREATE (client)-[:USES]->(proxy_class)" \
                        + " CREATE (client)-[:USES]->(subject)" \
                        + " CREATE (proxy_class)-[:USES]->(realsubject)"
        patternsqueries.append(proxy_pattern)

        # Round Tripping Persistent Object Pattern
        round_tripping_pattern = "CREATE (roundtrippingpersistentobject:Pattern {patternname:'Round Tripping Persistent Object'})" \
                                 + " MERGE (testclass:Patterncomponent {componentname:'TestClass'})" \
                                 + " MERGE (dao:Patterncomponent {componentname:'DAO'})" \
                                 + " MERGE (compareclass:Patterncomponent {componentname:'CompareClass'})" \
                                 + " CREATE (roundtrippingpersistentobject)-[:HASCOMPONENT]->(testclass)" \
                                 + " CREATE (roundtrippingpersistentobject)-[:HASCOMPONENT]->(dao)" \
                                 + " CREATE (roundtrippingpersistentobject)-[:HASCOMPONENT]->(compareclass)" \
                                 + " CREATE (testclass)-[:USES]->(dao)" \
                                 + " CREATE (testclass)-[:USES]->(compareclass)"
        patternsqueries.append(round_tripping_pattern)

        return patternsqueries
