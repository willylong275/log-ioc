
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
    print config.items('logIoc')[0][1]
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
        self.es= Elasticsearch([self.es_host], port=self.es_port)
        
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
        utc_now = datetime.utcnow().isoformat()[:-3]+'Z'
        return utc_now
        
    def get_epoch_now(self):
        epoch_now = int(time.time() * 1000)
        return epoch_now
    
    def get_last_run(self):
        if self.check_index_existance(self.logioc_index) == False:
            self.create_index(self.logioc_index)
        else:
            res = self.es.search(index=self.logioc_index, doc_type='cycler', body={'query': {'match': {'Script':'Cycler Main'}}})
            if res['hits']['total'] == 0:
                print 'no record exists'
                return False
            else:
                last_run = last_run =  res['hits']['hits'][0]['_source']['last_run_time']
                return last_run      
    
    def update_last_run(self):
        res=self.es.index(index=self.logioc_index, doc_type='cycler', id=1, body={
        'Script': 'Cycler Main',
        'last_run_time': self.get_utc_now(),
        })
        print(" response: '%s'" % (res))
    
    def get_hits(self):
        newHits = self.es.search(index=self.es_index, body={
    "from" : 0, "size" :10000 ,
    "query": {
    "bool": {
            "filter": {"range": {  "@timestamp": {"gte":self.get_last_run(), "lte": self.get_utc_now()}}}
        }
    }
})
        print "found " +str(len(newHits['hits']['hits']))+" records that match criteria"
        newHits = newHits['hits']['hits']
        return newHits
    
    def cycler_eng(self): 
        sys.path.append('/opt/anaconda/bin/queries/')
        for line in self.query_list:
            print line.split('.')[0]
            #fix this
            import new_proc_watcher
            new_proc_watcher.main(self.get_hits())
            #new_proc_watcher.main()
