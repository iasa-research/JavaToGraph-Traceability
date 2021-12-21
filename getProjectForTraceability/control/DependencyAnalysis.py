from xml.etree import ElementTree
import csv
import subprocess

from service.util.util import Util


class DependencyAnalysis:
    def analyseDependencies(self):
        # Call of the Dependency Analysis Function via JAR subprocess
        subprocess.check_call(['java', '-jar', 'DependencyAnalysis.jar'])

    def formatDependenciesClean(self):
        util = Util()
        # Open result csv file
        with open(util.getDependencyAnalysisLink() + '/result/dependencymatrix.csv', 'w', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # parsing of the DAAccess result file
            tree = ElementTree.parse(util.getDependencyAnalysisLink() + '/result/result.odem')
            tree.getroot()
            # select relevant results and write into result csv file
            for child in tree.iter('type'):
                for subchild in child.iter('depends-on'):
                    if ("java." not in subchild.attrib.get('name')):
                        childattrib = child.attrib.get('name')
                        childattrib = childattrib.split('.').pop()
                        childattrib = childattrib + ".java"
                        csvfile.write(childattrib + ";")
                        subchildattrib = subchild.attrib.get('name')
                        subchildattrib = subchildattrib.split('.').pop()
                        subchildattrib = subchildattrib + ".java"
                        csvfile.write(subchildattrib + ";")
                        csvfile.write(subchild.attrib.get('classification'))
                        csvfile.write("\n")

    def formatDependencies(self):
        print("formatdependencies")
        util = Util()
        with open(util.getDependencyAnalysisLink() + '/result/dependencymatrix.csv', 'w', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            tree = ElementTree.parse(util.getDependencyAnalysisLink() + "/result/result.odem")
            tree.getroot()
            for child in tree.iter('type'):
                for subchild in child.iter('depends-on'):
                    if ("java." not in subchild.attrib.get('name')):
                        csvfile.write("" + child.attrib.get('name') + ";")
                        csvfile.write(subchild.attrib.get('name') + ";")
                        csvfile.write(subchild.attrib.get('classification'))
                        csvfile.write("\n")
