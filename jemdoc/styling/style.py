import pkgutil, os

class Style:
    defaultCss = """
/* Default css file for jemdoc. */

table#tlayout {
    border: none;
    border-collapse: separate;
    background: white;
}

body {
    background: white;
    font-family: Georgia, serif;
    padding-bottom: 8px;
    margin: 0;
}

#layout-menu {
    background: #f6f6f6;
    border: 1px solid #dddddd;
    padding-top: 0.5em;
    padding-left: 8px;
    padding-right: 8px;
    font-size: 1.0em;
    width: auto;
    white-space: nowrap;
    text-align: left;
    vertical-align: top;
}

#layout-menu td {
    background: #f4f4f4;
    vertical-align: top;
}

#layout-content {
    padding-top: 0.0em;
    padding-left: 1.0em;
    padding-right: 1.0em;
    border: none;
    background: white;
    text-align: left;
    vertical-align: top;
}

#layout-menu a {
    line-height: 1.5em;
    margin-left: 0.5em;
}

tt {
    background: #ffffdd;
}

pre, tt {
    font-size: 90%;
    font-family: monaco, monospace;
}

a, a > tt {
    color: #224b8d;
    text-decoration: none;
}

a:hover {
    border-bottom: 1px gray dotted;
}

#layout-menu a.current:link, #layout-menu a.current:visited {
    color: #022b6d;
    border-bottom: 1px gray solid;
}
#layout-menu a:link, #layout-menu a:visited, #layout-menu a:hover {
    color: #527bbd;
    text-decoration: none;
}
#layout-menu a:hover {
    text-decoration: none;
}

div.menu-category {
    border-bottom: 1px solid gray;
    margin-top: 0.8em;
    padding-top: 0.2em;
    padding-bottom: 0.1em;
    font-weight: bold;
}

div.menu-item {
    padding-left: 16px;
    text-indent: -16px;
}

div#toptitle {
    padding-bottom: 0.2em;
    margin-bottom: 1.5em;
    border-bottom: 3px double gray;
}

/* Reduce space if we begin the page with a title. */
div#toptitle + h2, div#toptitle + h3 {
    margin-top: -0.7em;
}

div#subtitle {
    margin-top: 0.0em;
    margin-bottom: 0.0em;
    padding-top: 0em;
    padding-bottom: 0.1em;
}

em {
    font-style: italic;
}

strong {
    font-weight: bold;
}


h1, h2, h3 {
    color: #527bbd;
    margin-top: 0.7em;
    margin-bottom: 0.3em;
    padding-bottom: 0.2em;
    line-height: 1.0;
    padding-top: 0.5em;
    border-bottom: 1px solid #aaaaaa;
}

h1 {
    font-size: 165%;
}

h2 {
    padding-top: 0.8em;
    font-size: 125%;
}

h2 + h3 {
    padding-top: 0.2em;
}

h3 {
    font-size: 110%;
    border-bottom: none;
}

p {
    margin-top: 0.0em;
    margin-bottom: 0.8em;
    padding: 0;
    line-height: 1.3;
}

pre {
    padding: 0;
    margin: 0;
}

div#footer {
    font-size: small;
    border-top: 1px solid #c0c0c0;
    padding-top: 0.1em;
    margin-top: 4.0em;
    color: #c0c0c0;
}

div#footer a {
    color: #80a0b0;
}

div#footer-text {
    float: left;
    padding-bottom: 8px;
}

ul, ol, dl {
    margin-top: 0.2em;
    padding-top: 0;
    margin-bottom: 0.8em;
}

dt {
    margin-top: 0.5em;
    margin-bottom: 0;
}

dl {
    margin-left: 20px;
}

dd {
    color: #222222;
}

dd > *:first-child {
    margin-top: 0;
}

ul {
    list-style-position: outside;
    list-style-type: square;
}

p + ul, p + ol {
    margin-top: -0.5em;
}

li ul, li ol {
    margin-top: -0.3em;
}

ol {
    list-style-position: outside;
    list-style-type: decimal;
}

li p, dd p {
    margin-bottom: 0.3em;
}


ol ol {
    list-style-type: lower-alpha;
}

ol ol ol {
    list-style-type: lower-roman;
}

p + div.codeblock {
    margin-top: -0.6em;
}

div.codeblock, div.infoblock {
    margin-right: 0%;
    margin-top: 1.2em;
    margin-bottom: 1.3em;
}

div.blocktitle {
    font-weight: bold;
    color: #cd7b62;
    margin-top: 1.2em;
    margin-bottom: 0.1em;
}

div.blockcontent {
    border: 1px solid silver;
    padding: 0.3em 0.5em;
}

div.infoblock > div.blockcontent {
    background: #ffffee;
}

div.blockcontent p + ul, div.blockcontent p + ol {
    margin-top: 0.4em;
}

div.infoblock p {
    margin-bottom: 0em;
}

div.infoblock li p, div.infoblock dd p {
    margin-bottom: 0.5em;
}

div.infoblock p + p {
    margin-top: 0.8em;
}

div.codeblock > div.blockcontent {
    background: #f6f6f6;
}

span.pycommand {
    color: #000070;
}

span.statement {
    color: #008800;
}
span.builtin {
    color: #000088;
}
span.special {
    color: #990000;
}
span.operator {
    color: #880000;
}
span.error {
    color: #aa0000;
}
span.comment, span.comment > *, span.string, span.string > * {
    color: #606060;
}

@media print {
    #layout-menu { display: none; }
}

#fwtitle {
    margin: 2px;
}

#fwtitle #toptitle {
    padding-left: 0.5em;
    margin-bottom: 0.5em;
}

#layout-content h1:first-child, #layout-content h2:first-child, #layout-content h3:first-child {
    margin-top: -0.7em;
}

div#toptitle h1, #layout-content div#toptitle h1 {
    margin-bottom: 0.0em;
    padding-bottom: 0.1em;
    padding-top: 0;
    margin-top: 0.5em;
    border-bottom: none;
}

table {
    border: 2px solid black;
    border-collapse: collapse;
}

td {
    padding: 2px;
    padding-left: 0.5em;
    padding-right: 0.5em;
    text-align: center;
    border: 1px solid gray;
}

table + table {
    margin-top: 1em;
}

tr.heading {
    font-weight: bold;
    border-bottom: 2px solid black;
}

img {
    border: none;
}

""" 

    @staticmethod
    def getDefaultCSS():
        return Style.defaultCss

    @staticmethod
    def downloadDefaultCSS(outdir):
        filePath = os.path.join(outdir, "jemdoc.css")
        file = open(filePath, "w")
        file.write(Style.defaultCss)
        file.flush()
        file.close()
