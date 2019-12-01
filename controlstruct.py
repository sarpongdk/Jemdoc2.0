"""
This class is a control sturct class for convenience. It's a wrapper around the input and output files
"""


class ControlStruct(object):
    def __init__(self, infile, outfile=None, conf=None, inname=None):
        self.inname = inname
        self.inf = infile
        self.outf = outfile
        self.conf = conf
        self.linenum = 0
        self.otherfiles = []
        self.texlines = []
        self.analytics = None
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


class JandalError(Exception):
    pass
