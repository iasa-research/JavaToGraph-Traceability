from neo4j import GraphDatabase

class DatabaseAccess:
    # import the neo4j driver for Python
    # Connect to the neo4j database server
    # function takes parameters and puts them into method
    def __init__(self, uri, user, password):
        # self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=false)
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def executequery(self, query):
        with self._driver.session() as graphDB_Session:
            graphDB_Session.run(query)

    def executeQueryWithResult(self, query):
        with self._driver.session() as graphDB_Session:
            return list(graphDB_Session.run(query))
