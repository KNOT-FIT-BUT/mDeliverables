#!/usr/bin/python
# -*- coding: utf-8 -*-

# Synchronized queue
from Queue import Queue
# Thread, Thread safe event variable and Synchronization lock
from threading import Thread, Event, Lock
from random import randrange
# Import deliverables
from deliverables.interface import *
# Monitor

# Config parser
import ConfigParser 

# Pymongo
from pymongo import Connection
import pymongo
import gridfs

# File I/O
import os

# File download
import urllib2

class Document():
	"""
	Document class
	"""

	def __init__(this,mongodb_connection):
		"""
		Constructor
			
		@type  mongodb_connection: conenction
		@param mongodb_connection: conenction to mongodb
		"""
		
		this.fs = gridfs.GridFS(mongodb_connection['deliverables'])
		this.mongo_collection = mongodb_connection['deliverables']['file']
	
	def document_store(this,document_url, title, project_url, fileDV):
		"""
		Inserts file into database
			
		@type  document_url: string
		@param document_url: url of the document
			
		@type  title: string
		@param title: title of the project
			
		@type  project_url: string
		@param project_url: url of the project (page with deliverables)
			
		@type  fileDV: dict
		@param fileDV: dictionary containing file name, content type and data themself
		"""

		if this.fs.exists({"_id": document_url}):
			this.fs.delete(document_url)
		with this.fs.new_file(_id = document_url,filename = fileDV['filename'],contentType = fileDV['contentType']) as this.fp:
			this.fp.write(fileDV['data'])
			
			this.mongo_collection.insert([{'_id':document_url,'title' : title,'project_url' : project_url }])
			#osetrit ci mongo_collection uz existuje alebo je None

class parser:
	"""
	Configuration parser
	"""
	
	config = ConfigParser.ConfigParser()

	def parse(self,file):
		config = self.config.read(file)

	def getPropertyValue(self, section, name):
		return self.config.get(section,name)

	def getValueAsInt(self, section, name):
		return self.config.getint(section,name)

	def getValueAsFloat(self, section, name):
		return self.config.getfloat(section,name)

	def getValueAsBoolean(self, section, name):
		return self.config.getboolean(section,name)

	def loadConfiguration(self, filepath, requiredconfig):
		config = self.config.read(filepath)
		k = requiredconfig.keys()

		for section in k:
			sec_exists = self.config.has_section(section)
			if sec_exists == False:
				raise ConfigParser.NoSectionError

			for names in requiredconfig[section]:
				name_exists = self.config.has_option(section,names)
				if name_exists == False:
					raise ConfigParser.NoOptionError(names,section)


#end of class parser



class Worker(Thread):
	"""
	Task implementing worker agent base. Task is given from a synchronous queue.
	Thread is executing tasks from a given tasks queue.
	"""
	
	def __init__(self, tasks, err_object):
		"""
		Worker constructor
		
		@type  tasks: queue
		@param tasks: queue of tasks
		
		@type  err_object: object
		@param err_object: object implementing set_error(self,error) method
		"""
		self.err_object = err_object
		Thread.__init__(self)
		self.tasks = tasks
		self.daemon = True
		self.start()
	
	def run(self):
		"""
		Method running the tasks
		"""
		while True:
			func, args, kargs = self.tasks.get()
			try: func(*args, **kargs)
			except Exception, e: self.err_object.set_error("Thread unhandeled exception: \n"+str(e))
			self.tasks.task_done()

class ThreadPool:
	"""
	Pool of threads consuming tasks from a queue
	"""
	def __init__(self, num_threads, err_object):
		"""
		Worker pool constructor
		
		@type  num_threads: integer
		@param num_threads: number of worker agent to spawn
		
		@type  err_object: object
		@param err_object: object implementing set_error(self,error) method
		"""
		self.tasks = Queue(num_threads)
		for _ in range(num_threads): Worker(self.tasks, err_object)

	def add_task(self, func, *args, **kargs):
		"""
		Adds a task to the queue
		
		@type  func: function object
		@param func: function for execution by worker
		
		@type  args: list
		@param args: list of unnamed arguments for given worker procedure
		
		@type  kargs: dict
		@param kargs: dictionary of named arguments for given worker procedure
		"""
		self.tasks.put((func, args, kargs))

	def wait_completion(self):
		"""
		Wait for completion of all the tasks in the queue
		"""
		self.tasks.join()
		
		


