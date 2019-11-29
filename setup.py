#!/usr/bin/env python
import os.path
from sys import stderr
from setuptools import setup

from pyautoconfig import __version__ as VERSION

DESCRIPTION = "Python configuration library"
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()

setup(
    name="pyautoconfig",
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Joshua Nelson",
    author_email="jyn514@gmail.com",
    license="BSD",
    keywords="configuration, argparse",
    url="https://github.com/jyn514/py-autoconfig/",
    packages=["pyautoconfig"],
    # TODO: make these optional
    install_requires=["toml", "pyyaml"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
)
