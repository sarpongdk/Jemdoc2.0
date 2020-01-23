#!/usr/bin/env python2

import argparse, os, subprocess, sys, shutil, pkg_resources

from defaultconfig import DefaultConfig

PKG_NAME = "jemdoc"

class CommandLineParser(object):
    '''
    The CommandLineParser parses and processes command line arguments provided by the user.
    
    Args:

    Attributes:
        parser (ArgumentParser): this is the backbone for parsing cli arguments
        _cssEngine (str): represents the css preprocessor the user is using
    '''
    def __init__(self):
        self._standardConfig = DefaultConfig()
        self._DEFAULT_OUTDIR = "."
        self._version = "0.8.0"
        self._cssEngine = None
        self.parser = argparse.ArgumentParser(
            prog=PKG_NAME,
            description=
            "Produces html markup from a jemdoc SOURCEFILE.\n\nSee \033[96mhttp://jemdoc.jaboc.net/\033[00m for many more details."
        )
        self.parser.add_argument(
            "-s",
            "--show-config",
            dest="showConfig",
            help=
            "downloads the standard configuration 'standardconfig.txt' in the current directory",
            action="store_true")
        self.parser.add_argument("-v",
                                 "--version",
                                 dest="version",
                                 help="display Jemdoc version number",
                                 action="version",
                                 version="%(prog)s {}".format(self._version))
        self.parser.add_argument("-i",
                                 "--info",
                                 dest="info",
                                 help="display system information",
                                 action="store_true")
        self.parser.add_argument(
            "--css",
            dest="cssEngine",
            metavar="\033[94m<engine>\033[00m",
            help=
            "add stylesheet <engine> support [less|sass|scss] (defaults to plain css)",
            type=self._checkCssEngine,
            default="css")
        # self.parser.add_argument("-r",
        #                          "--react",
        #                          dest="useReact",
        #                          help="compile with ReactJS",
        #                          action="store_true")
        self.parser.add_argument("-c",
                                 "--config",
                                 dest="config",
                                 metavar="\033[94m<filename>\033[00m",
                                 help="add custom configuration file",
                                 action="store")
        self.parser.add_argument(
            "-d",
            "--dir",
            dest="outdir",
            metavar="\033[94m<dirname>\033[00m",
            help="output files in directory <dirname>", # name of ReactJS directory when compiling with ReactJS",
            type=self._checkOutputDir)
        self.parser.add_argument("input",
                                 help="relative path to input files",
                                 type=self._checkFileExists,
                                 nargs="*")
        self._args = self.parser.parse_args()
        # self.createStandardConfig()

    def getArgs(self):
        return self._args

    def getStandardConfigPath(self):
        return os.path.join(os.getcwd(), "configs", "standardconf.config")

    def getInputFiles(self):
        return self._args.input

    def _checkOutputDir(self, outdir):
        if os.path.isfile(outdir):
            raise argparse.ArgumentTypeError(
                "output directory name '{}' is not a directory, please give a directory!"
                .format(outdir))

        if os.path.exists(outdir):  # already exists
            prompt = "'{}' already exists. Would you like to override it (\033[92my\033[00m/\033[91mn\033[00m) ".format(
                outdir)
            response = raw_input(prompt).lower()
            while response not in ('y', 'yes', 'yeah', 'yah', 'n', 'no',
                                   'nah'):
                response = raw_input(prompt).lower()

            if response in ('y', 'yes', 'yeah', 'yah'):
                shutil.rmtree(outdir)
                os.mkdir(outdir)
            else:
                raise argparse.ArgumentTypeError(
                    "Duplicate directory name '{}'".format(outdir))
        else:
            os.mkdir(outdir)
        return outdir

    def _createOutputDir(self, dirname):
        try:
            os.mkdir(dirname)
        except FileExistsError as e:
            response = ""
            while response not in ("y", "yes", "no", "n"):
                response = raw_input("Would you like to overrwrite directory %s (\033[92my\033[00m/\033[91mn\033[00m) " % dirname).lower()
            if response in ("y", "yes"):
                shutil.rmtree(dirname)
                os.mkdir(dirname)
            else:
                raise FileExistsError("directory %s already exists" % dirname)

    def getOutputDir(self):
        if self._args.outdir:     
            return self._args.outdir
        else:
            return self._DEFAULT_OUTDIR

    def getUserConfig(self):
        if self._args.config:
            if not os.path.exists():
                raise FileNotFoundError("configuration file %s provided does not exist" % self._args.config)
        return self._args.config

    def showConfig(self):
        '''

        '''
        return self._args.showConfig

    def displayConfig(self):
        print CommandLineParser.getStandardConfig()
        sys.exit(1)

    def showInfo(self):
        return self._args.info

    def displayInfo(self):
        print 'Platform: ' + sys.platform + '.'
        print 'Python: {}, located at {}.'.format(sys.version[:5], sys.executable)
        sys.exit(1)

    # def useReact(self):
    #     return self._args.useReact

    def _install(self, package):
        try:
            print "Installing %s" % package
            subprocess.check_output(
                [sys.executable, "-m", "pip2", "-q", "install", "--user", package])
            return True
        except subprocess.CalledProcessError as ex:
            print "\033[91mWarn\033[00m: {} cannot be installed.\n Creating a non-react jemdoc website...".format(
                package)
            return False

    def _checkCssEngine(self, engine):
        engineName = engine.lower()
        if engineName not in ("less", "sass", "css", "scss"):
            raise argparse.ArgumentTypeError(
                "css engine '{}' is not supported".format(engine))
        return engineName

    def getCssEngine(self):
        return self._cssEngine

    def getCssStyle(self):
        return self._args.cssEngine.lower()

    @staticmethod
    def compileToCss(engine, inputfile, outputfile):
        if not os.path.exists(inputfile):
            print "\033[91mWarn\033[00m: %s does not exist in current directory, cannot be used!"
            return False

        try:
            out = os.path.join(os.getcwd(), outputfile)
            cmd = "{} {} {}".format(engine, inputfile, out)
            print cmd
            out = subprocess.check_output(cmd, shell=True)
            return True
        except subprocess.CalledProcessError as ex:
            print "\033[91mWarn\033[00m: {}".format(str(ex).lower())
            sys.exit(1)

    def _checkFileExists(self, filename):
        if "*" in filename:
            name, ext = os.path.splitext(filename)
            files = []
            if "*" in name:
                files = [str(f) for f in os.listdir('.') if os.path.isfile(f)]
            elif "*" in ext:
                files = [str(f) for f in os.listdir('.') if f.startswith(name)]
            return files

        if not os.path.exists(filename):
            raise argparse.ArgumentTypeError("file '{}' does not exists in current directory".format(filename))
        elif not os.path.isfile(filename):
            raise argparse.ArgumentTypeError("{} is a directory and not a file. Please provide a file".format(filename))
        return str(filename)

    def downloadStandardConfig(self):
        self._standardConfig.downloadStandardConfig()
        sys.exit(1)



if __name__ == "__main__":
    parser = CommandLineParser()
    args = parser.getArgs()
    if (args.info):
        parser.displayInfo()
    if (args.showConfig):
        parser.displayConfig()
    # print "Use React: {}".format(args.useReact)
    print "User Config file: {}".format(args.config)
    print "Outdir: {}".format(args.outdir)
    print "Innames: {}".format(args.input)
    print "CSS Engine: {}".format(args.cssEngine)

