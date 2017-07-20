#!/usr/bin/env python
def main(hits):
	from logIoc import logIoc
	import os
	lio = logIoc()
	print "executing proc watcher query"
	print ("total hits sent to proc watcher was " + str(len(hits))) 
	id1_hits=[]
	hashes=[]
	writelist=[]
	file1=open(os.path.abspath('docs/unchecked-hashes'),"r+")
        unchecked_hashes = [line.rstrip('\n').split(',')[0] for line in file1]
	file2=open(os.path.abspath('docs/checked-hashes'),"r")
        checked_hashes = [line.rstrip('\n').split(',')[0] for line in file2]

	for item in hits:
		if item.get('_source', {}).get('event_id') == 1:
			id1_hits.append(item.copy())
	for item in id1_hits:
		tdict = {}
		thash = item.get('_source', {}).get('event_data', {}).get('Hashes')
		thost = item.get('_source', {}).get('beat', {}).get('hostname')
		ttime = item.get('_source', {}).get('@timestamp')
		tpid = item.get('_source', {}).get('process_id')
		timagename = item.get('_source', {}).get('event_data', {}).get('Image')
  		tdict={"_type":"image_hashes", "_index": lio.logioc_index, "hash":thash, "host":thost, "execution_time": ttime, "pid": tpid, "image": timagename}
		hashes.append(tdict)
		item['_type']= 'running-procs'
		item['_index'] = 'logioc-management'
		tempvar=thash.split(',')[0]
		
		if tempvar in checked_hashes:
			print "hash noticed that is already on deck for checking"
		if tempvar in unchecked_hashes:
			print "Captured hash that has already been checked with 0 bad results"
		else:
			#file1.append(str(thash+','+timagename))
			writelist.append(str(thash+','+timagename))

	print "The following hashes will be added to added to uncheck_hashes for virus total query"
	print writelist
	writelist=set(writelist)
	for line in writelist:
		file1.write("%s\n" % line)
	file1.close()
	file2.close()	
	
	print ("cycle caught "+ str(len(hashes))+" hashes")				
	if len(id1_hits)!=0:
		lio.bulk_index("logioc-management", id1_hits)
		lio.bulk_index(lio.logioc_index, hashes)
	print ("from all hits "+ str(len(id1_hits)) + " were event id 1")
	id1_hits=[]
	
	hits = []
	return 


if __name__ == "__main__":
        main()

