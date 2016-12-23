#!/usr/bin/python3

from setuptools import setup, find_packages
import sys
from os import path

if(sys.version_info.major != 3):
	raise SystemError("PyRegisterMachine2 is designed for python3 only.")

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
	name = "py_register_machine2",
	version = "0.1.2",
	description = "A Register Machine Package",
	long_description = long_description,
	url = "https://github.com/daknuett/py_register_machine2",
	author = "Daniel Knüttel",
	author_email = "daknuett@gmail.com",
	license = "GPL v3",
	classifiers = ['Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
		'Topic :: Education',
		'Topic :: Education :: Testing',

		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5'],
	keywords = "simulation virtualization processor registermachine",
	packages = find_packages()


     )
