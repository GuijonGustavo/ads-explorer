#!/usr/bin/env python

from distutils.core import setup

setup(
    name='ads-explore',
    version='0.1.0',
    author='A. Camps-Fariña, C. Espinosa-Ponce, G. Guijon',
    # author_email='',
    packages=['ads-explorer'],
    # url='http://pypi.python.org/pypi/',
    description="Get stats on an author's papers and give useful information as well as formatting the output for use in CV or just to get some fun statistics from ADS",
    install_requires=[
        "ads",
        "werkzeug == 1.0.1",
        "metaphone"
    ],
)
