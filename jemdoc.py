#!/usr/bin/env python2
"""jemdoc version 0.7.3, 2012-11-27."""

# Copyright (C) 2007-2012 Jacob Mattingley (jacobm@stanford.edu).
#
# This file is part of jemdoc.
#
# jemdoc is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# jemdoc is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# The LaTeX equation portions of this file were initially based on
# latexmath2png, by Kamil Kisiel (kamil@kamikisiel.net).
#

import sys
import os
import re
import time
import StringIO
from subprocess import *
import tempfile

from commandlineparser import CommandLineParser
from controlstruct import ControlStruct, JandalError

def standardconf():
    return CommandLineParser.getStandardConfig(False)


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


def parseconf(cns):
    """
  This function parses configuration configuration filenames.
  cns is a list of configuration filenames
  
  This parses the given configuration file into a dictionary in which the tag variable are the contents of the square brackets
  in the config file
  
  The tag variable is the key and the resulting HTML page is the value in the syntax dict
  """
    syntax = {}
    warn = False
    # manually add the defaults as a file handle.
    fs = [
        StringIO.StringIO(standardconf())
    ]  # fs represents all the configuration files, including the default configuration file, as file objects
    for sname in cns:
        fs.append(
            open(sname, 'rb')
        )  # opens each configuration file and appends the file object to fs

    for f in fs:  # for each file object in fs
        # ControlStruct(fileObj) wraps fileObj in ControlStruct class
        # pc is a method
        while pc(ControlStruct(f)) != '':
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
  
  mname is the filename of the menu file
  current is the 
  prefix is the
  f is the ControlStruct wrapper class that decorates the output file object
  """
    m = open(mname, 'rb')
    while pc(ControlStruct(m)) != '':
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


def pc(f, ditchcomments=True):
    """Peeks at next character in the file."""
    # Should only be used to look at the first character of a new line.
    c = f.inf.read(1)  # reads first charactor of input file
    if c:  # only undo forward movement if we're not at the end.
        #
        # if character c is comment symbol and ditchComments is True, read next line with nl(f)
        if ditchcomments and c == '#':
            l = nl(f)  # reads next line
            if doincludes(
                    f, l
            ):  # doincludes(fileObj, line) is a method described below. Checks if user is including external file
                return "#"

        if c in ' \t':
            return pc(f)

        if c == '\\':
            c += pc(f)

        f.inf.seek(-1, 1)
    elif f.otherfiles:
        f.nextfile()
        return pc(f, ditchcomments)

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


def nl(f, withcount=False, codemode=False):
    """Get input file line."""
    """
  This method extracts the next line from the current file. If that file has no extra lines
  It switches to the next file
  """
    s = f.inf.readline()
    if not s and f.otherfiles:  # if current file has no lines left and there are other files
        f.nextfile()  # switch files
        return nl(f, withcount, codemode)  # perform same algorithm on it

    f.linenum += 1

    if not codemode:
        # remove any special characters - assume they were checked by pc()
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
            raise SyntaxError("couldn't handle the jandal (code 12039) on line"
                              " %d" % f.linenum)

        if not codemode:
            s = s.lstrip('-.=:')

        return (s, len(r.group(1)))
    else:
        if not codemode:
            s = s.lstrip('-.=:')

        print "nl: %s" % s
        return s


def np(f, withcount=False, eatblanks=True):
    """Gets the next paragraph from the input file."""
    # New paragraph markers signalled by characters in following tuple.
    if withcount:
        (s, c) = nl(f, withcount)
    else:
        s = nl(f)

    while pc(f) not in ('\n', '-', '.', ':', '', '=', '~', '{', '\\(', '\\)'):
        s += nl(f)

    while eatblanks and pc(f) == '\n':
        nl(f)  # burn blank line.

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
    r = re.compile(
        r'(?<!\\)\[img((?:\{.*?\}){,3})\s(.*?)(?:\s(.*?))?(?<!\\)\]',
        re.M + re.S)
    m = r.search(b)
    s = re.compile(r'{(.*?)}', re.M + re.S)
    while m:
        m1 = list(s.findall(m.group(1)))
        m1 += [''] * (3 - len(m1))

        bits = []
        link = m.group(2).strip()
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

        b = b[:m.start(
        )] + r'<figure><img class="img-fluid" %s /></figure>' % " ".join(
            bits) + b[m.end():]

        m = r.search(b, m.start())

    print "replacedimage: %s" % b
    return b


def replacelinks(b):
    """
  This method replaces all links written in the meta language and produces the corresponding HTML anchor tag
  with the href attribute appropriately populated
  """
    # works with [link.html new link style].
    r = re.compile(r'(?<!\\)\[(.*?)(?:\s(.*?))?(?<!\\)\]', re.M + re.S)
    m = r.search(b)
    while m:
        m1 = m.group(1).strip()

        if '@' in m1 and not m1.startswith('mailto:') and not \
           m1.startswith('http://'):
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

        b = b[:m.start()] + r'<a href=\"%s\">%s<\/a>' % (
            link, linkname) + b[m.end():]

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

    while pc(f) == char:
        (s, newlevel) = np(f, True, False)

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
    while pc(f) == ':':
        s = np(f, eatblanks=False)
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
        l = nl(f, codemode=True)
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

        output, _ = Popen(ext_prog, shell=True, stdin=PIPE,
                          stdout=PIPE).communicate(buff)
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
    if t is not None:
        hb(f.outf, f.conf['doctitle'], t)

        # Look for a subtitle.
        if pc(f) != '\n':
            hb(f.outf, f.conf['subtitle'], br(np(f), f))

        hb(f.outf, f.conf['doctitleend'], t)

def procfile(f, cliparser):
    f.linenum = 0

    menu = None
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

    while pc(f, False) == '#':
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
                    r = re.compile(r'(?<!\\){(.*?)(?<!\\)}', re.M + re.S)
                    g = re.findall(r, b)
                    if len(g) > 3 or len(g) < 2:
                        raise SyntaxError('sidemenu error on line %d' %
                                          f.linenum)
                    if len(g) == 2:
                        menu = (f, g[0], g[1], '')
                    else:
                        menu = (f, g[0], g[1], g[2])

                elif b.startswith('nav'):
                    # TODO: parse nav
                    nav = True
                    pass

                elif b.startswith('nofooter'):
                    showfooter = False

                elif b.startswith('nodate'):
                    showlastupdated = False

                elif b.startswith('notime'):
                    showlastupdatedtime = False

                elif b.startswith('fwtitle'):
                    fwtitle = True

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
                        raise SyntaxError('addtitle error on line %d' %
                                          f.linenum)

                    title = g[0]

    # Get the file started with the firstbit.
    # writing the first bit to the output file
    out(f.outf, f.conf['firstbit'])

    # writing default css link tag to output file
    if not nodefaultcss:
        out(f.outf, f.conf['defaultcss'])

    # Add per-file css lines here.
    extension = '.' + cliparser.getCssStyle()
    invalidCSS = []
    for cssFile in css:
        # TODO: compile with corresponding css engine
        outCssfile = os.path.splitext(cssFile)[0] + '.css'
        cssEngine = cliparser.getCssEngine()
        if cssFile.endswith(extension):
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
    if pc(f) == '=':  # don't check exact number f.outf '=' here jem.
        t = br(nl(f), f)[:-1]
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

    # TODO: complete navbar
    if nav:
        out(f.outf, f.conf['nav'])
    else:
        out(f.outf, f.conf['nonav'])

    if menu:
        out(f.outf, f.conf['menustart'])
        insertmenuitems(*menu)
        out(f.outf, f.conf['menuend'])
    else:
        out(f.outf, f.conf['nomenu'])

    if not fwtitle:
        inserttitle(f, t)

    infoblock = False
    imgblock = False
    tableblock = False
    while 1:  # wait for EOF.
        p = pc(f)

        if p == '':
            break

        elif p == '\\(':
            if not (f.eqs and f.eqsupport):
                break

            s = nl(f)
            # Quickly pull out the equation here:
            # Check we don't already have the terminating character in a whole-line
            # equation without linebreaks, eg \( Ax=b \):
            if not s.strip().endswith('\)'):
                while True:
                    l = nl(f, codemode=True)
                    if not l:
                        break
                    s += l
                    if l.strip() == '\)':
                        break
            out(f.outf, br(s.strip(), f))

        # look for lists.
        elif p == '-':
            dashlist(f, False)

        elif p == '.':
            dashlist(f, True)

        elif p == ':':
            colonlist(f)

        # look for titles.
        elif p == '=':
            (s, c) = nl(f, True)
            # trim trailing \n.
            s = s[:-1]
            hb(f.outf, '<h%d>|</h%d>\n' % (c, c), br(s, f))

        # look for comments.
        elif p == '#':
            l = nl(f)

        elif p == '\n':
            nl(f)

        # look for blocks.
        elif p == '~':
            nl(f)
            if infoblock:
                out(f.outf, f.conf['infoblockend'])
                infoblock = False
                nl(f)
                continue
            elif imgblock:
                out(f.outf, '</figure>\n')
                imgblock = False
                nl(f)
                continue
            elif tableblock:
                out(f.outf, '</td></tr></table>\n')
                tableblock = False
                nl(f)
                continue
            else:
                if pc(f) == '{':
                    l = allreplace(nl(f))
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
                    name = ''
                    if len(g) >= 3 and g[2]:
                        name += ' id="%s"' % g[2]
                    out(f.outf,
                        '<table%s>\n<tr class="r1"><td class="c1">' % name)
                    f.tablerow = 1
                    f.tablecol = 1

                    tableblock = True

                elif len(g) == 2:
                    codeblock(f, g)

                elif len(g) >= 4 and g[1] == 'img_left':
                    # handles
                    # {}{img_left}{source}{alttext}{width}{height}{linktarget}.
                    g += [''] * (7 - len(g))

                    if g[4].isdigit():
                        g[4] += 'px'

                    if g[5].isdigit():
                        g[5] += 'px'

                    out(f.outf, '<figure>\n')
                    if g[6]:
                        out(f.outf, '<a href="%s">' % g[6])
                    out(f.outf, '<img class="img-fluid" src="%s"' % g[2])
                    out(f.outf, ' alt="%s"' % g[3])
                    if g[4]:
                        out(f.outf, ' width="%s"' % g[4])
                    if g[5]:
                        out(f.outf, ' height="%s"' % g[5])
                    if g[6]:
                        out(f.outf, '</a>')
                    imgblock = True

                else:
                    raise JandalError("couldn't handle block", f.linenum)

        else:
            s = br(np(f), f, tableblock)
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


def main():
    cliparser = CommandLineParser()
    if cliparser.showConfig():
        cliparser.displayConfig()

    if cliparser.showInfo():
        cliparser.displayInfo()

    cliparser.installCssEngine()
    cssEngine = cliparser.getCssEngine()

    confnames = []
    innames = cliparser.getInputFiles()
    outdirname = cliparser.getOutputDir()
    if cliparser.getUserConfig():
        confnames.append(cliparser.getUserConfig())

    conf = parseconf(
        confnames
    )  # this function parses the configuration filenames in the list and returns config files

    # TODO: verify this
    # if outdirname is not None and not os.path.isdir(outdirname) and len(innames) > 1:
    #     raise RuntimeError('cannot handle one outfile with multiple infiles')

    # for each input file, format the corresponding output file
    for inname in innames:
        filename = re.sub(r'.jemdoc$', '', inname) + '.html'
        if outdirname is None:
            outfile = filename
        elif os.path.isdir(outdirname):
            # if directory, prepend directory to automatically generated name.
            outfile = os.path.join(outdirname, filename)
        # else:
        #     outfile = outdirname

        infile = open(inname, 'rUb')
        outfile = open(outfile, 'w')

        # create a control struct with the necessary parsed configuration
        f = ControlStruct(infile, outfile, conf, inname)

        procfile(f, cliparser)


#
if __name__ == '__main__':
    main()

# Insights on commandline parsing
# If user gives an output, that output has to be a directory, i.e., the directory to store the html documents produced by jemdoc
# All the output files are named after the input files with the extension '.html' attached to it instead of '.jemdoc'

# My improvements to commandline parsing:
# - html files are outputted to a directory specified by the -o optional argument. If none is provided by the user, a default is used
# - when compiling with react, the -o argument will be the name of the react application folder. The application name and title is decided during initialization of react app
# - only one arg for -o, raise error otherwise
# - only one arg for -c, raise error otherwise
# - if using react at compile time, no -c argument is used
# - all input files must exist in current dir. If they do not end with extension '.jemdoc' raise error
# - arguments can come in any order now
# - jemdoc will have a man page

# Improvements to the html
# - uses html5 syntax now

# Improvements to the css
# - more control over components via css than meta language
# - ability to use less

# Improvements to project structure
# when not using react:
# - styles directory
# - js directory
# - html directory

# when using react:
# - use react structure

# Replacement of latex with mathJax

# Proposed React Components:
# - List Component
# - Sidenar Component
# - Navbar Component
# - Footer Component
# - Image Component
# - Form Component
# - Codeblock Component
# - Title Component
# - Info Component
