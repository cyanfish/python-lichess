import io
import os
import setuptools
import sys
import platform
import re

def read_description():
    return io.open(os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8").read()

setuptools.setup(
    name="python-lichess",
    version='0.7',
    description='A client for the lichess.org API',
    long_description=read_description(),
    license="GPL3",
    keywords="chess lichess api",
    url="https://github.com/cyanfish/python-lichess",
    packages=["lichess"],
    install_requires=['requests', 'six'],
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
