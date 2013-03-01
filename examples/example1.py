#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This code should serve as an example of how to use deliverables2
as a module
"""


# Import deliverables
from deliverables.interface import *


# Create interface object and initialize url
deliv = Deliverables()

deliv.parse(url = "http://siconos.inrialpes.fr/")

# Lets get the RRSProject class instance
project = deliv.get_deliverables()

# Check the output
if not project:
	
	print("Non deliverables found")
	
else:
	
	# Lets print output RRS XML. I would like to note here that as the parsing
	# is already done ( by calling get_deliverables() ) it is not done again
	print(
		deliv.get_rrs_xml()
	)
