"""
This class is a control sturct class for convenience. It's a wrapper around the input and output files
"""
class ControlStruct(object):
  def __init__(self, infile, outfile=None, conf=None, inname=None, eqs=True,
         eqdir='eqs', eqdpi=130):
    self.inname = inname #
    self.inf = infile # input file
    self.outf = outfile # output file: filename or fileobj?
    self.conf = conf # configuration file: filename or fileobj?
    self.linenum = 0
    self.otherfiles = []
    self.eqs = eqs # equations support: boolean
    self.eqdir = eqdir # equations directory
    self.eqdpi = eqdpi
    # Default to supporting equations until we know otherwise.
    self.eqsupport = True
    self.eqcache = True
    self.eqpackages = []
    self.texlines = []
    self.analytics = None
    self.eqbd = {} # equation base depth.
    self.baseline = None

  def pushfile(self, newfile):
    """
    This function updates which file is self.inf
    Treats self.otherfiles as a stack with [0] being top
    """
    self.otherfiles.insert(0, self.inf)
    self.inf = open(newfile, 'rb')

  def nextfile(self):
    self.inf.close()
    self.inf = self.otherfiles.pop(0)