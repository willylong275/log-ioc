#!/usr/bin/env python
try:
        import sys
        import time
        import os
        import ConfigParser
        import collections
        import flatdict
        import calendar
        import pandas as pd
        from datetime import datetime
        from elasticsearch import Elasticsearch, helpers
        from multiprocessing import Process
        import threading
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
                self.window_walk= config.get('logIoc', 'window_walk')
                self.sliding_window= config.get('logIoc', 'sliding_window')
                self.batch_window= config.get('batch_cycler', 'batch_window')
                self.api_key= config.get('virus_total', 'api_key')
                self.query_list = queries
                self.batch_query_list = batch_queries
                self.es= Elasticsearch([self.es_host], port=self.es_port)
                #self.cycler_initialize()
                self.init_done = False
		self.lock=threading.Lock()		

	def log_alert(self, offending_id, message):
		print ("log alert added to elasticsearch")
                res=self.es.index(index="logstash-windows-hosts-2017.07.25" , doc_type="log-alert",  body={
                'Message': message,
                'Offending_Log_id:': offending_id,
                })
                print(" response: '%s'" % (res))

        
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
                #print("creating '%s' index..." % (index))
                res = self.es.indices.create(index = index, body = request_body)
                #print(" response: '%s'" % (res))

        def get_utc_now(self):
                utc_now = datetime.utcnow().isoformat()[:-3]+'Z'
                return utc_now

        def get_epoch_now(self):
                epoch_now = int(time.time() * 1000)
                return epoch_now

        def get_last_run(self, script_name):
                #print "in get last run"
                if self.check_index_existance(self.logioc_index) == False:
                        self.create_index(self.logioc_index)
                else:
                        res = self.es.search(index=self.logioc_index, doc_type=script_name+"-time-record", body={'query': {'match': {'Script':script_name}}})
                if res['hits']['total'] == 0:
                        print 'no time record for '+script_name+' existed'
                        return False
                else:
                        last_run = last_run =  res['hits']['hits'][0]['_source']['last_run_time']
                        return last_run

        def update_last_timestamp(self, script_name, last_timestamp):
                print ("last timestamp updated for "+script_name)
                res=self.es.index(index=self.logioc_index, doc_type=script_name+"-last-timestamp", id=1, body={
                'Script': script_name,
                'last_timestamp_saw': last_timestamp,
                })
                #print(" response: '%s'" % (res))
	
	def get_last_timestamp(self, script_name):
                #print "in get last run"
        	if self.check_index_existance(self.logioc_index) == False:
                        self.create_index(self.logioc_index)
                else:
                        res = self.es.search(index=self.logioc_index, doc_type=script_name+"-last-timestamp", body={'query': {'match': {'Script':script_name}}})
                if res['hits']['total'] == 0:
                        print 'no last timestamp for '+script_name+' existed'
                        return False
                else:
                        last_timestamp = last_run =  res['hits']['hits'][0]['_source']['last_timestamp_saw']
                        return last_timestamp

        def update_last_run(self, script_name):
                print ("last run updated for"+script_name)
                res=self.es.index(index=self.logioc_index, doc_type=script_name+"-time-record", id=1, body={
                'Script': script_name,
                'last_run_time': self.get_epoch_now(),
                })
                #print(" response: '%s'" % (res))
        def bulk_index(self, index_name, dict_list):
                res = helpers.bulk( self.es, dict_list)
                print(" response: '%s'" % (str(res)))
                print res
                print str(res)
                return

        def get_hits(self, start_time, stop_time):
                #print "in get hits"
                time_filter_query={ "query":{"bool": { "filter": {"range": {"@timestamp": {
                                                                                        "gte": start_time,
                                                                                        "lte": stop_time,
                                                                                        "format":"epoch_millis"
                                                                                        }}}}}}
                scan_generator=helpers.scan(self.es, query=time_filter_query, index=self.es_index,)
                newHits=[]
                for item in scan_generator:
                        utc_record=item['_source']['@timestamp'][:-1]
                        new_value=calendar.timegm(datetime.strptime(utc_record, "%Y-%m-%dT%H:%M:%S.%f").timetuple())*1000
                        item['@timestamp']=new_value
                        #item['fields']['@timestamp']=new_value
                        newHits.append(item)
                #len(listy)
                #print "printing new hits"
                #print newHits[0]
                #print ("found " +str(len(newHits))+" records that match criteria and sending them to cycle")
                #newHits = ['hits']['hits']
                return newHits

        def cycler_initialize(self):
        #print "in cyler initialize"
            if self.check_index_existance(self.logioc_index)== False:
                print "management index existance returned false"
                print "creating it now..."
                lio.create_index(lio.logioc_index)
            if self.get_last_run('batch-cycler') == False:
                        self.update_last_run('batch-cycler')
            
	    for line in self.query_list:
	
	   	 if self.get_last_timestamp(line) == False:
                 	self.update_last_timestamp(line, self.get_epoch_now())
	    try:
                if self.sliding_window[-1:] != 'h' or 'm' or 's':
                    print "config check pass....starting window initialization"
            except:
                print ("Problem with config, sliding window elapsed time should be appended with  either an h, m, or s for hour, minutes or seconds")
            now=self.get_epoch_now()
            if self.sliding_window[-1:]== "h":
                window_start=now-int(self.sliding_window[:-1])*3600000
                self.window_interval=int(self.sliding_window[:-1])*3600000
            elif self.sliding_window[-1:]== "m":
                window_start=now-int(self.sliding_window[:-1])*60000
            elif self.sliding_window[-1:]== "s":
                window_start=now-int(self.sliding_window[:-1])*1000
            else:
                print ("error initializing time window....exiting")
                exit()
            window_walk=int(self.window_walk[:-1])
            #print (self.sliding_window)
            #print (window_start)
            #print (str(int(self.get_epoch_now()-window_start())))
            hits = self.flatten_dict(self.get_hits(window_start, self.get_epoch_now()))
            return(hits)

        def flatten_dict(self, hits):
            flat_hits=[]

            def flatten(hit, parent_key='', sep='.'):
                items = []
                for k, v in hit.items():
                    new_key = parent_key + sep + k if parent_key else k
                    if isinstance(v, collections.MutableMapping):
                        items.extend(flatten(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return(dict(items))
            
            for hit in hits:
                flat_hits.append(flatten(hit))         
            return(flat_hits)

        def subprocess_holder_loop(self, subquery):
                x=__import__(subquery)
                wait = self.config.get('query_window', subquery)
                print ("starting thread to start execute then wait loop for  "+subquery)
                #sub_proc_query=Process(target = self.batch_cycler(),)
                while True:
                        hits=[]
                        sub_proc_query=Process(target = x.main(df_hits, self.lock),)
                        self.update_last_run(subquery)
                        time.sleep(int(wait))
                        print ("execution & wait cycle complete for  "+ subquery)
                        print "starting cycle over again"
        
	def query_proc_start(self):
                from multiprocessing import Process
                sys.path.append(os.getcwd()+'/queries/')
                jobs = []
                print self.query_list
                for line in self.query_list:

                                subquery = line.split('.')[0]
                                #g=Process(target = self.subprocess_holder_loop(),args=(subquery,)).start()
                                #g.start()
                                #subquery.join()
                                #thread = Thread()
                                thread=threading.Thread(target=self.subprocess_holder_loop, args=(subquery,))
                                thread.daemon=True
                                thread.start()
                                #self.subprocess_holder_loop(thread, subquery)
                                print ("subquery was "+ subquery)
                while True:
                        time.sleep(1)

        def eng(self):
            cycle_num=1
            while True:
                if cycle_num==1:
                    init_time_start=self.get_epoch_now()
                    hits=self.cycler_initialize()
                    global df_hits
		    #self.lock.acquire()
                    df_hits = pd.DataFrame(hits).sort_values('@timestamp')
		    print ("Window Initialization ElasticSearch query returned "+str(len(df_hits))+" records for the entire configured window")
		    #self.lock.release()
                    del hits
                    print ("initialization time took "+str((self.get_epoch_now()-init_time_start)/1000)+" seconds")
                    eng_now=self.get_epoch_now()
                    #display(df_hits.iloc[(len(df_hits)-1)])
                    #time.sleep(int(lio.window_walk[:-1]))
                    sys.path.append(os.getcwd()+'/queries/')
                    #start_queries=Process(target = lio.query_proc_start(),)
                    thready=threading.Thread(target=self.query_proc_start, args=())
                    thready.daemon=True
                    thready.start()
		    time.sleep(10)

                print ("window has walked forward "+str(self.window_walk[:-1])+" seconds")
                then=eng_now
                eng_now=self.get_epoch_now()
                hits_update=self.flatten_dict(self.get_hits(then, eng_now))
                if len(hits_update)!= 0:
                    df_hits_update = pd.DataFrame(hits_update)
                    #print "length of new dataframe for merging"
                   # print len(df_hits_update)
		    self.lock.acquire()
                    df_hits = pd.concat([df_hits, df_hits_update], ignore_index=True)
		    self.lock.release()
                    del df_hits_update
                    df_hits.sort_values('@timestamp')
                    print("cyle has recieved new records and will remove old records from window")
                    #get the time stamp when all older records should be deleted
                window_cutoff = eng_now-int(self.window_interval)
                before_cutoff = len(df_hits)
		self.lock.acquire()
                df_hits = df_hits[df_hits['@timestamp'] > window_cutoff]
                self.lock.release()
		after_cutoff= len(df_hits)
		
                print("cyle has recieved "+ str(len(hits_update))+" new records and will remove "+str(before_cutoff-after_cutoff)+" old records from window")      
                print("cycle number: "+ str(cycle_num)+" complete, now waiting before window walks" )
                cycle_num+= 1  
                #print("cycle number: "+ str(cycle_num))
                time.sleep(int(self.window_walk[:-1]))

