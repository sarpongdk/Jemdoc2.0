# Jemdoc (0.8.0)

Jemdoc is a light text-based markup language designed for creating websites. It takes a text file written with jemdoc markup, an optional configuration file and an optional menu file, and makes static websites that look something like [this one](http://jemdoc.jaboc.net/).

### Motivation

This revision to [jemdoc](https://github.com/jem/jemdoc) seeks to keep this utility tool with modern standards in web development. Since 2007, new technologies and modifications have been made to HTML and CSS. Jemdoc, in its present state lacks some of the features of the [HTML5](https://html.spec.whatwg.org/multipage/) standard including basic HTML markup such as:

- Semantic HTML tags
- HTML Forms
- Responsive web design

In addition, CSS3 has seen some changes as well. The most important feature concerning styling is the ability to use CSS Preprocessors, that have become common in the web development world.

This revision to jemdoc seeks to keep jemdoc abreast with these changes

### Installation

To install, make sure you have a python 2.7.\* interpreter available on your laptop. [Download it here](https://github.com/sarpongdk/Python-2.7.-/blob/master/python-2.7.17-macosx10.9.pkg) if needed.

Execute the following command in the console to download the jemdoc:

```
pip install jemdoc
```

### Documentation

To be provided soon


### Building source with `make`

A Makefile has been provided for anyone that wants to build the source documents from scratch locally. The following commands serves as a guide for using the Makefile, assuming the user is currently at the root of whatever directory the user decides to build the project in

```
Please use `make <target>' where <target> is one of
  clean         to remove build files
  clean-pyc     to remove .pyc files
  build         to build the project for distribution
  install       to install the project locally
  create-env    to initialize project in a virtual environment in the current working directory
  init    to download project dependencies from requirements.txt
```


### License

This work is the extension of the original jemdoc created by [Jacob Mattingley](https://github.com/jem). As the original project was under a GNU license, this has been put under the same license.
For more detail concerning the license, [click here](https://github.com/sarpongdk/Jemdoc2.0/blob/master/LICENSE)


### Bugs/Request

Please use the [GitHub issue tracker](https://github.com/sarpongdk/Jemdoc2.0/issues) to submit bugs and/or feature requests