class Deliverables_daemon:
	"""
	Main class of threading parser of deliverables
	"""
	
	
	# Object checking URL for changes
	monitor = None
	
	# Thread pool
	pool = None
	
	# Thread safe event variable for first thread, that call that makes an error
	error = None
	error_lock = Lock()
	
	# Url iterator
	iterator = [].__iter__()
	
	# Database connection
	connection = None
	db = None
	
	def __init__(self,number_of_threads,url_iterator = None,connection = None,host = 'localhost',port = 27017):
		"""
		Constructor - Either connection or host with port should be given by parameters.
		Otherwise localhost:27017 will be expected to run database.
		
		@type  number_of_threads: integer
		@param number_of_threads: number of threads
		
		@type  url_iterator: iterator
		@param url_iterator: iterator of urls of deliverables projects
		
		@type  connection: connection
		@param connection: conenction to mongodb
		
		@type  host: string
		@param host: host of the mongodb database (implicitly 'localhost')
		
		@type  port: integer
		@param port: port on which database is running (implicitly 27017)
		"""
		
		# Initialize database connection
		if connection:
			self.connection = connection
		else:
			try:
				self.connection = Connection(host, port)
			except:
				self.set_error("Unable to establish connection to MongoDB")
				return
			self.db = self.connection.deliverables
		# Initializing pool and creating threads
		self.pool = ThreadPool(number_of_threads,self)
		# If is given setting up iterator over input URLs
		self.iterator = url_iterator

	def parse(self,url_iterator = None):
		"""
		Main method for running thread pool.
		
		@type  url_iterator: iterator
		@param url_iterator: iterator of urls of deliverables projects
		"""
		# If is given setting up iterator over input URLs
		if url_iterator:
			self.iterator = url_iterator
		
		# If no iterator is given, we have nothing to do
		if self.iterator:
			
			# Check for error
			if self.error:
				return
				
			# Infinite loop
			while True:
				# End of iteration will raise exception StopIteration
				try:
					# Check for error
					if self.error:
						break
					# Get next url
					next_url = self.iterator.next()
					# Give another task to queue
					self.pool.add_task(self.worker_procedure, next_url)
				except StopIteration:
					# No more URLs to deal
					break;
			
			# Wait for completion of task in queue
			self.pool.wait_completion()
		
	def isErr(self):
		"""
		Method returning None if there was no fatal error. If there was an
		error it is returned in form of string
		"""
		return self.error

	def worker_procedure(self,url):
		"""
		Main method for running thread pool.
		
		@type  url: string
		@param url: url of deliverables project
		"""
		### Download URLs and meta throught Deliverables2 interface ###

		# Create interface object and initialize url
		deliv = Deliverables()

		print "Deliverables project url: %s" % url

		try:
			deliv.parse(url)
		except:
			# Recoverable error during parsing
			return

		# Lets get the RRSProject class instance
		project = deliv.get_deliverables()

		# Check the output
		if project:
			# Get list of RRSPublication instances
			try:
				document_list = deliv.get_list()
			except:
				# Recoverable error during parsing
				return
			# Check each URL with link checker
			for deliverable in document_list:
				try:
					url = deliverable.url[0].get_entities()[0].link
				except:
					continue
				# If it is changed or new: download
				# Check URL for changes if monitor is set
				if not self.monitor or self.monitor.get(url).check():
					# Download document
					print "Processing document: %s" % url
					try:
						response = urllib2.urlopen(url)
						data = response.read()
					except:
						# Non-working URL - ignore
						data = None

					if data:
						# Content type determination
						import mimetypes
						content_type = mimetypes.guess_type(url, strict=False)
						# Database actualization
						document = Document(self.connection)
						filedv = {"filename":url.rsplit('/',1)[0],"contentType":content_type,"data":data}
						try:
							document.document_store(url, deliverable.title, deliv.get_deliverables().url[0].get_entities()[0].link, filedv)
						except:
							# Error saving file
							return

			# Project last checkout date actualization
			
	def set_error(self,error):
		"""
		Fatal error synchronous processing method. Uses lock.
		(unhandeled exception form thread, no connection to db etc.)
		
		@type  error: string
		@param error: text descripting error
		"""
		self.error_lock.acquire()
		if not self.error:
			self.error = error
		self.error_lock.release()
