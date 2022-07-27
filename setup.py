# -*- coding: utf-8 -*-
'''
The setup script for the entire project.
@author: James Howard
'''
from setuptools import setup, find_packages

VERSION = "1.0.0"

setup(
  name="EKKOTools",
  version=VERSION,
  author="James Howard",
  author_email="jrhoward@utexas.edu",
  packages=find_packages(),
  license="No license. All rights reserved to original authors",
  keywords=["circular","dichroism"]
)