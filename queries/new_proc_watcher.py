#!/usr/bin/env python
def main(hits):
        print "executing proc watcher query"
	print "&&&&&&&&&&&&&&&&&"
	#print hits
	id1_hits=[]
	for line in hits:
		if line.get("event_id", "1"):
			id1_hits=hits.append(line)
			
	hits = []
	lio=logIoc()
        return 


if __name__ == "__main__":
        main()

