from cli.commandlineparser import CommandLineParser
from cli.defaultconfig import DefaultConfig
from control.controlstruct import ControlStruct
from control.jandal import JandalError

from parser import *

def main():
    defaultConfig = DefaultConfig()
    cliparser = CommandLineParser()
    if cliparser.showConfig():
        cliparser.downloadStandardConfig()

    if cliparser.showInfo():
        cliparser.displayInfo()

    # cliparser.installCssEngine()
    cssEngine = cliparser.getCssEngine()

    confnames = []
    innames = cliparser.getInputFiles()
    outdirname = cliparser.getOutputDir()
    if cliparser.getUserConfig():
        confnames.append(cliparser.getUserConfig())

    if not innames and not cliparser.showInfo() and not cliparser.showConfig():
        raise RuntimeError("Error: no input files provided...")

    conf = parseconf(confnames, defaultConfig)  # this function parses the configuration filenames in the list and returns config files

    # TODO: verify this, might not need this
    # if outdirname is not None: 
    #   if not os.path.isdir(outdirname) and len(innames) > 1:
    #     raise RuntimeError('cannot handle one outfile with multiple infiles')

    # for each input file, format the corresponding output file
    for inname in innames:
        filename = re.sub(r'.jemdoc$', '', inname) + '.html'
        if outdirname is None:
            outdirname = '.'
            outfile = filename
        elif os.path.isdir(outdirname):
            # if directory, prepend directory to automatically generated name.
            outfile = os.path.join(outdirname, filename)
        # else:
        #     outfile = outdirname

        infile = open(inname, 'rUb')
        outfile = open(outfile, 'w')

        # create a control struct with the necessary parsed configuration
        print "Processing \033[96m%s...\033[00m" % inname
        f = ControlStruct(infile, outfile, conf, inname, outdirname)
        procfile(f, cliparser)


# main
if __name__ == '__main__':
    main()
