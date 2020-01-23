#!/usr/bin/env python2

import sys
import os
import re
import time
import StringIO
import subprocess # was from subprocess import *
import tempfile

from cli.commandlineparser import CommandLineParser
from control.controlstruct import ControlStruct
from control.jandal import JandalError
from styling.style import Style

def raisejandal(msg, line=0):
    if line == 0:
        s = "%s" % msg
    else:
        s = "line %d: %s" % (line, msg)
    raise JandalError(s)


def readnoncomment(f):
    l = f.readline()
    if l == '':
        return l
    elif l[0] == '#':
        return readnoncomment(f)  # read next line if current line is a comment
    else:
        return l.rstrip() + '\n'  # leave just one \n and no spaces etc.


def parseconf(cns, defaultConfig):
    syntax = {}
    warn = False
    # manually add the defaults as a file handle.
    standardconf = defaultConfig.getStandardConfig()
    fs = [ StringIO.StringIO(standardconf) ]  # fs represents all the configuration files, including the default configuration file, as file objects
    for sname in cns:
        fs.append(open(sname, 'rb'))  # opens each configuration file and appends the file object to fs

    for f in fs:  # for each file object in fs
        # ControlStruct(fileObj) wraps fileObj in ControlStruct class
        # getNextCharacter is a method
        while getNextCharacter(ControlStruct(f)) != '':
            l = readnoncomment(f)
            r = re.match(r'\[(.*)\]\n', l)

            if r:
                tag = r.group(1)

                s = ''
                l = readnoncomment(f)
                while l not in ('\n', ''):
                    s += l
                    l = readnoncomment(f)

                syntax[tag] = s

        f.close()

    return syntax


def insertmenuitems(f, mname, current, prefix):
    """
  This function inserts menu items into the output html
  
  mname is the name of the menu file
  current is the 
  prefix is the
  f is the ControlStruct wrapper class that decorates the output file object
  """
    m = open(mname, 'rb')
    while getNextCharacter(ControlStruct(m)) != '':
        l = readnoncomment(m)
        l = l.strip()
        if l == '':
            continue

        r = re.match(r'\s*(.*?)\s*\[(.*)\]',
                     l)  # this matches: one or more spaces followed by

        if r:  # then we have a menu item.
            link = r.group(2)
            #print link
            # Don't use prefix if we have an absolute link.
            if '://' not in r.group(2):
                link = prefix + allreplace(link)

            # replace spaces with nbsps.
            # do do this, even though css would make it work - ie ignores.
            # only replace spaces that aren't in {{ blocks.
            in_quote = False
            menuitem = ""
            for group in re.split(r'({{|}})', r.group(1)):
                if in_quote:
                    if group == '}}':
                        in_quote = False
                        next
                    else:
                        menuitem += group
                else:
                    if group == '{{':
                        in_quote = True
                        next
                    else:
                        menuitem += br(re.sub(r'(?<!\\n) +', '~', group), f)

            if link[-len(current):] == current:
                hb(f.outf, f.conf['currentmenuitem'], link, menuitem)
            else:
                hb(f.outf, f.conf['menuitem'], link, menuitem)

        else:  # menu category.
            hb(f.outf, f.conf['menucategory'], br(l, f))

    m.close()


def out(f, s):
    f.write(s)


def hb(f, tag, content1, content2=None):
    """Writes out a halfblock (hb)."""

    if content1 is None:
        content1 = ""

    if content2 is None:
        out(f, re.sub(r'\|', content1, tag))
    else:
        r = re.sub(r'\|1', content1, tag)
        r = re.sub(r'\|2', content2, r)
        out(f, r)


def getNextCharacter(f, ditchcomments=True):
    """Peeks at next character in the file."""
    # Should only be used to look at the first character of a new line.
    c = f.inf.read(1)  # reads first charactor of input file
    if c:  # only undo forward movement if we're not at the end.
        #
        # if character c is comment symbol and ditchComments is True, read next line with getNextLine(f)
        if ditchcomments and c == '#':
            l = getNextLine(f)  # reads next line
            if doincludes(
                    f, l
            ):  # doincludes(fileObj, line) is a method described below. Checks if user is including external file
                return "#"

        if c in ' \t':
            return getNextCharacter(f)

        if c == '\\':
            c += getNextCharacter(f)

        f.inf.seek(-1, 1)
    elif f.otherfiles:
        f.nextfile()
        return getNextCharacter(f, ditchcomments)

    return c


def doincludes(f, l):
    """
  Input: f = fileObject, l = line
  This method includes jemdoc file that is included using the syntax include{filename} or includeraw{filename}
  includeraw does not jemdoc parsing
  include parses with jemdoc rules
  
  Returns boolean on completion, False if nothing has been included
  """
    ir = 'includeraw{'
    i = 'include{'
    if l.startswith(ir):  # if line starts with includeraw{
        nf = open(l[len(ir):-2], 'rb')
        rawHTML = nf.read()
        f.outf.write(
            rawHTML)  # write the contents of includeraw to the outputfile
        nf.close()
    elif l.startswith(i):  # if line starts with include{
        f.pushfile(
            l[len(i):-2]
        )  # switches which file is currently being parsed. makes the include{file} the one to be parsed
    else:
        return False

    return True


def getNextLine(f, withcount=False, codemode=False):
    """Get input file line."""
    """
  This method extracts the next line from the current file. If that file has no extra lines
  It switches to the next file
  """
    s = f.inf.readline()
    if not s and f.otherfiles:  # if current file has no lines left and there are other files
        f.nextfile()  # switch files
        return getNextLine(f, withcount, codemode)  # perform same algorithm on it

    f.linenum += 1

    if not codemode:
        # remove any special characters - assume they were checked by getNextCharacter()
        # before we got here.
        # remove any trailing comments.
        s = s.lstrip(' \t')
        s = re.sub(r'\s*(?<!\\)#.*', '', s)

    if withcount:
        if s[0] == '.':
            m = r'\.'
        else:
            m = s[0]

        r = re.match('(%s+) ' % m, s)
        if not r:
            raise SyntaxError("couldn't handle the jandal (code 12039) on line%d" % f.linenum)

        if not codemode:
            s = s.lstrip('-.=:')

        return (s, len(r.group(1)))
    else:
        if not codemode:
            s = s.lstrip('-.=:')

        return s


