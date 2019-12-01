import argparse, os, subprocess, sys, shutil


class CommandLineParser():
    """
    This class parses the command line arguments. 
    Upon illegal usage of commandline arguments or error in parsing commandline arguments, it terminates and exits the program
    """
    def __init__(self):
        self._DEFAULT_OUTDIR = "."
        self._version = '0.7.3'
        self._cssEngine = None
        self.parser = argparse.ArgumentParser(
            prog="Jemdoc",
            description=
            "Produces html markup from a jemdoc SOURCEFILE.\n\nSee \033[96mhttp://jemdoc.jaboc.net/\033[00m for many more details."
        )
        self.parser.add_argument(
            "-s",
            "--show-config",
            dest="showConfig",
            help=
            "generates the standard configuration in a directory <configs> in the current working directory",
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
        self.parser.add_argument("-r",
                                 "--react",
                                 dest="useReact",
                                 help="compile with ReactJS",
                                 action="store_true")
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
            help=
            "output files in directory <dirname>, name of ReactJS directory when compiling with ReactJS",
            type=self._checkOutputDir)
        self.parser.add_argument("input",
                                 help="relative path to input files",
                                 type=self._checkFileExists,
                                 nargs="+")
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

    def getOutputDir(self):
        if self._args.outdir:
            return self._args.outdir
        else:
            return self._DEFAULT_OUTDIR

    def getUserConfig(self):
        return self._args.config

    def showConfig(self):
        return self._args.showConfig

    def displayConfig(self):
        print self.getStandardConfig()
        sys.exit(1)

    def showInfo(self):
        return self._args.info

    def displayInfo(self):
        """
        This function prints out system information such as python version, os, if there is equation support or not
        """
        print 'Platform: ' + sys.platform + '.'
        print 'Python: {}, located at {}.'.format(sys.version[:5],
                                                  sys.executable)
        sys.exit(1)

    def useReact(self):
        return self._args.useReact

    def _install(self, package):
        try:
            print "Installing %s" % package
            subprocess.check_output(
                [sys.executable, "-m", "pip2", "-q", "install", package])
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
        self._engine = engineName
        return engineName

    def installCssEngine(self):
        engine = self._args.cssEngine
        if engine == "less":
            self._install("lesscpy")
            self._engine = "lesscpy"
        elif engine == "sass" or engine == "scss":
            self._install("libsass")
            self._engine = "pysassc"

    def getCssEngine(self):
        return self._engine

    def getCssStyle(self):
        return self._args.cssEngine.lower()

    @staticmethod
    def compileToCss(self, engine, inputfile, outputfile):
        if not os.path.exists(inputfile):
            print "\033[91mWarn\033[00m: %s does not exist in current directory, cannot be used!"
            return False

        try:
            out = os.path.join(os.getcwd(), outputfile)
            cmd = "{} {} {}".format(engine, inputfile, out)
            out = subprocess.check_output(cmd, shell=True)
            return True
        except subprocess.CalledProcessError as ex:
            print "\033[91mWarn\033[00m: {}".format(str(ex).lower())
            sys.exit(1)

    def _checkFileExists(self, file):
        if not os.path.exists(file):
            raise argparse.ArgumentTypeError(
                "file '{}' does not exists in current directory".format(file))
        elif not os.path.isfile(file):
            raise argparse.ArgumentTypeError(
                "{} is a directory and not a file. Please provide a file".
                format(file))
        return str(file)

    @staticmethod
    def getStandardConfig(self, toFile=False):
        standardConfig = """[firstbit]
  <!doctype html>
  <html lang="en">
  <head>
  <meta charset="utf-8">
  <meta name="generator" content="jemdoc, see http://jemdoc.jaboc.net/" />
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    tex2jax: {
      inlineMath: [['$','$'], ['\\(','$\\)']],
      displayMath: [['$$','$$'], ['$\\[','$\\]']]
    },
    TeX: { 
      extensions: ["AMScd.js", "action.js", "autobold.js", "cancel.js", "begingroup.js", "color.js", "enclose.js"] 
    }
  });
  </script>
  <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML"></script>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
  
  [defaultcss]
  <link rel="stylesheet" href="jemdoc.css" type="text/css" />
  
  [windowtitle]
  # used in header for window title.
  <title>|</title>

  [fwtitlestart]
  <div class="jumbotron text-center" id="fwtitle">

  [fwtitleend]
  </div>

  [nav]
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
  <a class="navbar-brand" href="#">Navbar</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
    <div class="navbar-nav">
      <a class="nav-item nav-link active" href="#">Home <span class="sr-only">(current)</span></a>
      <a class="nav-item nav-link" href="#">Features</a>
      <a class="nav-item nav-link" href="#">Pricing</a>
      <a class="nav-item nav-link disabled" href="#">Disabled</a>
    </div>
  </div>
  </nav>
  
  [nonav]
  <div class="title-divider"></div>

  [doctitle]
  # used at top of document.
  <div class="toptitle">
  <h1>|</h1>
  
  [subtitle]
  <h2 id="subtitle">|</h2>
  
  [doctitleend]
  </div>
  
  [bodystart]
  </head>
  <body>
  
  [analytics]
  <script type="text/javascript">
  var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
  document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
  </script>
  <script type="text/javascript">
  try {
      var pageTracker = _gat._getTracker("|");
      pageTracker._trackPageview();
  } catch(err) {}</script>
  
  [menustart]
  <main class="container" id="tlayout">
  <div class="row">
  <!-- Side menu -->
  <aside class="col-12 col-md-3" id="sidemenu">
  <ul class="nav nav-pills flex-column">
  
  [menuend]
  </ul>
  </aside>
  <div class="col-12 col-md-9" id="main-content">
  
  [menucategory]
  <div class="menu-category">|</div>

  [menuitem]
  <li class="nav-item menu-item"><a href="|1" class="nav-link">|2</a></li>

  [specificcss]
  <link rel="stylesheet" href="|" type="text/css" />

  [specificjs]
  <script src="|.js" type="text/javascript"></script>
  
  [currentmenuitem]
  <li class="nav-item menu-item"><a href="|1" class="nav-link active">|2</a></li>
  
  [nomenu]
  <div id="main-content">
  
  [menulastbit]
  <!-- End of main body -->
  </div>
  </div>
  </main>
  
  [nomenulastbit]
  </div>
  
  [bodyend]
  <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
  </body>
  </html>
  
  [infoblock]
  <div class="infoblock">
  
  [codeblock]
  <div class="codeblock">
  
  [blocktitle]
  <div class="blocktitle">|</div>
  
  [infoblockcontent]
  <div class="blockcontent">
  
  [codeblockcontent]
  <div class="blockcontent"><pre>
  
  [codeblockend]
  </pre></div></div>
  
  [codeblockcontenttt]
  <div class="blockcontent"><tt class="tthl">
  
  [codeblockendtt]
  </tt></div></div>
  
  [infoblockend]
  </div></div>
  
  [footerstart]
  <footer class="jumbotron" id="footer">
  <div id="footer footer-text">
  
  [footerend]
  </div>
  </footer>
  
  [lastupdated]
  Page generated |, by <a href="http://jemdoc.jaboc.net/">jemdoc</a>.

  [formstart]
  <form method="|1" action="|2">

  [inputtext]
  <input type="text" name="|1" |2>

  [inputpassword]
  <input type="password" name="|1" |2>

  [inputemail]
  <input type="email" name="|1" |2>

  [inputnumber] 
  <input type="number" name="|1" |2>

  [inputsubmit]
  <input type="submit">

  [formend]
  </form>

  [videostart]
  <video width="|1" height="|2" |3>

  [videosource]
  <source src="|1" type="video/|2">

  [videoend]
  </video>

  [audiostart]
  <audio |1>

  [audiosource]
  <source src="|1" type="audio/|2">

  [audioend]
  </audio>

  [sourcelink]
  (<a href="|">source</a>)

  """
        if toFile:
            configDir = os.path.join(os.getcwd(), "configs")
            if not os.path.exists(configDir):
                os.mkdir(configDir)

            filename = "standardconf.config"
            filepath = os.path.join(configDir, filename)
            file = open(filepath, "w")
            for line in standardConfig.splitlines(True):
                if line.startswith('  '):
                    file.write(line[2:])
                else:
                    file.write(line)
            file.flush()
            file.close()

        return standardConfig


if __name__ == "__main__":
    parser = CommandLineParser()
    args = parser.getArgs()
    if (args.info):
        print("Info...")
    if (args.showConfig):
        print("Show Config...")
    print "Use React: {}".format(args.useReact)
    print "User Config file: {}".format(args.config)
    print "Outdir: {}".format(args.outdir)
    print "Innames: {}".format(args.input)
    print "CSS Engine: {}".format(args.cssEngine)

# TODO: Build man page