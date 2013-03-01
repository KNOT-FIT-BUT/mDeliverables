#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script name: Deliverables
Task: Find out page with deliverables, get links leading to deliverable
documents and index all available data.

Input: project site URL
Output: XML containing data stored in objects (rrslib.db.model) about deliverables


This script is part of ReResearch system.

Implemented by (authors):

	- Jan Skácel
	- Pavel Novotny
	- Stanislav Heller
	- Lukas Macko

Brno University of Technology (BUT)
Faculty of Information Technology (FIT)
"""

# RRSlib
from rrslib.web.httptools import is_url_valid
from rrslib.db.model import RRSProject,RRSUrl,RRSRelationshipPublicationProject
from rrslib.db.model import RRSRelationshipProjectUrl
from rrslib.xml.xmlconverter import Model2XMLConverter
# Modules of deliverables project
from gethtmlandparse import GetHTMLAndParse
from getdelivpage import GetDelivPage
from getdelivrecords import GetDelivRecords
# Standard modules
import StringIO
import os
import re

# JSON conversion

import xml.etree.cElementTree as ET
import simplejson, optparse, sys, os

def elem_to_internal(elem,strip=1):
	"""
	Convert an Element into an internal dictionary
	"""
	d = {}
	for key, value in elem.attrib.items():
		d['@'+key] = value
	# loop over subelements to merge them
	for subelem in elem:
		v = elem_to_internal(subelem,strip=strip)
		tag = subelem.tag
		value = v[tag]
		try:
			# add to existing list for this tag
			d[tag].append(value)
		except AttributeError:
			# turn existing entry into a list
			d[tag] = [d[tag], value]
		except KeyError:
			# add a new non-list entry
			d[tag] = value
	text = elem.text
	tail = elem.tail
	if strip:
			# ignore leading and trailing whitespace
			if text: text = text.strip()
			if tail: tail = tail.strip()
	if tail:
			d['#tail'] = tail
	if d:
			# use #text element if other attributes exist
			if text: d["#text"] = text
	else:
			# text is the value if no attributes
			d = text or None
	return {elem.tag: d}

def elem2json(elem, strip=1):
	"""
	Convert an ElementTree or Element into a JSON string.
	"""
	if hasattr(elem, 'getroot'):
			elem = elem.getroot()
	return simplejson.dumps(elem_to_internal(elem,strip=strip))

def xml2json(xmlstring,strip=1):
	"""
	Convert an XML string into a JSON string.
	"""
	elem = ET.fromstring(xmlstring)
	return elem2json(elem,strip=strip)

class Deliverables:
	"""
	Class implementing interface for purpose of using this module in other projects
	"""

	pr = None
	
	deliverables_rrs_xml = ""
	
	regexps = []
	
	def __init__(self,debug=False, verbose=False, quiet=True):
		"""
		Constructor of the class. Initialize deliverables extractor interface

		@type  debug: boolean
		@param debug: Prints debugging additional information
		
		@type  quiet: boolean
		@param quiet: No function will output anything on STDOUT when True.
		
		@type  verbose: boolean
		@param verbose: Prints additional information about parsing on STDOUT when True.
		
		"""
		self.opt = {
			'debug': False,
			'verbose': verbose,
			'regexp': None,
			'quiet': quiet,
			# We actually do not permit selecting single page without search
			# in this version of interface
			'page': False,
			'file': None,
			# Mechanism of storing file has been overloaded
			# No file is stored. Output RRS-XML is stored in atribute instead
			'storefile': True}
		
		links = None


	def parse(self,url):
		"""
		Finds deliverables page and parse data
			
		@type  url: string
		@param url: String defining initial url for deliverables search.
		
		"""
		# URL of the project
		self.opt_url = url
		
		# initialize main html handler and parser
		self.htmlhandler = GetHTMLAndParse()

		# searching deliverable page
		self.pagesearch = GetDelivPage(self.opt_url,
			verbose=self.opt['verbose'],
			debug=self.opt['debug'])
						 
		# extracting informations from page
		self.recordhandler = GetDelivRecords(debug=self.opt['debug'])
		
		# Proceed with extraction
		self.links = None
		self.main()
		
	def parse_page(self,deliverables_url):
		"""
		Finds deliverables page and parse data
			
		@type  deliverables_url: string
		@param deliverables_url: String defining url for deliverables extraction.
		
		"""

		# initialize main html handler and parser
		self.htmlhandler = GetHTMLAndParse()
						 
		# extracting informations from page
		self.recordhandler = GetDelivRecords(debug=self.opt['debug'])

		# URL of the project
		self.opt_url = deliverables_url
		
		# Proceed with extraction
		self.links = [deliverables_url]
		self.main()

	def main(self):
		"""
		Method implementing actions choosen by parameters in constructor.
		"""

		# Searching deliverable page
		if not self.links:
			self.pagesearch._sigwords.extend(self.regexps)
			self.links = self.pagesearch.get_deliverable_page()
		##################################
		if self.links[0] == -1:
			return self.links

		if self.opt['verbose']:
			print "*"*80
			print "Deliverable page: ", " ".join(self.links)
			print "*"*80

		self.pr = RRSProject()

		#Project - Url relationship
		if not self.opt['page']:
			pr_url = RRSUrl(link=self.opt_url)
			pr_url_rel = RRSRelationshipProjectUrl()
			pr_url_rel.set_entity(pr_url)
			self.pr['url'] = pr_url_rel
		self.recordhandler.process_pages(self.links)

		records = self.recordhandler.get_deliverables()

		if type(records) == list:
			#create relationship Project Publication
			self.records = records
			for r in records:
				rel = RRSRelationshipPublicationProject()
				rel.set_entity(r)
				self.pr['publication'] = rel
				#create XML from RRSProject
				output = StringIO.StringIO()
				converter = Model2XMLConverter(stream=output)
				converter.convert(self.pr)
				out = output.getvalue()
				output.close()
				#Either return RRSProject object or XML in string or store result into a file  
				if self.opt['storefile']:

					r = self._storeToFile(self.opt_url,out)
					#test if store ok
					if r[0]!=1:
						print r[1]
			 
				else:
					print out.encode('UTF-8')
				return self.pr

		else:
			return records
	
	def _storeToFile(self,url,res):
		"""
		Overrides method from original Deliverables class. This method just saves
		the RRS XML string to object atribute.
		
		@type  res: string
		@param res: Output RRS XML string for writing into object atribute.
		
		@type  url: string
		@param url: For compatibility with Deliverables class method only. It is not used.
		
		@return:  (1, 'OK')
		"""
		self.deliverables_rrs_xml = res.encode('UTF-8')

		return (1, 'OK')
	
	def get_deliverables(self):
		"""
		Access method to object of project with references to all parsed
		deliverables. It runs parsing only when necesseary.
		
		@return:  None when any error is found or RRSProject instance
		"""
		return self.pr
	
	def get_rrs_xml(self):
		"""
		Access method to object of project with references to all parsed
		deliverables. It runs parsing only when necesseary.
		
		@return:  String with RRS XML
		"""
		return self.deliverables_rrs_xml
		

	def get_json(self):
		"""
		Access method to data in form of JSON string.
		
		@return:  String in JSON
		"""	
		return xml2json(self.get_rrs_xml())
	
	def get_list(self):
		"""
		Access method to object of project with references to all parsed
		deliverables.
		
		@return:  List of RRSPublication instances
		"""	
		return self.records

	def __debug(self,msg):
		"""
		Prints debug message.
		
		@type  msg: string
		@param msg: String for printing on STDOUT
		"""
		if self.opt.debug:
			print("Debug message: " +str(msg));
			
	def add_regexp(self,regexp):
		"""
		Prints debug message.
		
		@type  regexp: string
		@param regexp: Regular expression pattern for adding to deliverables page ranking regexp list
		"""
		self.regexps.append(regexp)
		
	def remove_regexp(self,regexp):
		"""
		Prints debug message.
		
		@type  regexp: string
		@param regexp: Regular expression pattern for remove from deliverables page ranking regexp list
		"""
		self.regexps.remove(regexp)
