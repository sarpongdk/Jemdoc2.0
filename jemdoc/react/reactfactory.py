#!/usr/bin/env python2
import os
import subprocess
import sys
import shutil
from bs4 import BeautifulSoup


class ReactFactory:
    def __init__(self):
        name, title = self.getMetaDataFromUser()
        self._appTitle = title
        self._reactDirname = name
        self._components = []

    def getMetaDataFromUser(self):
        print """
\033[96mJemdoc 2.0 Initialization\033[00m

This utility will walk you through creating a react application.
If no answer is provided by the user a default name in parenthesis will be used
Press ^C \033[91m(Ctrl + C)\033[00m at any time to quit.
"""

        prompt = "application name (\033[96mjemdoc-website\033[00m): "
        defaultName = "jemdoc-website"
        name = raw_input(prompt)
        if name == "" or not name:
            name = defaultName.strip().lower()

        prompt = "application title (\033[96mJemdoc Website\033[00m): "
        defaultTitle = "Jemdoc Website"
        title = raw_input(prompt)
        if title == "" or not title:
            title = defaultTitle.strip().lower()
        
        return (name.strip().lower(), title.strip().capitalize())

    def requestToCreateReactApp(self):
        response = raw_input(
            "Would you like to install create-react-app (\033[92my\033[00m/\033[91mn\033[00m) ").lower()
        while response not in ('y', 'yes', 'yeah', 'yah', 'n', 'no', 'nah'):
            response = raw_input(
                "Would you like to install create-react-app (\033[92my\033[00m/\033[91mn\033[00m) ").lower()

        if response in ('yes', 'y', 'yah', 'yeah'):
            try:
                output = subprocess.check_output(
                    'npm i create-react-app', shell=True)
                return True
            except subprocess.CalledProcessError:
                print "The CLI `create-react-app unavailable`\n Creating a non-react jemdoc website..."
                return False
        else:
            print "The CLI `create-react-app` is needed to create a react application.\nCreating a non-react jemdoc website..."
            return False

    def createReactApp(self):
        output = subprocess.check_output(
            "create-react-app %s" % self._reactDirname, shell=True)

    def testCreateReactApp(self):
        print "Creating react application named '\033[96m%s\033[00m'" % self._reactDirname
        try:
            self.createReactApp()
            return True
        except subprocess.CalledProcessError as ex:
            print "\033[91mWarn\033[00m: Unable to create react application without create-react-app"
            return self.requestToCreateReactApp()

    def testNPM(self):
        try:
            output = subprocess.check_output('npm -v', shell=True)
            return True
        except subprocess.CalledProcessError as ex:
            print "\033[91mWarn\033[00m: NPM needs to be installed to compile as a React Application\nCreating a non-react jemdoc website..."
            return False

    def install(self, package):
        try:
            print "Installing %s" %package
            subprocess.check_output(
                [sys.executable, "-m", "pip2", "-q", "install", "--user", package])
            return True
        except subprocess.CalledProcessError as ex:
            print "\033[91mWarn\033[00m: %s cannot be installed.\n Creating a non-react jemdoc website..." %package
            return False

    def testBS4(self):
        try:
            from bs4 import BeautifulSoup
            return True
        except ImportError:
            installed = self.install("bs4")
            return installed

    def isDuplicateDirname(self):
        """
        This method checks if a duplicate name exists in the directory in which the react application is to be created.
        If duplicate name exists, returns True. Otherwise returns False

        Input: void
        Output: boolean
        """
        dirs = os.listdir(os.getcwd())
        if self._reactDirname in dirs:  # if has duplicate name
            return True
        else:
            return False

    def overwriteDuplicateFolderName(self):
        """
        This method checks if user wants to overwrite duplicate directory name if it exists. User is asked and based on user response, erases duplicate 
        """
        print "\033[92mInfo\033[00m: Directory named '%s' already exists." % self._reactDirname
        prompt = "Would you like to overwrite directory (\033[92my\033[00m/\033[91mn\033[00m)? "
        response = raw_input(prompt).lower()
        while response not in ('y', 'yes', 'yeah', 'yah', 'n', 'no', 'nah'):
            response = raw_input(prompt).lower()

        if response in ('yes', 'y', 'yah', 'yeah'):
            print "\033[92mInfo\033[00m: Deleting directory named '%s'" %self._reactDirname
            path = os.path.join(os.getcwd(), self._reactDirname)
            shutil.rmtree(path)
            return True
        else:
            return False

    def testRequirements(self):
        """
        This method verifies that all the necessary requirements needed to create a react application have been met
        If True a react application is created, otherwise it falls back to creating a static jemdoc website

        Input: void
        Output: boolean - whether all the requirements have been met
        """
        if self.isDuplicateDirname():
            if not self.overwriteDuplicateFolderName():
                sys.exit(0)

        npm = self.testNPM()
        reactApp = self.testCreateReactApp() # this method also creates the react application if create-react-app is available
        soup4 = self.testBS4()

        if (npm and reactApp and soup4):
            print "Creating react application \033[91m(Ctrl + c to interrupt)\033[00m..."
            return True
        else:
            print "System requirements have not been met. Please ensure NPM and create-react-app are installed on system"
            print "Creating a non-react jemdoc website..."
            return False

    def raiseError(self, msg):
        print msg
        sys.exit(0)

    def getComponentsDir(self):
        return os.path.join(os.getcwd(), self._reactDirname, "src", "components")

    def getCSSDir(self):
        return os.path.join(self.getSrcDir(), "styles")

    def getSrcDir(self):
        return os.path.join(os.getcwd(), self._reactDirname, "src")

    def createComponentDir(self):
        dirname = self.getComponentsDir()
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        # os.chdir(dirname)
        # print os.getcwd()

    def createCSSDir(self):
        dirname = self.getCSSDir()
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def move(self, source, destination):
        # print destination
        try:
            shutil.move(source, destination)
            return
        except:
            os.rename(source, destination)

    def moveToCssDir(self, cssFiles):
        """
        This method moves css fileObjs provided by the user into the styles directory in the react application

        Input: string[] - names of the css fileObjs
        Return: void
        """
        # cssFiles is a list of css fileObjs
        cssDir = self.getCSSDir()
        for css in cssFiles:
            source = os.path.join(os.getcwd(), css)
            dest = os.path.join(cssDir, css)
            # print "Moving %s to %s" %(source, dest) # debug
            self.move(source, dest)

    def askForNewFilename(self):
        response = raw_input("Please enter a new fileObjname: ").capitalize()
        return response

    def addComponent(self, component):
        """
        This method adds the component fileObj to the appropriate directory
        """
        path = self.getComponentsDir()
        fileObjpath = os.join(path, component)
        while os.path.exists(fileObjpath):
            print "Component with name '%s' already exists"
            response = self.askForNewFilename()
            fileObjpath = os.join(path, response)
        os.makedirs(fileObjpath)

    def getAllCSSImports(self):
        """
        This method creates all of the css import statements for the react application
        """
        imports = ''
        cssDir = self.getCSSDir()
        # print "CSS Directory: %s" % cssDir
        cssFiles = os.listdir(cssDir)
        for css in cssFiles:
            cssPath = os.path.join(".", "styles", css)
            statement = "import '%s';\n" % cssPath
            imports += statement
        # print imports  # for debugging
        return imports

    def createComponent(self, componentName, render, state="", write=False):
        """
        This method creates a generic component and writes the component to a JSX fileObj in the  components directory
        """
        component = """
%s

import { React } from 'react';

export class %s extends React.Component {
    constructor(props) {
        super(props);

        this.state = {%s};
    }

    render() {
        return (
            <React.Fragment>
                %s
            </React.Fragment>
        );
    }
}
""" % (self.getAllCSSImports(), componentName, state, render)

        fileObjname = "%s.jsx" %componentName.capitalize()
        # print component #debug
        if write:
            self.writeComponent(fileObjname, component)
        self._components.append(componentName.capitalize())
        return component

    def writeComponent(self, fileObjname, component):
        """
        This method creates and flushes the component fileObj into the components directory as a JSX fileObj

        Input: string - fileObjname, string - component JSX fileObj contents
        Output: void
        """
        componentsDir = self.getComponentsDir()
        if not os.path.exists(componentsDir):
            os.makedirs(componentsDir)

        fileObjPath = os.path.join(componentsDir, fileObjname)
        fileObj = open(fileObjPath, "w+")
        fileObj.write(component)
        fileObj.flush()
        fileObj.close()

    def addBootstrap(self, version = "4.3.1"):
        """
        This method adds bootstrap@4.3.1, jquery@1.9.1 and popper.js@1.14.7 to the react application via npm. 
        If npm is not installed or bootstrap is unavailable the react application cannot use bootstrap

        Input: string - version number of bootstrap. Defaults to version 4.3.1
        Output: void
        """
        originalDir = os.getcwd()
        reactAppDir = os.path.join(originalDir, self._reactDirname)
        os.chdir(reactAppDir);
        try:
            print "Adding Twitter Bootstrap4 to application..."
            output = subprocess.check_output("npm i -S tsutils@3.17.1 jquery@1.9.1 popper.js@1.14.7 bootstrap@%s" %version, shell=True)
            # output = subprocess.check_output("npm i -S jquery@1.9.1", shell=True)
            # output = subprocess.check_output("npm i -S popper.js@1.14.7", shell=True)
            return True
        except subprocess.CalledProcessError as ex:
            print "\033[91mWarn\033[00m: Twitter Bootstrap4 has not been installed. Proceeding without Twitter Bootstrap4"
            return False
        finally:
            os.chdir(originalDir)

    def getBootstrapImport(self):
        """
        This method returns all the necessary reactjs Twitter Bootstrap import statements

        Input: void
        Output: string - import statements
        """
        return """
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import '../node_modules/bootstrap/dist/js/bootstrap.min.js';
import '../node_modules/jquery/dist/jquery.slim.min.js';

"""

    # def insertBootstrap4(self):
    #     if self.addBootstrap():
    #         indexFile = os.path.join(self.getSrcDir(), "index.js")
    #         # prepend at beginning of fileObj
    #         with open(indexFile, "r+") as f:
    #             content = f.read()
    #             f.seek(0, 0)
    #             f.write(self.getBootstrapImport() + content)

    def cleanReactAppDir(self):
        """
        This method clears the predefined css fileObjs and the index.js fileObj. 
        It replaces each of these fileObjs with user created/defined fileObjs

        Input: void
        Output: void
        """
        
        # deleting the default CSS and JS fileObjs
        path = self.getSrcDir()
        fileObjs = os.listdir(path)

        for fileObj in fileObjs:
            extension = os.path.splitext(fileObj)[1]
            # print extension # debug

            if extension in (".css", ".js", ".svg"):
                fileObjpath = os.path.join(path, fileObj)
                os.remove(fileObjpath)
        

    # def insertCSSToFile(self, fileObjname, css):
    #     """
    #     This method inserts the css fileObjs into the styles directory that will be used by all components of the react application.
    #     These will be imported into all the component classes via another method
    #     """
    #     pass

    def getPublicDir(self):
        return os.path.join(os.getcwd(), self._reactDirname, "public")

    def processHTMLEntryPoint(self):
        """
        This method inserts the MathJax CDN into index.html in the react application
        Uses BeautifulSoup to insert script tags into the index.html fileObj

        Input: void
        Output: void
        """
        # creating mathjax script and config tags to insert into index.html
        path = os.path.join(self.getPublicDir(), "index.html")
        html = open(path, "r+")
        soup = BeautifulSoup(html, "html.parser")
        scriptTag = soup.new_tag('script', src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML", type="text/javascript", asyn="async")
        configTag = soup.new_tag("script", type="text/x-mathjax-config")
        config = """
MathJax.Hub.Config({tex2jax: {
    inlineMath: [ ["$","$"], ["\\(","\\)"] ],
    displayMath: [ ["$$","$$"], ["\\[","\\]"] ]
}});"""
        configTag.append(config)
        soup.head.append(configTag)
        soup.head.append(scriptTag)


        # changing app title
        soup.title.string.replace_with(self._appTitle)

        html.close()
        
        # writing new html back to fileObj
        newHTML = soup.prettify("utf-8")
        with open(path, "wb") as fileObj:
            fileObj.write(newHTML)
        
    
    def getAllComponentImports(self):
        imports = ""
        for component in self._components:
            imports += "import { %s } from './components/%s.jsx'\n" %(component, component)


    # TODO: implement this method
    def renderToDOM(self, components):
        """
        This method renders the components provided in the list 'components' to the DOM in the order in which the list is provided

        Input: string[] - formatted component string to render. contents are rendered as is given
        Output: void
        """

        # TODO: import all components here
        # TODO: import all CSS here 
        ui = """
import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
%s

ReactDOM.render(
    <React.Fragment>
        %s
    </React.Fragment>, document.getElementById('root')
);
""" %(self.getAllComponentImports(), components)

        path = os.path.join(self.getSrcDir(), "index.js")
        fileObj = open(path, "w")
        bootstrap4 = self.getBootstrapImport()
        fileObj.write(bootstrap4)
        fileObj.write(ui)
        fileObj.flush()
        fileObj.close()



# TODO: consider when user uses multiple html pages

def seedFiles(cssFiles):
    if os.path.exists("jemdoc-website"):
        path = os.path.join(os.getcwd(), "jemdoc-website")
        try:
            shutil.rmtree(path)
        except:
            os.rmdir(path)            

    for css in cssFiles:
        if not os.path.exists(css):
            fileObj = open(css, "w")
            fileObj.flush()
            fileObj.close()

if __name__ == "__main__":
    # try-catch block is to handle the keyboard interrupt exception
    try:
        # commented means it works correctly and has been unit tested
        cssFiles = ["main.css", "textbox.css"]
        seedFiles(cssFiles)

        factory = ReactFactory()
        factory.testRequirements()
        factory.createComponentDir()
        factory.createCSSDir()
        factory.moveToCssDir(cssFiles)
        factory.cleanReactAppDir()
        factory.createComponent("TestComponent", "<h1>David</h1>", "", True) # error here
        factory.processHTMLEntryPoint()
        factory.renderToDOM("""
# <TestComponent>
#     <NonExistingComponent>Hello, World!</NonExistingComponent>
# </TestComponent>
# """)
    except KeyboardInterrupt:
        print "\n\nCancelling creation of react application...\n"
        if os.path.exists("jemdoc-website"):
            path = os.path.join(os.getcwd(), "jemdoc-website")
            try:
                shutil.rmtree(path)
            except:
                os.rmdir(path) 
    except AttributeError as ex:
        print "Attribute Error...\n"
        print ex


#TODO: fallback to using regular jemdoc in the event of an error at compile time
