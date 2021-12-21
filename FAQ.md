# FAQ 

## Error Messages 

### Build 
#### Installing site package psycopg2:  
* error "pg_config executable not found", see here: https://stackoverflow.com/questions/11618898/pg-config-executable-not-found
* ubuntu: `sudo apt-get install libpq-dev`

### Execution: Create/ update project 
#### Generic errors 
* check if `curl localhost:5000/request/0` works, if not restart and do not delete this sample request

#### Issues with global database (postgres)
* check if the project you want to create exists in the global database and has the same project_id
* check if all attributes (projectdatabase_url, projectdatabase_user,...) have a value for this project_id
* check if global database can be reached (from your network, e.g. check vpn connection)
* check if you put the right credentials in your postgreSQLconfig.ini file 

#### Issues with the project database (neo4j)
* check if project database can be reached (from your network, e.g. check vpn connection)
* if you are using neo4j version 4.0 or higher, change 
`self._driver  = GraphDatabase.driver(uri, auth=(user, password))`
in class DatabaseAccess.py to 
`self._driver = GraphDatabase.driver(uri, auth=(user,password), encrypted=false)`

#### Error message in terminal: cannot find dependencyAnalysis.jar
* did you add the DependencyAnalysis.jar to your control package? if not, request it from admin and do 
* make sure you are executing from a path where the .jar-file is visible, e.g. from `getrepository/control`

## Usage for others than HBRS-students 
* if you are not a HBRS-student but are interested in IASA contact me under franziska.kuesters@smail.inf.h-brs.de