def nextParagraph(f, withcount=False, eatblanks=True):
    """Gets the next paragraph from the input file."""
    # New paragraph markers signalled by characters in following tuple.
    if withcount:
        (s, c) = getNextLine(f, withcount)
    else:
        s = getNextLine(f)

    while getNextCharacter(f) not in ('\n', '-', '.', ':', '', '=', '~', '{', '\\(', '\\)'):
        s += getNextLine(f)

    while eatblanks and getNextCharacter(f) == '\n':
        getNextLine(f)  # burn blank line.

    # in both cases, ditch the trailing \n.
    if withcount:
        return (s[:-1], c)
    else:
        return s[:-1]


def quote(s):
    """
  Input: string s
   This method escapes wildcards and reserved characters in the string s and returns it
   
  Return: escaped string s
  """
    return re.sub(r"""[\\*/+"'<>&$%\.~[\]-]""", r'\\\g<0>', s)


def replacequoted(b):
    """Quotes {{raw html}} sections."""
    """This method extracts the html within {{html text}} and returns that html text. HTML text will be escaped/sanitized as well"""
    r = re.compile(r'\{\{(.*?)\}\}', re.M + re.S)
    m = r.search(b)
    while m:
        qb = quote(m.group(1))

        b = b[:m.start()] + qb + b[m.end():]

        m = r.search(b, m.start())

    return b


def replacepercents(b):
    # replace %sections% as +{{sections}}+. Do not replace if within a link.

    r = re.compile(r'(?<!\\)%(.*?)(?<!\\)%', re.M + re.S)
    m = r.search(b)
    while m:
        #qb = '+' + quote(m.group(1)) + '+'
        a = re.sub(r'\[', r'BSNOTLINKLEFT12039XX', m.group(1))
        a = re.sub(r'\]', r'BSNOTLINKRIGHT12039XX', a)
        qb = '+{{' + a + '}}+'

        b = b[:m.start()] + qb + b[m.end():]

        m = r.search(b, m.start())

    return b

def replaceimages(b):
    # works with [img{width}{height}{alttext} location caption].
    r = re.compile(r'(?<!\\)\[img(\.[A-Za-z0-9]+)?(#[A-Za-z0-9]+)?((?:\{.*?\}){,3})\s(.*?)(?:\s(.*?))?(?<!\\)\]', re.M + re.S)
    m = r.search(b)
    s = re.compile(r'{(.*?)}', re.M + re.S)
    while m:
        imgClass = m.group(1)
        imgId = m.group(2)
        if imgClass:
            imgClass = imgClass[1:]

        if imgId:
            imgId = imgId[1:]

        m1 = list(s.findall(m.group(3)))
        m1 += [''] * (3 - len(m1))

        bits = []
        link = m.group(4).strip()
        bits.append(r'src=\"%s\"' % quote(link))

        if m1[0]:
            if m1[0].isdigit():
                s = m1[0] + 'px'
            else:
                s = m1[0]
            bits.append(r'width=\"%s\"' % quote(s))
        if m1[1]:
            if m1[1].isdigit():
                s = m1[1] + 'px'
            else:
                s = m1[1]
            bits.append(r'height=\"%s\"' % quote(s))
        if m1[2]:
            bits.append(r'alt=\"%s\"' % quote(m1[2]))
        else:
            bits.append(r'alt=\"\"')

        b = b[:m.start()] + r'<figure><img class="img-fluid %s" id="%s" %s /></figure>' % (imgClass, imgId, " ".join(bits) + b[m.end():])

        m = r.search(b, m.start())
    return b


def replacelinks(b):
    """
  This method replaces all links written in the meta language and produces the corresponding HTML anchor tag
  with the href attribute appropriately populated
  """
  # TODO: add class and id here
    # works with [link.html new link style].
    r = re.compile(r'(?<!\\)\[(.*?)(?:\s(.*?))?(?<!\\)\](\.[A-Za-z0-9]+)?(#[A-Za-z0-9]+)?', re.M + re.S)
    m = r.search(b)

    while m:
        m1 = m.group(1).strip()
        anchorClass = m.group(3).strip() if m.group(3) else None
        anchorId = m.group(4).strip() if m.group(4) else None

        if anchorClass:
            anchorClass = anchorClass[1:]
        
        if anchorId:
            anchorId = anchorId[1:]

        if '@' in m1 and not m1.startswith('mailto:') and not m1.startswith('http://'):
            link = 'mailto:' + m1
        else:
            link = m1

        # first unquote any hashes (e.g. for in-page links).
        link = re.sub(r'\\#', '#', link)

        # remove any +{{ or }}+ links.
        link = re.sub(r'(\+\{\{|\}\}\+)', r'%', link)

        link = quote(link)

        if m.group(2):
            linkname = m.group(2).strip()
        else:
            # remove any mailto before labelling.
            linkname = re.sub('^mailto:', '', link)

        aId = ''
        if anchorId:
            aId = 'id="%s"' % anchorId

        aClass = ''
        if anchorClass:
            aClass = 'class="%s"' % anchorClass


        b = b[:m.start()] + r'<a href=\"%s\" %s %s>%s<\/a>' % (link, aId, aClass, linkname) + b[m.end():]

        m = r.search(b, m.start())

    return b


