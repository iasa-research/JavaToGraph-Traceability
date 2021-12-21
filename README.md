# READ ME

## Watch showcase here
https://drive.google.com/file/d/1AOkofseiU2wcuxEFpzoA6HyAOxmpcwXv/view?usp=sharing

## Installation 

### Requirements
* python 3.7+ 64bit
* connection to iasa_global database 
* neo4j local instance 
* pip3 

Install the following libs using pip3: 
* pydriller 
* setuptools 
* requests
* GitPython
* neo4j 
* psycopg2
* flask 
* flask_restful

### Build

1. Download the DependencyAnalysis.jar (request from admin) and copy .jar file into getrepository/control 

2. Start a new neo4j instance as project database and make sure it exists in global IASA project database 

3. Create postgreSQLconfig.ini in control package and add global database credentials (request from admin)

4. Run component: 
* In terminal, navigate to `getrepository/control`
* execute projectRestAPI.py with `python3 projectRestAPI.py` or create new run configuration for it

## Use 
### Requirements
* you have a publicly accessable git repository (e.g. on Github)
* the .class files are in this git repository (check that you don't ignore .class files in your .gitignore file)
* you have the iasa_global postgres database running 
* you have a neo4j project database instance running 
* you have a project registered in the iasa_global database with the associated project from git and the associated neo4j project database

### Execution 
Example for a project with project id 1: 
* create a project: `curl localhost:5000/createproject -d "project_id=1" -X POST`
* update a project: `curl localhost:5000/updateproject -d "project_id=1" -X POST`
* see project_id for a specific request `curl localhost:5000/request/<request_id>`

## Debug 
* process is printed in "Run"-terminal 




