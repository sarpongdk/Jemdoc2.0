#/usr/bin/env python2

import setuptools

# long description
longDesc = ""
with open("README.md", "r") as f:
   longDesc = f.read()

# parsing requirements.txt
requirements = []
with open("requirements.txt", "r") as fr:
   for line in fr:
      requirements.append(line.strip())

# setup tools
setuptools.setup(name='jemdoc',
      version='0.8.0',
      description='jemdoc is a light text-based markup language designed for creating websites. It takes a text file written with jemdoc markup, an optional configuration file and an optional menu file, and makes static websites',
      author='David Sarpong',
      author_email='sarpong.david2@gmail.com',
      long_description=longDesc,
      long_description_content_type="text/markdown",
      python_requires="==2.7.*",
      url='https://github.com/sarpongdk/Jemdoc2.0',
      packages=setuptools.find_packages(),
      install_requires=requirements,
      classifiers=[
         "Programming Language :: Python :: 2",
         "Operating System :: OS Independent"
      ],
      entry_points={
         "console_scripts": ["jemdoc=jemdoc.main:main"]
      },
      include_package_data=True,
      package_data={
         # include any config/*.txt file and css/*.css file in jemdoc package
         "": [ "*.css" ]
      }
    )
