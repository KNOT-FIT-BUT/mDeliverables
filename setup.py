#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
	"""
	Prints README.rst (which should contain information about this package)
	"""
	with open('README.rst') as f:
		return f.read()

setup(name='deliverables2',
      #version='0.1',
      description='Deliverables extractor',
      long_description=readme(),
      #classifiers=[
      #  'Development Status :: 3 - Alpha',
      #  'License :: OSI Approved :: MIT License',
      #  'Programming Language :: Python :: 2.7',
      #  'Topic :: Text Processing :: Linguistic',
      #],
      #keywords='',
      #url='',
      author='Jan Skácel',
      author_email='xskace08@stud.fit.vutbr.cz',
      #license='MIT',
      packages=['deliverables'],
      install_requires=[
          'rrslib','pymongo'
      ],
      #test_suite='nose.collector',
      #tests_require=['nose', 'nose-cover3'],
      #entry_points={
      #    'console_scripts': ['funniest-joke=funniest.cmd:main'],
      #},
      zip_safe=False)
