import psycopg2
import configparser


class GlobalDatabaseAccess:
    def __init__(self):
        try:
            # get environment
            config = configparser.ConfigParser()
            config.read('postgreSQLconfig.ini')

            user = config['REMOTE']['USER']
            password = config['REMOTE']['PASSWORD']
            host = config['REMOTE']['HOST']
            port = config['REMOTE']['PORT']
            database = config['REMOTE']['DATABASE']

            print(user)


            # connect to to postgreSQL
            self.connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
            self.cursor = self.connection.cursor()
            print("cursor set")

            # Print PostgreSQL Connection properties
            print(self.connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            self.cursor.execute("SELECT version();")
            record = self.cursor.fetchone()
            print("You are connected to - ", record, "\n")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def executeQuery(self, query):
        self.cursor.execute(query)
        record = self.cursor.fetchone()
        if record != None:
            return record[0]
        else:
            raise Exception("Error while fetching data from PostgreSQL: No project with this id")

    def executeUpdateQuery(self, query):
        self.cursor.execute(query)
        self.connection.commit()

    def close(self):
        # closing database connection.
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("\n PostgreSQL connection closed")
