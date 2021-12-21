import os
import platform

class Util:
    def getDependencyAnalysisLink(self):
        if (platform.system()=="Windows"):
            return self.getDependencyAnalysisLinkWindows()
        elif (platform.system()=="Linux"):
            return self.getDependencyAnalysisLinkLinux()

    def getDependencyAnalysisLinkWindows(self):
        link = os.getenv('LOCALAPPDATA')
        link = link.replace('\\', '/')
        link = link + ('/dependency_analysis')
        return link

    def getDependencyAnalysisLinkLinux(self):
        link = os.getenv('HOME')
        link = link.replace('\\', '/')
        link = link + ('/dependency_analysis')
        return link