def br(b, f, tableblock=False):
    """Does simple text replacements on a block of text. ('block replacements')"""

    # Deal with environment variables (say, for Michael Grant).
    r = re.compile(r"!\$(\w{2,})\$!", re.M + re.S)

    for m in r.findall(b):
        repl = os.environ.get(m)
        if repl == None:
            b = re.sub("!\$%s\$!" % m, 'FAILED_MATCH_' + m, b)
        else:
            b = re.sub("!\$%s\$!" % m, repl, b)

    b = re.sub(r'\\\\', 'jemLITerl33talBS', b)

    # Deal with {{html embedding}}.
    b = replacequoted(b)

    b = allreplace(b)

    b = b.lstrip('-. \t')  # remove leading spaces, tabs, dashes, dots.
    b = replaceimages(b)  # jem not sure if this is still used.

    # Slightly nasty hackery in this next bit.
    b = replacepercents(b)
    b = replacelinks(b)
    b = re.sub(r'BSNOTLINKLEFT12039XX', r'[', b)
    b = re.sub(r'BSNOTLINKRIGHT12039XX', r']', b)
    b = replacequoted(b)

    # Deal with /italics/ first because the '/' in other tags would otherwise
    # interfere.
    r = re.compile(r'(?<!\\)/(.*?)(?<!\\)/', re.M + re.S)
    b = re.sub(r, r'<em>\1</em>', b)

    # Deal with *bold*.
    r = re.compile(r'(?<!\\)\*(.*?)(?<!\\)\*', re.M + re.S)
    b = re.sub(r, r'<strong>\1</strong>', b)

    # Deal with +monospace+.
    r = re.compile(r'(?<!\\)\+(.*?)(?<!\\)\+', re.M + re.S)
    b = re.sub(r, r'<tt>\1</tt>', b)

    # Deal with "double quotes".
    r = re.compile(r'(?<!\\)"(.*?)(?<!\\)"', re.M + re.S)
    b = re.sub(r, r'&ldquo;\1&rdquo;', b)

    # Deal with left quote `.
    r = re.compile(r"(?<!\\)`", re.M + re.S)
    b = re.sub(r, r'&lsquo;', b)

    # Deal with apostrophe '.
    # Add an assertion that the next character's not a letter, to deal with
    # apostrophes properly.
    r = re.compile(r"(?<!\\)'(?![a-zA-Z])", re.M + re.S)
    b = re.sub(r, r'&rsquo;', b)

    # Deal with em dash ---.
    r = re.compile(r"(?<!\\)---", re.M + re.S)
    b = re.sub(r, r'&#8201;&mdash;&#8201;', b)

    # Deal with en dash --.
    r = re.compile(r"(?<!\\)--", re.M + re.S)
    b = re.sub(r, r'&ndash;', b)

    # Deal with ellipsis ....
    r = re.compile(r"(?<!\\)\.\.\.", re.M + re.S)
    b = re.sub(r, r'&hellip;', b)

    # Deal with non-breaking space ~.
    r = re.compile(r"(?<!\\)~", re.M + re.S)
    b = re.sub(r, r'&nbsp;', b)

    # Deal with registered trademark \R.
    r = re.compile(r"(?<!\\)\\R", re.M + re.S)
    b = re.sub(r, r'&reg;', b)

    # Deal with copyright \C.
    r = re.compile(r"(?<!\\)\\C", re.M + re.S)
    b = re.sub(r, r'&copy;', b)

    # Deal with middot \M.
    r = re.compile(r"(?<!\\)\\M", re.M + re.S)
    b = re.sub(r, r'&middot;', b)

    # Deal with line break.
    r = re.compile(r"(?<!\\)\\n", re.M + re.S)
    b = re.sub(r, r'<br />', b)

    # Deal with paragraph break. Caution! Should only use when we're already in
    # a paragraph.
    r = re.compile(r"(?<!\\)\\p", re.M + re.S)
    b = re.sub(r, r'</p><p>', b)

    if tableblock:
        # Deal with ||, meaning </td></tr><tr><td>
        r = re.compile(r"(?<!\\)\|\|", re.M + re.S)
        f.tablecol = 2
        bcopy = b
        b = ""
        r2 = re.compile(r"(?<!\\)\|", re.M + re.S)
        for l in bcopy.splitlines():
            f.tablerow += 1
            l = re.sub(r, r'</td></tr>\n<tr class="r%d"><td class="c1">' \
                  % f.tablerow, l)

            l2 = ''
            col = 2
            r2s = r2.split(l)
            for x in r2s[:-1]:
                l2 += x + ('</td><td class="c%d">' % col)
                col += 1
            l2 += r2s[-1]

            b += l2

    # Second to last, remove any remaining quoting backslashes.
    b = re.sub(r'\\(?!\\)', '', b)

    # Deal with literal backspaces.
    b = re.sub('jemLITerl33talBS', r'\\', b)

    # Also fix up DOUBLEOPEN and DOUBLECLOSEBRACES.
    b = re.sub('DOUBLEOPENBRACE', '{{', b)
    b = re.sub('DOUBLECLOSEBRACE', '}}', b)

    return b


def allreplace(b):
    """Replacements that should be done on everything."""
    """
  Input: string b
  Return: escaped ampersand, less than and greater than symbols
  """
    # escaping/replacing & with amp
    r = re.compile(r"(?<!\\)&", re.M + re.S)
    b = re.sub(r, r'&amp;', b)

    # escaping/replacing greater than
    r = re.compile(r"(?<!\\)>", re.M + re.S)
    b = re.sub(r, r'&gt;', b)

    # escaping/replacing less than
    r = re.compile(r"(?<!\\)<", re.M + re.S)
    b = re.sub(r, r'&lt;', b)

    return b


def pyint(f, l):
    l = l.rstrip()
    l = allreplace(l)

    r = re.compile(r'(#.*)')
    l = r.sub(r'<span class = "comment">\1</span>', l)

    if l.startswith('&gt;&gt;&gt;'):
        hb(f, '<span class="pycommand">|</span>\n', l)
    else:
        out(f, l + '\n')


def putbsbs(l):
    for i in range(len(l)):
        l[i] = '\\b' + l[i] + '\\b'

    return l


