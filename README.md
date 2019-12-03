# Jemdoc2.0
Jemdoc2.0 is an extension of Jemdoc which extends the meta language used to include HTML5 features. incorporates the semantics behind HTML5 and supports multiple CSS preprocessors

## Getting Started
To run Jemdoc2.0, make sure that you have:
- python >= 2.6.x (< 3.x.x)
- npm

## Usage
Jemdoc2.0 provides a new commandline page that clearly describes the usage of the program

The commandline help can be accessed via `python2 jemdoc.py -h` or `python2 jemdoc2.py --help`

usage: Jemdoc [-h] [-s] [-v] [-i] [--css <engine>] [-r]
              [-c <filename>] [-d <dirname>]
              input [input ...]

Produces html markup from a jemdoc SOURCEFILE. See
http://jemdoc.jaboc.net/ for many more details.

positional arguments:
  input                 relative path to input files

optional arguments:
  -h, --help            show this help message and exit
  -s, --show-config     generates the standard configuration in a directory
                        <configs> in the current working directory
  -v, --version         display Jemdoc version number
  -i, --info            display system information
  --css <engine>
                        add stylesheet <engine> support [less|sass|scss]
                        (defaults to plain css)
  -c <filename>, --config <filename>
                        add custom configuration file
  -d <dirname>, --dir <dirname>
                        output files in directory <dirname>, name of ReactJS
                        directory when compiling with ReactJS



