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
	file1=open(os.path.abspath('docs/unchecked-hashes'),"r+w")
    	unchecked_hashes = file1.readlines()
	with open(os.path.abspath('docs/checked-hashes')) as file2:
                checked_hashes = file2.readlines()

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
		sha1=thash.split(',')[0]
		md5=thash.split(',')[1]
		if thash in checked_hashes:
			print "found a hash that has already been checked"	
		if thash in unchecked_hashes:
			print "found a hash that is already recorded for checking"
		else:
			print thash
			print sha1
			writelist.append(thash)
			#file1.write(sha1)
			#file1.write((md5)
#	file1.close()
#	file2.close()	
	print writelist
	for line in writelist:
		file1.write("%s\n" % line)
	print hashes
	print item
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