def gethl(lang):
    # disable comments by default, by choosing unlikely regex.
    d = {'strings': False}
    if lang in ('py', 'python'):
        d['statement'] = [
            'break', 'continue', 'del', 'except', 'exec', 'finally', 'pass',
            'print', 'raise', 'return', 'try', 'with', 'global', 'assert',
            'lambda', 'yield', 'def', 'class', 'for', 'while', 'if', 'elif',
            'else', 'import', 'from', 'as', 'assert'
        ]
        d['builtin'] = [
            'True', 'False', 'set', 'open', 'frozenset', 'enumerate', 'object',
            'hasattr', 'getattr', 'filter', 'eval', 'zip', 'vars', 'unicode',
            'type', 'str', 'repr', 'round', 'range', 'and', 'in', 'is', 'not',
            'or'
        ]
        d['special'] = [
            'cols', 'optvar', 'param', 'problem', 'norm2', 'norm1', 'value',
            'minimize', 'maximize', 'rows', 'rand', 'randn', 'printval',
            'matrix'
        ]
        d['error'] = [
            '\w*Error',
        ]
        d['commentuntilend'] = '#'
        d['strings'] = True
    elif lang in ['c', 'c++', 'cpp']:
        d['statement'] = ['if', 'else', 'printf', 'return', 'for']
        d['builtin'] = [
            'static', 'typedef', 'int', 'float', 'double', 'void', 'clock_t',
            'struct', 'long', 'extern', 'char'
        ]
        d['operator'] = [
            '#include.*', '#define', '@pyval{', '}@', '@pyif{', '@py{'
        ]
        d['error'] = [
            '\w*Error',
        ]
        d['commentuntilend'] = ['//', '/*', ' * ', '*/']
    elif lang in ('rb', 'ruby'):
        d['statement'] = putbsbs([
            'while', 'until', 'unless', 'if', 'elsif', 'when', 'then', 'else',
            'end', 'begin', 'rescue', 'class', 'def'
        ])
        d['operator'] = putbsbs(['and', 'not', 'or'])
        d['builtin'] = putbsbs(['true', 'false', 'require', 'warn'])
        d['special'] = putbsbs(['IO'])
        d['error'] = putbsbs([
            '\w*Error',
        ])
        d['commentuntilend'] = '#'
        d['strings'] = True
        d['strings'] = True
        if lang in ['c++', 'cpp']:
            d['builtin'] += ['bool', 'virtual']
            d['statement'] += ['new', 'delete']
            d['operator'] += ['&lt;&lt;', '&gt;&gt;']
            d['special'] = [
                'public', 'private', 'protected', 'template', 'ASSERT'
            ]
    elif lang == 'sh':
        d['statement'] = [
            'cd',
            'ls',
            'sudo',
            'cat',
            'alias',
            'for',
            'do',
            'done',
            'in',
        ]
        d['operator'] = [
            '&gt;', r'\\', r'\|', ';', '2&gt;', 'monolith&gt;', 'kiwi&gt;',
            'ant&gt;', 'kakapo&gt;', 'client&gt;'
        ]
        d['builtin'] = putbsbs([
            'gem', 'gcc', 'python', 'curl', 'wget', 'ssh', 'latex', 'find',
            'sed', 'gs', 'grep', 'tee', 'gzip', 'killall', 'echo', 'touch',
            'ifconfig', 'git', '(?<!\.)tar(?!\.)'
        ])
        d['commentuntilend'] = '#'
        d['strings'] = True
    elif lang == 'matlab':
        d['statement'] = putbsbs([
            'max', 'min', 'find', 'rand', 'cumsum', 'randn', 'help', 'error',
            'if', 'end', 'for'
        ])
        d['operator'] = ['&gt;', 'ans =', '>>', '~', '\.\.\.']
        d['builtin'] = putbsbs(['csolve'])
        d['commentuntilend'] = '%'
        d['strings'] = True
    elif lang == 'commented':
        d['commentuntilend'] = '#'

    # Add bsbs (whatever those are).
    for x in ['statement', 'builtin', 'special', 'error']:
        if x in d:
            d[x] = putbsbs(d[x])

    return d


def language(f, l, hl):
    l = l.rstrip()
    l = allreplace(l)
    # handle strings.
    if hl['strings']:
        r = re.compile(r'(".*?")')
        l = r.sub(r'<span CLCLclass="string">\1</span>', l)
        r = re.compile(r"('.*?')")
        l = r.sub(r'<span CLCLclass="string">\1</span>', l)

    if 'statement' in hl:
        r = re.compile('(' + '|'.join(hl['statement']) + ')')
        l = r.sub(r'<span class="statement">\1</span>', l)

    if 'operator' in hl:
        r = re.compile('(' + '|'.join(hl['operator']) + ')')
        l = r.sub(r'<span class="operator">\1</span>', l)

    if 'builtin' in hl:
        r = re.compile('(' + '|'.join(hl['builtin']) + ')')
        l = r.sub(r'<span class="builtin">\1</span>', l)

    if 'special' in hl:
        r = re.compile('(' + '|'.join(hl['special']) + ')')
        l = r.sub(r'<span class="special">\1</span>', l)

    if 'error' in hl:
        r = re.compile('(' + '|'.join(hl['error']) + ')')
        l = r.sub(r'<span class="error">\1</span>', l)

    l = re.sub('CLCLclass', 'class', l)

    if 'commentuntilend' in hl:
        cue = hl['commentuntilend']
        if isinstance(cue, (list, tuple)):
            for x in cue:
                if l.strip().startswith(x):
                    hb(f, '<span class="comment">|</span>\n', allreplace(l))
                    return
                if '//' in cue:  # Handle this separately.
                    r = re.compile(r'\/\/.*')
                    l = r.sub(r'<span class="comment">\g<0></span>', l)
        elif cue == '#':  # Handle this separately.
            r = re.compile(r'#.*')
            l = r.sub(r'<span class="comment">\g<0></span>', l)
        elif cue == '%':  # Handle this separately.
            r = re.compile(r'%.*')
            l = r.sub(r'<span class="comment">\g<0></span>', l)
        elif l.strip().startswith(cue):
            hb(f, '<span class="comment">|</span>\n', allreplace(l))
            return

    out(f, l + '\n')

