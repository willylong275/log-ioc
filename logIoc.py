try:
	import sys
	import time
	import warnings
	import os
	import ConfigParser
	from datetime import datetime
    	from elasticsearch import Elasticsearch, helpers
	from multiprocessing import Process
except:
	print("Please make sure you have required modules installed. pip -r requirements.txt or pip install elasticsearch")

class logIoc(object):
	config = ConfigParser.RawConfigParser()	
	config.read(os.getcwd()+'/configs/logIoc.ini')
	sys.path.append(os.getcwd()+'/queries/')
        sys.path.append(os.getcwd()+'/batch_queries/')

	def __init__(self):
        	config = ConfigParser.RawConfigParser()
		batch_queries = []
        	config.read(os.getcwd()+'/configs/logIoc.ini')
        	for line in (os.listdir(os.getcwd()+'/batch_queries/')):
                        if line.split('.')[1]=="py":
                                if line.split('.')[0] != "__init__":
                                        batch_queries.append(line)
		queries = []
        	for line in (os.listdir(os.getcwd()+'/queries/')):
        		if line.split('.')[1]=="py":
				if line.split('.')[0] != "__init__":
					queries.append(line)
        	self.ini_sections= config.sections()
        	self.es_host= config.get('logIoc', 'es_host')
        	self.es_port= config.get('logIoc', 'es_port')
        	self.es_index= config.get('logIoc', 'es_index')
        	self.logioc_index= config.get('logIoc', 'management_index')
        	self.batch_window= config.get('batch_cycler', 'batch_window')
		self.query_list = queries
		self.batch_query_list = batch_queries
		self.es= Elasticsearch([self.es_host], port=self.es_port)
		#self.cycler_initialize()
		self.init_done = False
        
	def check_index_existance(self, index):
        	print "in check_index_existance"
		if self.es.indices.exists(index):
             		return(True)
        	else:
            		return(False)
    
	def create_index(self, index):
		print "in create index"
        	request_body = {
        	"settings" : {
            	"number_of_replicas": 0
                	}
        	}	
        	print("creating '%s' index..." % (index))
        	res = self.es.indices.create(index = index, body = request_body)
        	print(" response: '%s'" % (res))
    
	def get_utc_now(self):
        	utc_now = datetime.utcnow().isoformat()[:-3]+'Z'
        	return utc_now
        
	def get_epoch_now(self):
        	epoch_now = int(time.time() * 1000)
        	return epoch_now
    
	def get_last_run(self):
		print "in get last run"
		#if self.check_index_existance(self.logioc_index) == False:
            		#self.create_index(self.logioc_index)
        	#else:
            	res = self.es.search(index=self.logioc_index, doc_type='cycler', body={'query': {'match': {'Script':'Cycler Main'}}})
            	if res['hits']['total'] == 0:
                	print 'no record exists'
                	return False
		else:
                	last_run = last_run =  res['hits']['hits'][0]['_source']['last_run_time']
			return last_run      
    
	def update_last_run(self):
		print "update last run"
        	res=self.es.index(index=self.logioc_index, doc_type='cycler', id=1, body={
        	'Script': 'Cycler Main',
        	'last_run_time': self.get_epoch_now(),
        	})
        	#print(" response: '%s'" % (res))
    
    	def bulk_index(self, index_name, dict_list):
		res = helpers.bulk( self.es, dict_list)
		return

	def get_hits(self):
		print "in get hits"
        	time_filter_query={ "query":{"bool": { "filter": {"range": {"@timestamp": {
											"gte": int(self.get_last_run()),
                                                                       			"lte": int(self.get_epoch_now()),
                                                                       			"format":"epoch_millis"
                                                                          		}}}}}}
		scan_generator=helpers.scan(self.es, query=time_filter_query, index=self.es_index,)
		newHits=[]
		for item in scan_generator:
    			newHits.append(item)
		#len(listy)
		print "found " +str(len(newHits))+" records that match criteria"
        	#newHits = ['hits']['hits']
        	return newHits
    
   	def cycler_initialize(self):
		print "in cyler initialize"
   		if self.check_index_existance(self.logioc_index)== False:
            		print "management index existance returned false"
			self.create_index(self.logioc_index)
        	if self.get_last_run() == False:
            		self.update_last_run()
            		time.sleep(10)
        	else:
            		print "cycler initialization completed already" 
	
	#def query_waiter_loop(self, query_name):
		#subprocess 
		#get configed wait time 
		#get hits ...have work to do there
		#spawn query_name(hits)
		#wait time
	
	def query_proc_start(self):
		sys.path.append(os.getcwd()+'/queries/')
		jobs = []
		for line in self.query_list:
                                line = line.split('.')[0]
                                line_query =__import__(line)
				wait = self.config.get('query_window', line)
				print wait
		#query = __import__('test_query')
		hits = self.get_hits()
		p=Process(target = query.main(hits),)
		p.start()
		p.join()
		print "in function"
		#def f(name):
		#	print 'hello', name
		#p = Process(target=f, args=('bob',))
		#p.start()
		#p.join()

   	def batch_cycler(self):
		cycle_start = self.get_epoch_now()
		if self.init_done == False:
        		self.cycler_initialize()
			self.init_done = True
        	hits = self.get_hits()
		self.update_last_run()
		if len(hits) == 0:
			print "last run time="+str(self.get_last_run())
			print "no logs captured since last run time, pausing until next window"
        	if len(hits) != 0:
			for line in self.batch_query_list:
	            		line = line.split('.')[0]
        	    		line_query =__import__(line)
            			line_query.main(hits)
		cycle_finish = self.get_epoch_now()
		cycle_duration = (cycle_finish - cycle_start)*.001
		print cycle_duration
		time.sleep(int(self.batch_window)-cycle_duration)
		self.batch_cycler() 
