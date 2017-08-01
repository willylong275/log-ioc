#!/usr/bin/env python
def main(df_hits, lock):
	from logIoc import logIoc
	import os
	lio = logIoc()
	
	print "\nconfigured wait time elasped, executing proc watcher query"
	print "executing proc watcher query"
	#print ("total hits sent to proc watcher was " + str(len(df_hits))) 
	id1_hits=[]
	hashes=[]
	writelist=[]
	file1=open(os.path.abspath('docs/unchecked-hashes'),"r+")
        unchecked_hashes = [line.rstrip('\n').split(',')[0] for line in file1]
	file2=open(os.path.abspath('docs/checked-hashes'),"r")
        checked_hashes = [line.rstrip('\n').split(',')[0] for line in file2]
	
	lock.acquire()
	lio.update_last_timestamp('new_proc_watcher', df_hits.iloc[(len(df_hits)-1)]['@timestamp'])
	local_df=df_hits[(df_hits['@timestamp'] > lio.get_last_timestamp('new_proc_watcher')) & (df_hits['_source.event_id'] == 1)]
	lock.release()
	
	if len(local_df) != 0:			
		for index, row in local_df.iterrows():
			thash = row["_source.event_data.Hashes"]#]item.get('_source', {}).get('event_data', {}).get('Hashes')
			timagename = row["_source.event_data.Image"]#item.get('_source', {}).get('event_data', {}).get('Image')
			tempvar=str(thash).split(',')[0]
			if tempvar in checked_hashes:
				print "hash noticed that is already on deck for checking"
			if tempvar in unchecked_hashes:
				print "Captured hash that has already been checked with 0 bad results"
			else:
				writelist.append(str(str(thash)+','+str(timagename)))
		if len(writelist)!=0:
			writelist=set(writelist)
			for line in writelist:
				file1.write("%s\n" % line)
	file1.close()
	file2.close()	
	return 


if __name__ == "__main__":
        main()
	exit()

