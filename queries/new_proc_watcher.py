#!/usr/bin/env python
def main(df_hits, lock):
	from logIoc import logIoc
	import os
	lio = logIoc()
	print "executing proc watcher query"
	#print ("total hits sent to proc watcher was " + str(len(df_hits))) 
	id1_hits=[]
	hashes=[]
	writelist=[]
	file1=open(os.path.abspath('docs/unchecked-hashes'),"r+")
        unchecked_hashes = [line.rstrip('\n').split(',')[0] for line in file1]
	file2=open(os.path.abspath('docs/checked-hashes'),"r")
        checked_hashes = [line.rstrip('\n').split(',')[0] for line in file2]
	
	#for line in df_hits[df_hits['@timestamp'] > window_cutoff]i
	lock.acquire()
	#print "*************************************"
	#print df_hits.iloc[0]['@timestamp']

	lio.update_last_timestamp('new_proc_watcher', df_hits.iloc[(len(df_hits)-1)]['@timestamp'])
	local_df=df_hits[(df_hits['@timestamp'] > lio.get_last_timestamp('new_proc_watcher')) & (df_hits['_source.event_id'] == 1)]
	#print (df_hits['@timestamp'])
	#print (lio.get_last_run('new_proc_watcher'))
	#for item in df_hits[df_hits['@timestamp'] > lio.get_last_run('new_proc_watcher')]:
	#for item in df_hits['@timestamp'] > lio.get_last_run('new_proc_watcher'):
	#	id1_hits.append(item)

	#for item in id1_hits:
	#	print type(item)
	lock.release()
	#print (lio.get_epoch_now())
	#print local_df['@timestamp']
	#for row in local_df.itertuples():
	#	print row 
	#if len(local_df)!= 0:
	#	print (len(local_df))
	#	print local_df['_source.event_data.Hashes']

		#if df_hits[df_hits['_source.event_id']==1:
		#	id1_hits.append(item.copy())
	
			
	for index, row in local_df.iterrows():
	#	tdict = {}
		thash = row["_source.event_data.Hashes"]#]item.get('_source', {}).get('event_data', {}).get('Hashes')
	#	thost = item.get('_source', {}).get('beat', {}).get('hostname')
	#	ttime = item.get('_source', {}).get('@timestamp')
	#	tpid = item.get('_source', {}).get('process_id')
		timagename = row["_source.event_data.Image"]#item.get('_source', {}).get('event_data', {}).get('Image')
  	#	tdict={"_type":"image_hashes", "_index": lio.logioc_index, "hash":thash, "host":thost, "execution_time": ttime, "pid": tpid, "image": timagename}
	#	hashes.append(tdict)
	#	item['_type']= 'running-procs'
	#	item['_index'] = 'logioc-management'
		tempvar=str(thash).split(',')[0]
	#	
		if tempvar in checked_hashes:
			print "hash noticed that is already on deck for checking"
		if tempvar in unchecked_hashes:
			print "Captured hash that has already been checked with 0 bad results"
		else:
			#file1.append(str(thash+','+timagename))
			writelist.append(str(str(thash)+','+str(timagename)))
	if len(writelist)!=0:
		print "The following hashes will be added to added to uncheck_hashes for virus total query"
		print writelist
		writelist=set(writelist)
		for line in writelist:
			file1.write("%s\n" % line)
	file1.close()
	file2.close()	
	
#	print ("cycle caught "+ str(len(hashes))+" hashes")				
#	if len(id1_hits)!=0:
#		lio.bulk_index("logioc-management", id1_hits)
#		lio.bulk_index(lio.logioc_index, hashes)
#	print ("from all hits "+ str(len(id1_hits)) + " were event id 1")
#	id1_hits=[]
#	
#	hits = []
	return 


if __name__ == "__main__":
        main()
	exit()