def dashlist(f, ordered=False):
    level = 0

    if ordered:
        char = '.'
        ul = 'ol'
    else:
        char = '-'
        ul = 'ul'

    while getNextCharacter(f) == char:
        (s, newlevel) = nextParagraph(f, True, False)

        # first adjust list number as appropriate.
        if newlevel > level:
            for i in range(newlevel - level):
                if newlevel > 1:
                    out(f.outf, '\n')
                out(f.outf, '<%s>\n<li>' % ul)
        elif newlevel < level:
            out(f.outf, '\n</li>')
            for i in range(level - newlevel):
                #out(f.outf, '</li>\n</%s>\n</li><li>' % ul)
                # demote means place '</ul></li>' in the file.
                out(f.outf, '</%s>\n</li>' % ul)
            #out(f.outf, '\n<li>')
            out(f.outf, '\n<li>')
        else:
            # same level, make a new list item.
            out(f.outf, '\n</li>\n<li>')

        out(f.outf, '<p>' + br(s, f) + '</p>')
        level = newlevel

    for i in range(level):
        out(f.outf, '\n</li>\n</%s>\n' % ul)


def colonlist(f):
    out(f.outf, '<dl>\n')
    while getNextCharacter(f) == ':':
        s = nextParagraph(f, eatblanks=False)
        r = re.compile(r'\s*{(.*?)(?<!\\)}(.*)', re.M + re.S)
        g = re.match(r, s)

        if not g or len(g.groups()) != 2:
            raise SyntaxError("couldn't handle the jandal (invalid deflist "
                              "format) on line %d" % f.linenum)
        # split into definition / non-definition part.
        defpart = g.group(1)
        rest = g.group(2)

        hb(f.outf, '<dt>|</dt>\n', br(defpart, f))
        hb(f.outf, '<dd><p>|</p></dd>\n', br(rest, f))

    out(f.outf, '</dl>\n')


def codeblock(f, g):
    # TODO: give users the ability to add class and id
    if g[1] == 'raw':
        raw = True
        ext_prog = None
    elif g[0] == 'filter_through':
        # Filter through external program.
        raw = False
        ext_prog = g[1]
        buff = ""
    else:
        ext_prog = None
        raw = False
        out(f.outf, f.conf['codeblock'])
        if g[0]:
            hb(f.outf, f.conf['blocktitle'], g[0])
        if g[1] == 'jemdoc':
            out(f.outf, f.conf['codeblockcontenttt'])
        else:
            out(f.outf, f.conf['codeblockcontent'])

    # Now we are handling code.
    # Handle \~ and ~ differently.
    stringmode = False
    while 1:  # wait for EOF.
        l = getNextLine(f, codemode=True)
        if not l:
            break
        elif l.startswith('~'):
            break
        elif l.startswith('\\~'):
            l = l[1:]
        elif l.startswith('\\{'):
            l = l[1:]
        elif ext_prog:
            buff += l
            continue
        elif stringmode:
            if l.rstrip().endswith('"""'):
                out(f.outf, l + '</span>')
                stringmode = False
            else:
                out(f.outf, l)
            continue

        # jem revise pyint out of the picture.
        if g[1] == 'pyint':
            pyint(f.outf, l)
        else:
            if raw:
                out(f.outf, l)
            elif g[1] == 'jemdoc':
                # doing this more nicely needs python 2.5.
                for x in ('#', '~', '>>>', '\~', '{'):
                    if str(l).lstrip().startswith(x):
                        out(f.outf, '</tt><pre class="tthl">')
                        out(f.outf, l + '</pre><tt class="tthl">')
                        break
                else:
                    for x in (':', '.', '-'):
                        if str(l).lstrip().startswith(x):
                            out(f.outf, '<br />' + prependnbsps(l))
                            break
                    else:
                        if str(l).lstrip().startswith('='):
                            out(f.outf, prependnbsps(l) + '<br />')
                        else:
                            out(f.outf, l)
            else:
                if l.startswith('\\#include{') or l.startswith(
                        '\\#includeraw{'):
                    out(f.outf, l[1:])
                elif l.startswith('#') and doincludes(f, l[1:]):
                    continue
                elif g[1] in ('python', 'py') and l.strip().startswith('"""'):
                    out(f.outf, '<span class="string">' + l)
                    stringmode = True
                else:
                    language(f.outf, l, gethl(g[1]))

    if raw:
        return
    elif ext_prog:
        print 'filtering through %s...' % ext_prog

        output, _ = subprocess.Popen(ext_prog, shell=True, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE).communicate(buff)
        out(f.outf, output)
    else:
        if g[1] == 'jemdoc':
            out(f.outf, f.conf['codeblockendtt'])
        else:
            out(f.outf, f.conf['codeblockend'])


def prependnbsps(l):
    g = re.search('(^ *)(.*)', l).groups()
    return g[0].replace(' ', '&nbsp;') + g[1]


def inserttitle(f, t):
    # TODO: give users the ability to add id and class
    if t is not None:
        hb(f.outf, f.conf['doctitle'], t)

        # Look for a subtitle.
        if getNextCharacter(f) != '\n':
            hb(f.outf, f.conf['subtitle'], br(nextParagraph(f), f))

        hb(f.outf, f.conf['doctitleend'], t)


def insertnavbaritems(f, mname, current, prefix):
    """
  This function inserts navbar items into the navbar html
  
  mname is the name of the menu file
  current is the 
  prefix is the
  """
    m = open(mname, 'rb')
    while getNextCharacter(ControlStruct(m)) != '':
        l = readnoncomment(m)
        l = l.strip()
        if l == '':
            continue

        r = re.match(r'\s*(.*?)\s*\[(.*)\]',
                     l)  # this matches: one or more spaces followed by

        if r:  # then we have a menu item.
            link = r.group(2)
            # Don't use prefix if we have an absolute link.
            if '://' not in r.group(2):
                link = prefix + allreplace(link)

            # replace spaces with nbsps.
            # do do this, even though css would make it work - ie ignores.
            # only replace spaces that aren't in {{ blocks.
            in_quote = False
            navitem = ""
            for group in re.split(r'({{|}})', r.group(1)):
                if in_quote:
                    if group == '}}':
                        in_quote = False
                        next
                    else:
                        navitem += group
                else:
                    if group == '{{':
                        in_quote = True
                        next
                    else:
                        navitem += br(re.sub(r'(?<!\\n) +', '~', group), f)

            if link[-len(current):] == current:
                hb(f.outf, f.conf['currentnavitem'], link, navitem)
            else:
                hb(f.outf, f.conf['navitem'], link, navitem)
    m.close()

