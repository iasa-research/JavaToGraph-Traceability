# IASA JavaToGraph-Traceability (former name: getProjectDataForTraceability)

## Infos 
* additional files necessary for deployment that are not available on Github: 
* DependencyAnalysis.jar and postgreSQLconfig.ini
* request from the IASA-leaders and copy both in the control package (see also README.md in the control package)

## Depends on other services
* iasa-global database
* iasa neo4j project databases

## Docker-Image 
### Description
This image contains an environment to deploy the `JavaToGraph`-IASA component for pattern validation usages, which pulls java project data from its git repository and writes the classes and their dependencies as graph in a neo4j graph database.

### File System Environment:
* path to application within container: /usr/iasa/getProjectDataForTraceability
* path to documentation within container: /usr/iasa/documentation

### Building the image
* this is only necessary when the app has changed and the used image was deleted or not the image was not yet created
* if javatograph_patternanalysis is in the result list of `docker image ls` this is not necessary
* vice versa, you'd probably need to delete this image again from the server before you can create a new one with this command:  
```
docker build -t javatograph_traceability  .
```
#### Error History during Image Building 
* packages were not recognized: fixed this by adding `__init__.py` in each (sub)package execept the one with the starting file in
* git was not installed on image: fixed this by adding the git installation to the docker file

### create container from the image 

```
docker run -p 5000:5000/tcp -d javatograph_traceability python3 projectRestAPI.py
```

* the commands exposes the application to the outside world using the port flag -p 
* and uses the deamon flag -d to start the application in the background 
* and uses the command `python3 projectRestAPI.py` within the container right after startup 

### Usage 
Example for a project with project id 1 in iasa-global:

create a project: `curl <your ip/localhost>:5001/createproject -d "project_id=1" -X POST`
update a project: `curl <your ip/localhost>:5001/updateproject -d "project_id=1" -X POST`
see project_id for a specific request: `curl <your ip/localhost>:5001/request/<request_id>`

### Debugging 
#### FAQ 
Check the FAQs in FAQ.md before you start debugging.

#### Basic docker commands
* list docker images: `docker image ls`
* list containers: `docker ps`
* start: `docker start <containername>`
* stop: `docker stop <containername>`
* delete container: `docker kill <containername>`
* remove image: `docker rmi <imagename>`

#### Start up 
* run the image/ start the container without the -d flag, then you get all output directly 
* in this case sometimes, only the http-requests are displayed, the moment you stop the container, you see all the program output

#### Logs 
* change directory to the docker log folder (from home): 
```
cd /var/lib/docker/containers`
```
* use `docker ps` to find the container you want to analyse the logs for
* in the folder: `cd <containername>`
* there should be the log for the container 