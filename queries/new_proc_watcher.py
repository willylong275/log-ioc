#!/usr/bin/env python
def main(hits):
	from logIoc import logIoc
	lio = logIoc()
        print lio.get_utc_now()
	print "executing proc watcher query"
	print ("total hits sent to proc watcher was " + str(len(hits))) 
	id1_hits=[]
	for line in hits:
		if line.get('_source', {}).get('event_id') == 1:
			id1_hits.append(line.copy())
	for line in id1_hits:
		hashes = line.get('_source', {}).get('event_data', {}).get('Hashes')
		print hashes
		line['_type']= 'running-procs'
		line['_index'] = 'logioc-management'
					
	if len(id1_hits) != 0:
		print id1_hits[0]
		lio.bulk_index("logioc-management", id1_hits)
	print ("from all hits "+ str(len(id1_hits)) + " were event id 1")
	hits = []
	#lio=logIoc()
	return 


if __name__ == "__main__":
        main()

