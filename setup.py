#!/usr/bin/python
"""
Created on Tue Oct 04 14:10:05 2011

@author: Chen Li
"""
from distutils.core import setup

setup(name='getdos',
      version='1.4.0.20111118',
      description='Phonon DOS generation from S(Q,E)',
      author='Chen Li',
      author_email='chenwli@gmail.com',
      url='http://getdos.googlecode.com',
      include_package_data = True,
      package_data = {'': ['*.pkl','*.csv']},
      packages=['multiphonon','uti','test_cases/ni_0300','batch_example','multiphonon/batch'],
#      data_files=[('test_cases', ['test_cases/ni_0300/sqe.pkl','test_cases/ni_0300/mqe.pkl'])],
      py_modules = [ 'user','getdos'],
     )