def procfile(f, cliparser):
    f.linenum = 0

    menu = {}
    navbar = {}
    # convert these to a dictionary.
    showfooter = True
    showsourcelink = False
    showlastupdated = True
    showlastupdatedtime = True
    nodefaultcss = False
    nav = False
    fwtitle = False
    css = []
    js = []
    title = None

    while getNextCharacter(f, False) == '#':
        l = f.inf.readline()

        f.linenum += 1
        if doincludes(f, l[1:]):
            continue
        if l.startswith('# jemdoc:'):
            l = l[len('# jemdoc:'):]
            a = l.split(',')
            # jem only handle one argument for now.
            for b in a:
                b = b.strip()
                if b.startswith('menu'):
                    sidemenu = True
                    r = re.compile(r'(\.[A-Za-z0-9]+)?(#[A-Za-z0-9]+)?(?<!\\){(.*?)(?<!\\)}', re.M + re.S)
                    g = re.findall(r, b)
                    if len(g) > 3 or len(g) < 2:
                        raise SyntaxError('sidemenu error on line %d' % f.linenum)
                    if len(g) == 2:
                        menu = {'file': f, 'menuname': g[0][2], 'page': g[1][2], 'preface': ''}
                        # menu = (f, g[0][2], g[1][2], '')
                    else:
                        menu = {'file': f, 'menuname': g[0][2], 'page': g[1][2], 'preface': g[2][2]}
                        # menu = (f, g[0][2], g[1][2], g[2][2])
                        # 'class': g[0][0], 'id': g[0][1]
                    if g[0][0]:
                        menu['class'] = g[0][0]
                    if g[0][1]:
                        menu['id'] = g[0][1]

                # TODO: setup navbar like menu
                elif b.startswith('nav'):
                    # navbar
                    nav = True
                    r = re.compile(r'(\.[A-Za-z0-9]+)?(#[A-Za-z0-9]+)?(?<!\\){(.*?)(?<!\\)}', re.M + re.S)
                    g = re.findall(r, b)
                    if len(g) > 3 or len(g) < 2:
                        raise SyntaxError('navbar error on line %d' % f.linenum)
                    if len(g) == 2:
                        navbar = {'file': f, 'navname': g[0][2], 'page': g[1][2], 'preface': ''}
                        # navbar = (f, g[0], g[1], '')
                    else:
                        navbar = {'file': f, 'navname': g[0][2], 'page': g[1][2], 'preface': g[2][2]}
                        # navbar = (f, g[0], g[1], g[2])
                    if g[0][0]:
                        navbar['class'] = g[0][0]
                    if g[0][1]:
                        navbar['id'] = g[0][1]

                elif b.startswith('nofooter'):
                    showfooter = False

                elif b.startswith('nodate'):
                    showlastupdated = False

                elif b.startswith('notime'):
                    showlastupdatedtime = False

                elif b.startswith('fwtitle'):
                    fwtitle = True
                # elif b.startswith('footerid'): # add footer id and class
                #     r = re.compile(r'')
                elif b.startswith('showsource'):
                    showsourcelink = True

                elif b.startswith('nodefaultcss'):
                    nodefaultcss = True

                elif b.startswith('addcss'):
                    r = re.compile(r'(?<!\\){(.*?)(?<!\\)}', re.M + re.S)
                    cssFiles = re.findall(r, b)  
                    css.extend(cssFiles)

                elif b.startswith('addjs'):
                    r = re.compile(r'(?<!\\){(.*?)(?<!\\)}', re.M + re.S)
                    jsFiles = re.findall(r, b)
                    js.extend(jsFiles)

                elif b.startswith('addtex'):
                    r = re.compile(r'(?<!\\){(.*?)(?<!\\)}', re.M + re.S)
                    textLines = re.findall(r, b) 
                    f.texlines += textLines

                elif b.startswith('analytics'):
                    r = re.compile(r'(?<!\\){(.*?)(?<!\\)}', re.M + re.S)
                    analytics = re.findall(r, b)[0]  
                    f.analytics = analytics

                elif b.startswith('title'):
                    r = re.compile(r'(?<!\\){(.*?)(?<!\\)}', re.M + re.S)
                    g = re.findall(r, b)
                    if len(g) != 1:
                        raise SyntaxError('addtitle error on line %d' %f.linenum)
                    title = g[0]

    # Get the file started with the firstbit.
    # writing the first bit to the output file
    out(f.outf, f.conf['firstbit'])

    # writing default css link tag to output file
    if not nodefaultcss:
        outdir = f.getOutputDir()
        Style.downloadDefaultCSS(outdir)
        out(f.outf, f.conf['defaultcss'])

    # Add per-file css lines here.
    extension = '.' + cliparser.getCssStyle()
    invalidCSS = []
    for cssFile in css:
        # compile with corresponding css engine
        outCssfile = os.path.splitext(cssFile)[0] + '.css'
        cssEngine = cliparser.getCssEngine()
        if cssFile.endswith(extension) and extension != ".css":
            compiled = CommandLineParser.compileToCss(cssEngine, cssFile, outCssfile)
            if not compiled:
                invalidCSS.append(cssFile)
        elif '.css' not in cssFile:
            cssFile += '.css'

    # writing the CSS html link tags to the output file
    for cssFile in css:
        if cssFile not in invalidCSS:
            hb(f.outf, f.conf['specificcss'], cssFile)

    # writing the JS html script tags to the output file
    for jsFile in js:
        hb(f.outf, f.conf['specificjs'], jsFile)

    # Look for a title.
    if getNextCharacter(f) == '=':  # don't check exact number f.outf '=' here jem.
        t = br(getNextLine(f), f)[:-1]
        if title is None:
            title = re.sub(' *(<br />)|(&nbsp;) *', ' ', t)
    else:
        t = None

    #if title:
    hb(f.outf, f.conf['windowtitle'], title)

    out(f.outf, f.conf['bodystart'])

    if f.analytics:
        hb(f.outf, f.conf['analytics'], f.analytics)

    if fwtitle:
        out(f.outf, f.conf['fwtitlestart'])
        inserttitle(f, t)
        out(f.outf, f.conf['fwtitleend'])

    # navbar
    if navbar:
        # navbar = {'file': f, 'class': g[0][0], 'id': g[0][1], 'menuname': g[0][2], 'page': g[1][2], 'preface': g[2][2]} 
        navstart = f.conf['navstart'] % (navbar.get('class', ''), navbar.get('id', 'navbar-menu'))
        out(f.outf, navstart)
        # navbar = (f, 'menuname', 'page', 'preface')
        navData = ( navbar['file'], navbar['menuname'], navbar['page'], navbar['preface'] ) 
        insertnavbaritems(*navbar)
        out(f.outf, f.conf['navend'])
    else:
        out(f.outf, f.conf['nonav'])

    if menu:
        # menu = {'file': f, 'class': g[0][0], 'id': g[0][1], 'menuname': g[0][2], 'page': g[1][2], 'preface': g[2][2]}
        menustart = f.conf['menustart'] % (menu.get('class', ''), menu.get('id', 'sidemenu'))
        # print menustart
        out(f.outf, menustart )
        # menu = (f, 'menuname', 'page', 'preface')
        menuData = ( menu['file'], menu['menuname'], menu['page'], menu['preface'] ) 
        insertmenuitems(*menuData)
        out(f.outf, f.conf['menuend'])
    else:
        out(f.outf, f.conf['nomenu'])

    if not fwtitle:
        inserttitle(f, t)

    infoblock = False
    imgblock = False
    tableblock = False
    while 1:  # wait for EOF.
        p = getNextCharacter(f)

        if p == '':
            break

        # look for lists.
        elif p == '-':
            dashlist(f, False)

        elif p == '.':
            dashlist(f, True)

        elif p == ':':
            colonlist(f)

        # look for titles.
        elif p == '=':
            (s, count) = getNextLine(f, True)
            # trim trailing \n.
            s = s[:-1]
            hb(f.outf, '<h%d>|</h%d>\n' % (count, count), br(s, f))

        # look for comments.
        elif p == '#':
            l = getNextLine(f)

        elif p == '\n':
            getNextLine(f)

        # look for blocks.
        elif p == '~':
            getNextLine(f)
            # TODO: add class and id here
            # add class and id here
            if infoblock:
                out(f.outf, f.conf['infoblockend'])
                infoblock = False
                getNextLine(f)
                continue
            elif imgblock:
                out(f.outf, '</figure>\n')
                imgblock = False
                getNextLine(f)
                continue
            elif tableblock:
                out(f.outf, '</td></tr></table>\n')
                tableblock = False
                getNextLine(f)
                continue
            else:
                if getNextCharacter(f) == '{':
                    l = allreplace(getNextLine(f))
                    r = re.compile(r'(?<!\\){(.*?)(?<!\\)}', re.M + re.S)
                    g = re.findall(r, l)
                else:
                    g = []

                # process jemdoc markup in titles.
                if len(g) >= 1:
                    g[0] = br(g[0], f)

                if len(g) in (0, 1):  # info block.
                    out(f.outf, f.conf['infoblock'])
                    infoblock = True

                    if len(g) == 1:  # info block.
                        hb(f.outf, f.conf['blocktitle'], g[0])
                    out(f.outf, f.conf['infoblockcontent'])

                elif len(g) >= 2 and g[1] == 'table':
                    # handles
                    # {title}{table}{name}
                    # one | two ||
                    # three | four ||
                    tableClass = None
                    tableSplit = g[1].split(".")
                    if len(tableSplit) > 1:
                        tableClass = tableSplit[1]
                    name = ''
                    if len(g) >= 3 and g[2]:
                        name += ' id="%s"' % g[2]
                    if tableClass:
                        name += ' class="%s"' %tableClass
                    out(f.outf, '<table%s>\n<tr class="r1"><td class="c1">' % name)
                    f.tablerow = 1
                    f.tablecol = 1

                    tableblock = True

                elif len(g) == 2:
                    codeblock(f, g)

                elif len(g) >= 4 and g[1] == 'img_left':
                    # handles
                    # {}{img_left}{source}{alttext}{width}{height}{linktarget}.
                    imgClass = None
                    imgId = None
                    imgClassSplit = g[1].split('.')
                    imgIdSplit = g[1].split('#')
                    if len(imgClassSplit) > 1:
                        imgClass = imgClassSplit[1]

                    if len(imgIdSplit) > 1:
                        imgId = imgIdSplit[1]

                    g += [''] * (7 - len(g))

                    if g[4].isdigit():
                        g[4] += 'px'

                    if g[5].isdigit():
                        g[5] += 'px'

                    out(f.outf, '<figure>\n')
                    if g[6]:
                        out(f.outf, '<a href="%s">' % g[6])
                    
                    htmlClass = ''
                    if imgClass:
                        htmlClass = 'class="%s"' %imgClass
                    
                    htmlId = ''
                    if imgId:
                        htmlId = 'id="%s"' %imgId

                    out(f.outf, '<img class="img-fluid" src="%s" %s %s' %(g[2], htmlClass, htmlId) )
                    out(f.outf, ' alt="%s"' % g[3])
                    if g[4]:
                        out(f.outf, ' width="%s"' % g[4])
                    if g[5]:
                        out(f.outf, ' height="%s"' % g[5])
                    out(f.outf, ' />')
                    if g[6]:
                        out(f.outf, '</a>')
                    imgblock = True
                
                elif len(g) >= 2 and 'video' in g[1]:
                    # {}{video}{width}{height}{source}{source}...
                    videoTag = '<video'
                    if 'c' in g[1]:
                        videoTag += ' controls'
                    
                    if 'a' in g[1]:
                        videoTag += ' autoplay'
                    
                    if 'l' in g[1]:
                        videoTag += ' loop'

                    start = 2
                    if g[2].isdigit():
                        g[2] += 'px'
                        videoTag += ' width="%s"' %g[2]
                        start = 3

                    if g[3].isdigit():
                        g[3] += 'px'
                        videoTag += ' height="%s"' %g[3]
                        start = 4

                    videoTag += '>\n'
                    out(f.outf, videoTag)

                    for i in range(start, len(g)):
                        if g[i]:
                            source = g[i]
                            ext = os.path.splitext(g[i])[1]
                            srcTag = '<source src=%s type=video/%s />\n' %(source, ext)
                            out(f.outf, srcTag)
                        else:
                            # user did not provide source and so we consider it to be the end of it
                            break
                    out(f.outf, '<em>Sorry, your browser <strong>does not</strong> support the embedded videos.</em>')
                    out(f.outf, '</video>\n')

                # parse audio
                elif len(g) >= 2 and 'audio' in g[1]:
                    # {}{audio}{source}{source}...
                    classList = g[1].split('.')
                    idList = g[1].split('#')
                    audioClass = None
                    audioId = None

                    if len(classList) > 1:
                        audioClass = str(classList[1])
                    
                    if len(idList) > 1:
                        audioId = str(idList[1])

                    audioTag = '<audio'
                    if audioClass:
                        audioTag += ' %s' % audioClass

                    if audioId:
                        audioTag += ' %s' % audioId

                    if 'c' in g[1]:
                        audioTag += ' controls'
                    
                    if 'a' in g[1]:
                        audioTag += ' autoplay'
                    
                    if 'l' in g[1]:
                        audioTag += ' loop'
                    audioTag += '>\n'
                    out(f.outf, audioTag)

                    for i in range(2, len(g)):
                        if g[i]:
                            source = g[i]
                            ext = os.path.splitext(g[i])[1]
                            srcTag = '<source src=%s type=audio/%s />\n' %(source, ext)
                            out(f.outf, srcTag)
                        else: # user did not provide source and so we consider it to be the end of it
                            break
                    out(f.outf, '<em>Sorry, your browser <strong>does not</strong> support embedded audios.</em>')
                    out(f.outf, '</audio>\n')
                
                # parse forms
                elif len(g) >= 2 and g[1] == 'fs' or g[1] == 'FS':
                    # {}{fs}{action}{method}{name}
                    #g += [''] * (7 - len(g))
                    
                    classList = g[1].split('.')
                    idList = g[1].split('#')
                    formClass = None
                    formId = None

                    if len(classList) > 1:
                        formClass = str(classList[1])
                    
                    if len(idList) > 1:
                        formId = str(idList[1])

                    if not g[2]:
                        raisejandal("cannot create form without action attribute provided: \{fs\}\{action\}", f.linenum)
                    htmlForm = '<form action="%s"' %g[2]

                    if formId:
                        htmlForm += ' id="%s"' % formId
                    if formClass:
                        htmlForm += ' class="%s"' % formClass
                    
                    out(f.out, htmlForm)
                    
                    if g[3]:
                        out(f.outf, ' method="%s"') %g[3]
                    else:
                        out(f.outf, ' method="GET"')
 
                    if 'v' in g[1] or 'V' in g[1]:
                        out(f.outf, ' novalidate')
                    # introduced new form block variable for creation of forms
                    out(f.out, '>\n')

                elif len(g) == 2 and g[1].lower() == 'fe':
                    # {}{fe}
                    out(f.outf, '</form>\n')       
                elif len(g) >= 2 and g[1].lower() in ('it', 'ip', 'ie', 'ic', 'is'):
                    #{}{it}{name}{placeholder} = input type="text" name value
                    #{}{ip}{name}{placeholder} = input type="password" name
                    #{}{ie}{name}{placeholder} = input type="email" name
                    #{}{ic}{name}{value}{label} = input type="checkbox" name value 
                    #{}{is} =
                    g[1] = g[1].lower()
                    if g[1] != "is":
                        if not g[2]:
                            raisejandal("cannot create <input> tag without a 'name' attribute provided\nusage: \{inputtag\}\{name\}", f.linenum)
                        if g[1] == 'ic' and not g[3]:
                            raisejandal("cannot create <input type='checkbox> without a 'value' attrubute\nusage: \{inputtag\}\{name\}\{value\}")

                    if g[1] in ('it', 'ip', 'ie'):
                        name = str(g[2])
                        placeholder = None

                        if (g[3]):
                            placeholder = str(g[3])                        
                        inputType = 'text'
                        if g[1] == 'ip':
                            inputType = 'password'
                        elif g[1] == 'ie':
                            inputType = 'email'
                        out(f.outf, '<div class="form-group">\n')
                        out(f.outf, '<input type="%s" name="%s" placeholder="%s" class="form-control" />\n' %(inputType, name, placeholder))
                        out(f.outf, '</div>\n')
                    elif g[1] == 'is':
                        out(f.outf, '<button type="submit" class="btn btn-primary">Submit</button>\n')
                    elif g[1] == 'ic':
                        name = str(g[2])
                        inputType = 'checkbox'
                        value = str(g[3])
                        out(f.outf, '<div class="form-group">\n')
                        out(f.outf, '<input type="%s" name="%s" value="%s" class="form-control" />\n' %(inputType, name, value))
                        out(f.outf, '</div>\n')

                else:
                    raisejandal("couldn't handle block", f.linenum)

        else:
            s = br(nextParagraph(f), f, tableblock)
            if s:
                if tableblock:
                    hb(f.outf, '|\n', s)
                else:
                    hb(f.outf, '<p>|</p>\n', s)

    if menu:
        out(f.outf, f.conf['menulastbit'])
    else:
        out(f.outf, f.conf['nomenulastbit'])

    if showfooter and (showlastupdated or showsourcelink):
        out(f.outf, f.conf['footerstart'])
        if showlastupdated:
            if showlastupdatedtime:
                ts = '%Y-%m-%d %H:%M:%S %Z'
            else:
                ts = '%Y-%m-%d'
            s = time.strftime(ts, time.localtime(time.time()))
            hb(f.outf, f.conf['lastupdated'], s)
        if showsourcelink:
            hb(f.outf, f.conf['sourcelink'], f.inname)
        out(f.outf, f.conf['footerend'])

    out(f.outf, f.conf['bodyend'])

    if f.outf is not sys.stdout:
        # jem: close file here.
        # jem: XXX this is where you would intervene to do a fast open/close.
        f.outf.close()


# # TODO: regex matching bug for optional capture group