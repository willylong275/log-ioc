try:
	import sys
	import time
	import warnings
	import os
	import ConfigParser
	from datetime import datetime
    	from elasticsearch import Elasticsearch, helpers
except:
   	 print("Please make sure you have required modules installed. pip -r requirements.txt or pip install elasticsearch")

class logIoc(object):
    config = ConfigParser.RawConfigParser()
    config.read(os.getcwd()+'/configs/logIoc.ini')
    queries = []
    for line in (os.listdir(os.getcwd()+'/queries/')):
        queries.append(line)

    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read(os.getcwd()+'/configs/logIoc.ini')
        queries = []
        for line in (os.listdir(os.getcwd()+'/queries/')):
            queries.append(line)
        self.ini_sections= config.sections()
        self.es_host= config.get('logIoc', 'es_host')
        self.es_port= config.get('logIoc', 'es_port')
        self.es_index= config.get('logIoc', 'es_index')
        self.logioc_index= config.get('logIoc', 'management_index')
        self.query_list = queries
        self.es= Elasticsearch([self.es_host], port=9200)
        
    def check_index_existance(self, index):
        if self.es.indices.exists(index):
             return(True)
        else:
            return(False)
    
    def create_index(self, index):
        request_body = {
        "settings" : {
            "number_of_replicas": 0
                }
        }
        print("creating '%s' index..." % (index))
        res = self.es.indices.create(index = index, body = request_body)
        print(" response: '%s'" % (res))
    
    def get_utc_now(self):
        now = datetime.utcnow().isoformat()[:-3]+'Z'
        return now
        
