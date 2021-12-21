import os
import shutil
import stat
from subprocess import call
from git import Repo

from DependencyAnalysis import DependencyAnalysis
from GetRepositoryData import GetRepositoryData
from ManagePersistence import ManagePersistence
from service.util.util import Util


class ExecuteProjectCreationControl:
    link_to_home_directory = "1"

    def __init__(self, projectdatabase_url, projectdatabase_username, projectdatabase_password):
        # set class variables
        self.util = Util()
        self.managePersistence = ManagePersistence()
        self.dependencyAnalysis = DependencyAnalysis()

        # get environment
        self.link_to_home_directory = self.util.getDependencyAnalysisLink()

        # set paths to local project data
        self.class_csv = self.link_to_home_directory + '/result/rawrepdatacsv.csv'
        self.dependency_csv = self.link_to_home_directory + '/result/dependencymatrix.csv'

        # init project database connection
        self.managePersistence.init_connection(projectdatabase_url, projectdatabase_username, projectdatabase_password)

    # clones repo from Github
    def getSourceCode(self, projectGitURL):
        # prepare working directory for cloning a git project into it
        self.cleanUpFolder(self.link_to_home_directory)
        # clone repository from git
        # save repo temporarily in home directory
        Repo.clone_from(projectGitURL, self.link_to_home_directory)
        # check if compiled files exist in clones git repository (otherwise the dependency analysis does not work)
        if (self.compiledFilesExist(self.link_to_home_directory)) is not True:
            raise Exception('No compiled files found! Please provide a project with compiled java code.')

    # extract project data from cloned repo into csv file "rawrepdatacsv.csv"
    def extractProjectData(self, path):
        os.makedirs(self.link_to_home_directory + "/result")
        # with open(self.link_to_home_directory + "/result/rawrepdatacsv.csv", 'w', "utf-8"):
        #   pass
        getRepositoryData = GetRepositoryData()
        getRepositoryData.getRepInfo(self.link_to_home_directory + "/result/rawrepdatacsv.csv", path)

    # persists package file structure (idempotent)
    # persists the dependencies between the file nodes
    def persistProjectData(self):
        # persist project files in project database
        projectLastTrace = self.managePersistence.persistPackageFileStructure(self.link_to_home_directory + '/result/rawrepdatacsv.csv')
        # persist class dependencies in project database
        self.managePersistence.process_dependency_persisting(
            self.link_to_home_directory + '/result/dependencymatrix.csv')
        return projectLastTrace

    # 1. deletes all files that were either deleted from github project or renamed (moved)
    # 2. creates package/file structure for files that were added or renamed
    # this way, the moved files are created at another place in the graph
    # finally, the packages that no longer have any files are deleted
    def updateProjectFiles(self, projectLastTrace):
        # check if file already exists and if not, persist it
        # delete all files from graph structure that were either deleted from git project or renamed (they may be moved)
        newprojectLastTrace = self.managePersistence.handleDeletedOrMovedFiles(self.link_to_home_directory + '/result/rawrepdatacsv.csv', projectLastTrace)
        # create all package/file structure that is not there yet
        self.managePersistence.persistPackageFileStructure(self.link_to_home_directory + '/result/rawrepdatacsv.csv')
        self.managePersistence.deleteLonelyPackages()
        return newprojectLastTrace

    # deletes packages, that have no longer any files in them
    # github deletes those automatically, so this is necessary
    # to keep graph and github project similar
    def deleteLonelyPackages(self):
        self.managePersistence.deleteLonelyPackages()

    # checks for each dependency if it exists already in the graph, if not, it add the relation
    def updateProjectDependencies(self):
        # check if relation already exists and if not, persist it
        self.managePersistence.checkRelationExists(self.dependency_csv)

    # persists the pattern in the graph
    def persistPatternData(self):
        self.managePersistence.process_patterns_persisting()

    # analyses the project and writes the dependencies to the "dependencymatrix.csv"
    def analyseDependencies(self):
        self.dependencyAnalysis.analyseDependencies()
        self.dependencyAnalysis.formatDependenciesClean()

    # checks if the compiled files (.class files) are in the cloned repo
    # if they are not, the dependency analysis can not be executed
    def compiledFilesExist(self, link):
        for root, dirs, files in os.walk(link):
            for name in files:
                if ".class" in name:
                    print(name)
                    return True
        return False

    # cleans up the folder with the cloned project, csv files and so on from disk
    # executed before the whole process is started
    def cleanUpFolder(self, link):
        linkgit = link + ('/.git')
        linkgitobjpack = link + ('/.git/objects')

        # Cleanup of the Workdirectory
        if os.path.isdir(linkgit):
            call(['attrib', '-H', linkgit])
            for root, dirs, files in os.walk(linkgitobjpack):
                for f in files:
                    os.chmod(root + "/" + f, stat.S_IWRITE)
                    os.unlink(root + "/" + f)
            os.chmod(linkgitobjpack, stat.S_IWRITE)
            shutil.rmtree(linkgitobjpack)
            shutil.rmtree(linkgit)
            for entry in os.scandir(link):
                if entry.is_file():
                    os.unlink(entry)
                else:
                    shutil.rmtree(entry)
        elif (os.path.isdir(link + '/result')):
            shutil.rmtree(link + '/result')

    # deletes folder from disk completely after process
    def deleteLocalProjectFolder(self):
        if os.path.exists(self.link_to_home_directory):
            shutil.rmtree(self.link_to_home_directory)

    # deletes all data from the project database
    def deleteDataFromProjectDatabase(self):
        # clean up database
        self.managePersistence.deleteProject()
