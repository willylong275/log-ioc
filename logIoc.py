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
        #from datetime import datetime
        import datetime
        from elasticsearch import Elasticsearch, helpers
        from multiprocessing import Process
        import threading
except:
        print("Please make sure you have required modules installed. pip -r requirements.txt or pip install elasticsearch")
	exit()
class logIoc(object):
        config = ConfigParser.RawConfigParser()
        config.read(os.getcwd()+'/configs/logIoc.ini')
        sys.path.append(os.getcwd()+'/queries/')

        def __init__(self):
                config = ConfigParser.RawConfigParser()
                config.read(os.getcwd()+'/configs/logIoc.ini')
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
                self.api_key= config.get('virus_total', 'api_key')
                self.query_list = queries
                self.es= Elasticsearch([self.es_host], port=self.es_port)
                self.init_done = False
		self.lock=threading.Lock()		

	def log_alert(self, offending_id, message, severity, host):
		print ("log alert added to elasticsearch")
		today=datetime.date.today().strftime('%Y.%m.%d')
		alert_json={ "timestamp": self.get_utc_now(),"severity":severity, "host":host,"message":message,"offending_id":offending_id}
                res=self.es.index(index=str("logstash-log-alert-"+today) , doc_type="log-alert",  body=alert_json)
                print(" response: '%s'" % (res))
		alert_file=open("log-alerts.json","a+")
		#alert_file.write('{"timestamp": {0}, "beat_name": "log-alert", "message": {1}, "offending_id": {2}}\n'.format(self.get_utc_now(), message, offending_id))
		#alert_file.write("\n")
		alert_file.write("{ \"timestamp\":\"" + self.get_utc_now()+"\",\"severity\":\"" + severity + "\",\"host\":\""+host+"\",\"message\":\"" + message + "\",\"offending_id\":\"" + offending_id + "\"}" + "\n")
		alert_file.close()
        
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
                utc_now = datetime.datetime.utcnow().isoformat()[:-3]+'Z'
                return utc_now

        def get_epoch_now(self):
                epoch_now = int(time.time() * 1000)
                return epoch_now

        def get_last_run(self, script_name):
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
                print ("last timestamp updated for  "+script_name)
                res=self.es.index(index=self.logioc_index, doc_type=script_name+"-last-timestamp", id=1, body={
                'Script': script_name,
                'last_timestamp_saw': last_timestamp,
                })
                #print(" response: '%s'" % (res))
	
	def get_last_timestamp(self, script_name):
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
                print ("last run updated for "+script_name)
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
                        new_value=calendar.timegm(datetime.datetime.strptime(utc_record, "%Y-%m-%dT%H:%M:%S.%f").timetuple())*1000
                        item['@timestamp']=new_value
                        newHits.append(item)
                return newHits

        def cycler_initialize(self):
            if self.check_index_existance(self.logioc_index)== False:
                print "management index existance returned false"
                print "creating it now..."
                self.create_index(self.logioc_index)

            if self.check_index_existance('logstash-log-alert-2017.08.02')== False:
                print "management index existance returned false"
                self.log_alert("123456789", "Example Log Alert Created by logIoc...happy hunting", "info", "cool-hostname")
	
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
                print ("\nstarting thread to start execute then wait loop for  "+subquery)
                while True:
                        hits=[]
			print ("\nstarting execution of "+subquery)
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
                                thread=threading.Thread(target=self.subprocess_holder_loop, args=(subquery,))
                                thread.daemon=True
                                thread.start()
                                #print ("subquery was "+ subquery)
                while True:
                        time.sleep(1)

        def eng(self):
            cycle_num=1
            while True:
                if cycle_num==1:
                    init_time_start=self.get_epoch_now()
                    hits=self.cycler_initialize()
                    global df_hits
		    self.lock.acquire()
                    df_hits = pd.DataFrame(hits).sort_values('@timestamp')
		    print ("Window Initialization ElasticSearch query returned "+str(len(df_hits))+" records for the entire configured window")
		    self.lock.release()
                    del hits
                    print ("initialization time took "+str((self.get_epoch_now()-init_time_start)/1000)+" seconds")
                    eng_now=self.get_epoch_now()
                    sys.path.append(os.getcwd()+'/queries/')
                    query_thread=threading.Thread(target=self.query_proc_start, args=())
                    query_thread.daemon=True
                    query_thread.start()
		    time.sleep(10)

                print ("window has walked forward "+str(self.window_walk[:-1])+" seconds")
                then=eng_now
                eng_now=self.get_epoch_now()
                hits_update=self.flatten_dict(self.get_hits(then, eng_now))
                if len(hits_update)!= 0:
                    df_hits_update = pd.DataFrame(hits_update)
		    self.lock.acquire()
                    df_hits = pd.concat([df_hits, df_hits_update], ignore_index=True)
		    self.lock.release()
                    del df_hits_update
                    df_hits.sort_values('@timestamp')
                    print("cyle has recieved new records and will remove old records from window")
                window_cutoff = eng_now-int(self.window_interval)
                before_cutoff = len(df_hits)
		self.lock.acquire()
                df_hits = df_hits[df_hits['@timestamp'] > window_cutoff]
                self.lock.release()
		after_cutoff= len(df_hits)
		
                print("cyle has recieved "+ str(len(hits_update))+" new records and will remove "+str(before_cutoff-after_cutoff)+" old records from window")      
                print("cycle number: "+ str(cycle_num)+" complete, now waiting before window walks\n" )
                cycle_num+= 1  
                time.sleep(int(self.window_walk[:-1]))

