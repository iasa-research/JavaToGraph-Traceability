from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from createProjectControl import CreateProjectControl
from updateProjectControl import UpdateProjectControl

app = Flask(__name__)
api = Api(app)

# DOCUMENTATION https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api

# add some test data
PROJECT = {
    # 'request_id': {'project_data_attribute': 'project_data'}
    '0': {'project_id': 0}
}


# input validation
# 1. check for existence
# test if a request with a specific request_id exists, if not: send error message
def abort_if_project_doesnt_exist(request_id):
    if request_id not in PROJECT:
        abort(404, message="Request failed, {} doesn't exist".format(request_id))


# 2. parsing
# initialise parser
parser = reqparse.RequestParser()
# add arguments to parser: project_id (int) and dev_id (int)
parser.add_argument('project_id', type=int)


# methods for endpoint request
# defines the endpoint to handle all request for project creation/update the component executed by runtime
# GET, DELETE, PUT
class request(Resource):
    # REST GET, needs request_id
    # test with: curl localhost:5000/request/1
    def get(self, request_id):
        # check if there is a request that matches the request_id
        abort_if_project_doesnt_exist(request_id)
        # look in array for request and return it
        return PROJECT[request_id]

    # REST DELETE, needs request_id
    # deletes an existing request: url is http://localhost:5000/request/<request_id>
    # test with: curl localhost:5000/request/1 -X DELETE
    def delete(self, request_id):
        abort_if_project_doesnt_exist(request_id)
        # uses already existing function del
        del PROJECT[request_id]
        # return nothing (shows that it was deleted) and code 204 that it worked
        return '', 204

    # REST PUT, needs request_id
    # NOT TO UPDATE A PROJECT BUT THE REQUEST IN THE API
    # updates an existing request: url is http://localhost:5000/request/<request_id>
    # test with: curl localhost:5000/request/1 -d "project_id=12" -X PUT
    def put(self, request_id):
        # parse the arguments and save it in python dictionary args
        args = parser.parse_args()

        # read python dict args using e.g. args['key']
        # save value from project_id in variable that is a json_dict, e.g.: project_id_dict = {'project_id': 1}
        project_id_dict = {'project_id': args['project_id']}

        # update project
        # save project in variable source
        source = PROJECT[request_id]
        # update project_id
        source['project_id'] = project_id_dict['project_id']

        # return the updated request
        return PROJECT[request_id], 201


# defines the endpoint to create a new project
# calls createProjectControl class and forwards request with project_id
class createProject(Resource):
    # create a new project
    def post(self):
        # parse the arguments and save it in python dictionary args
        args = parser.parse_args()

        # find out highest existing request_id_number, increment it by 1 and
        # save the number in variable 'request_id_number'
        request_id_number = int(max(PROJECT.keys())) + 1
        # print(request_id_number)
        # create a new request_id like 'request_<request_id_number>'
        request_id = str(request_id_number)

        # read python dict args using e.g. args['key']
        # save value from project_id in variable that is a json_dict, e.g.: project_id = {'project_id': 1}
        project_id_dict = {'project_id': args['project_id']}

        # create an empty project with newly created request_id
        # save it in variable 'source'
        source = PROJECT[request_id] = {'project_id': ''}
        # update project_id and developer_id
        source['project_id'] = project_id_dict['project_id']

        # trigger create project process
        createProjectControl = CreateProjectControl(source['project_id'])
        createProjectControl.createProject()

        # return newly added todo_ and status code
        return PROJECT[request_id], 201


# defines the endpoint to update a project
# calls updateProjectControl class and forwards request with project_id
class updateProject(Resource):
    def post(self):
        # parse the arguments and save it in python dictionary args
        args = parser.parse_args()

        # find out highest existing request_id_number, increment it by 1 and
        # save the number in variable 'request_id_number'
        request_id_number = int(max(PROJECT.keys())) + 1
        # print(request_id_number)
        # create a new request_id like 'request_<request_id_number>'
        request_id = str(request_id_number)

        # read python dict args using e.g. args['key']
        # save value from project_id in variable that is a json_dict, e.g.: project_id = {'project_id': 1}
        project_id_dict = {'project_id': args['project_id']}

        # create an empty project with newly created request_id
        # save it in variable 'source'
        source = PROJECT[request_id] = {'project_id': ''}
        # update project_id and developer_id
        source['project_id'] = project_id_dict['project_id']

        # trigger create project process
        updateProjectControl = UpdateProjectControl(source['project_id'])
        updateProjectControl.updateProject()

        # return newly added todo_ and status code
        return PROJECT[request_id], 201


# add url endpoints
# create project /createproject
# e.g. curl localhost:5000/createproject -d "project_id=1" -X POST
api.add_resource(createProject, '/createproject')

# update project /updateproject
# e.g. curl localhost:5000/updateproject -d "project_id=1" -X POST
api.add_resource(updateProject, '/updateproject')

# get a specific or all projects
# e.g. curl localhost:5000/request/1
api.add_resource(request, '/request/<request_id>')

# run
# https://www.modius-techblog.de/devops/python-flask-app-mit-docker-deployen/
# why we need the host='0.0.0.0'
if __name__ == '__main__':
    # set debug mode to false
    # important: specifiy host, otherwise execution in docker env does not work
    app.run(host='0.0.0.0', debug=False)
