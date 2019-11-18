#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
from bs4 import BeautifulSoup


class ReactFactory:
    def __init__(self, name="jemdoc-website"):
        self._cwd = os.getcwd()
        self._reactDirname = name
        self._mathjax = '''
        <!-- Configuration of inline MathJax expression -->
        <script type="text/x-mathjax-config">
            MathJax.Hub.Config({tex2jax: {
                inlineMath: [ ["$","$"], ["\\(","\\)"] ],
                displayMath: [ ["$$","$$"], ["\\[","\\]"] ]
            }});
        </script>

        <script type="text/javascript" async
            src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML">
        </script>
        '''
        self._pathToCSS = None

    def requestToCreateReactApp(self):
        response = input(
            "Would you like to install create-react-app (y/n) ").lower()
        while response not in ('y', 'yes', 'yeah', 'yah', 'n', 'no', 'nah'):
            response = input(
                "Would you like to install create-react-app (y/n) ").lower()

        if response in ('yes', 'y', 'yah', 'yeah'):
            try:
                output = subprocess.check_output(
                    'npm i create-react-app', shell=True)
                return True
            except subprocess.CalledProcessError:
                print(
                    "The CLI `create-react-app unavailable`\n Creating a non-react jemdoc website...")
                return False
        else:
            print("The CLI `create-react-app` is needed to create a react application.\nCreating a non-react jemdoc website...")
            return False

    def createReactApp(self):
        output = subprocess.check_output(
            "create-react-app %s" % self._reactDirname, shell=True)

    def testCreateReactApp(self):
        print("Creating react application named '%s'" % self._reactDirname)
        try:
            self.createReactApp()
            return True
        except subprocess.CalledProcessError as ex:
            print("Unable to create react application without create-react-app")
            return self.requestToCreateReactApp()

    def testNPM(self):
        try:
            output = subprocess.check_output('npm -v', shell=True)
            return True
        except subprocess.CalledProcessError as ex:
            print("NPM needs to be installed to compile as a React Application\nCreating a non-react jemdoc website...")
            return False

    def install(self, package):
        try:
            subprocess.check_output(
                [sys.executable, "-m", "pip", "install", package])
            return True
        except subprocess.CalledProcessError as ex:
            print(
                "BeautifulSoup cannot be installed.\n Creating a non-react jemdoc website...")
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
        dirs = os.listdir(self._cwd)
        if self._reactDirname in dirs:  # if has duplicate name
            return True
        else:
            return False

    def overwriteDuplicateFolderName(self):
        """
        This method checks if user wants to overwrite duplicate directory name if it exists. User is asked and based on user response, erases duplicate 
        """
        print("Directory named '%s' already exists." % self._reactDirname)
        prompt = "Would you like to overwrite directory (y/n)? "
        response = input(prompt).lower()
        while response not in ('y', 'yes', 'yeah', 'yah', 'n', 'no', 'nah'):
            response = input(prompt).lower()

        if response in ('yes', 'y', 'yah', 'yeah'):
            print("Deleting directory named '%s'" %self._reactDirname)
            path = os.path.join(self._cwd, self._reactDirname)
            shutil.rmtree(path)
            return True
        else:
            return False

    def testRequirements(self):
        if self.isDuplicateDirname():
            if not self.overwriteDuplicateFolderName():
                sys.exit(0)

        npm = self.testNPM()
        reactApp = self.testCreateReactApp() # this method also creates the react application if create-react-app is available
        soup4 = self.testBS4()

        if (npm and reactApp and soup4):
            print("Creating react application (Ctrl + c to interrupt)...")
            return True
        else:
            print("System requirements have not been met. Please ensure NPM and create-react-app are installed on system")
            print("Creating a non-react jemdoc website...")
            return False

    def raiseError(self, msg):
        print(msg)
        sys.exit(0)

    def getComponentsDir(self):
        return os.path.join(self._cwd, self._reactDirname, "src", "components")

    def getCSSDir(self):
        return os.path.join(self.getSrcDir(), "styles")

    def getSrcDir(self):
        return os.path.join(self._cwd, self._reactDirname, "src")

    def createComponentDir(self):
        dirname = self.getComponentsDir()
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        # os.chdir(dirname)
        # print(os.getcwd())

    def createCSSDir(self):
        dirname = self.getCSSDir()
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def move(self, source, destination):
        # print(destination)
        try:
            shutil.move(source, destination)
            return
        except:
            os.rename(source, destination)

    def moveToCssDir(self, cssFiles):
        """
        This method moves css files provided by the user into the styles directory in the react application

        Input: string[] - names of the css files
        Return: void
        """
        # cssFiles is a list of css files
        cssDir = self.getCSSDir()
        for css in cssFiles:
            # print(os.path.join(self._cwd, css))
            self.move(os.path.join(self._cwd, css), os.path.join(cssDir, css))

    def askForNewFilename(self):
        response = input("Please enter a new filename: ").capitalize()
        return response

    def addComponent(self, component):
        """
        This method adds the component file to the appropriate directory
        """
        path = self.getComponentsDir()
        filepath = os.join(path, component)
        while os.path.exists(filepath):
            print("Component with name '%s' already exists")
            response = self.askForNewFilename()
            filepath = os.join(path, response)
        os.makedirs(filepath)

    def getAllCSSImports(self):
        """
        This method creates all of the css import statements for the react application
        """
        imports = ''
        cssFiles = os.listdir(self.getCSSDir())
        for css in cssFiles:
            cssPath = os.path.join(".", "styles", css)
            statement = "import '%s';\n" % cssPath
            imports += statement
        # print(imports)  # for debugging
        return imports

    def createComponent(self, componentName, render, state=""):
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

        return component

    def addBootstrap(self, version = "4.3.1"):
        """
        This method adds bootstrap@4.3.1, jquery@1.9.1 and popper.js@1.14.7 to the react application via npm. 
        If npm is not installed or bootstrap is unavailable the react application cannot use bootstrap

        Input: string - version number of bootstrap. Defaults to version 4.3.1
        Output: void
        """
        reactAppDir = os.path.join(self._cwd, self._reactDirname)
        os.chdir(reactAppDir);
        try:
            print("Adding Twitter Bootstrap4 to application...")
            output = subprocess.check_output("npm i -S tsutils@3.17.1 jquery@1.9.1 popper.js@1.14.7 bootstrap@%s" %version, shell=True)
            # output = subprocess.check_output("npm i -S jquery@1.9.1", shell=True)
            # output = subprocess.check_output("npm i -S popper.js@1.14.7", shell=True)
            return True
        except subprocess.CalledProcessError as ex:
            print("Twitter Bootstrap4 has not been installed. Proceeding without Twitter Bootstrap4")
            return False

    def getBootstrapImport(self):
        """
        This method returns all the necessary reactjs Twitter Bootstrap import statements

        Input: void
        Output: string - import statements
        """
        return "import '../node_modules/bootstrap/dist/css/bootstrap.min.css'\nimport '../node_modules/bootstrap/dist/js/bootstrap.min.js'\nimport '../node_modules/jquery/dist/jquery.slim.min.js;\n\n\n"

    def insertBootstrap4(self):
        if self.addBootstrap():
            indexFile = os.path.join(self.getSrcDir(), "index.js")
            # prepend at beginning of file
            with open(indexFile, "r+") as f:
                content = f.read()
                f.seek(0, 0)
                f.write(self.getBootstrapImport() + content)

    def cleanReactAppDir(self):
        """
        This method clears the predefined css files and the index.js file. 
        It replaces each of these files with user created/defined files

        Input: void
        Output: void
        """
        pass

    def insertCSSToFile(self, filename, css):
        """
        This method inserts the css files into the styles directory that will be used by all components of the react application.
        These will be imported into all the component classes via another method
        """
        pass

    def insertMathJax(self):
        """
        This method inserts the MathJax CDN into index.html in the react application
        Uses BeautifulSoup to insert script tags into the index.html file

        Input: void
        Output: void
        """
        pass

    def renderToDOM(self, components):
        """
        This method renders the components provided in the list 'components' to the DOM in the order in which the list is provided

        Input: string[] - list of components to render
        Output: void
        """
        ui = ""
        render = """
        ReactDOM.render(
            <React.Fragment>
                %s
            </React.Fragment>, document.getElementById(root)
        );
        """ 
        return render





def seedFiles(cssFiles):
    for css in cssFiles:
        os.makedirs(css)

if __name__ == "__main__":
    # commented means it works correctly and has been unit tested
    #cssFiles = ["main.css", "textbox.css", "homepage.css", "about.css"]
    #seedFiles(cssFiles)

    factory = ReactFactory()
    # factory.testRequirements()
    # factory.createComponentDir()
    # factory.createCSSDir()
    # factory.moveToCssDir(cssFiles)
    # factory.getAllCSSImports()
    # factory.insertBootstrap4()
    # print(factory.createComponent("TestComponent", "<h1>David</h1>"))
