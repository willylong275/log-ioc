#!/usr/bin/env python

def main(df_hits, lock):
	from logIoc import logIoc
	lio=logIoc()
	import urllib, urllib2, os, json, time
	time.sleep(61)
	file1=open(os.path.abspath('docs/unchecked-hashes'),"r")
	unchecked_hashes = [line.rstrip('\n') for line in file1]
	file1.close()
	if len(unchecked_hashes)>5:
		file2=open(os.path.abspath('docs/checked-hashes'),"r+w")
		results_list=[]
		checked_hashes = [line.rstrip('\n') for line in file2]
		base = 'https://www.virustotal.com/vtapi/v2/'

		for list_line in range(1,5):
    			got_hash = unchecked_hashes[list_line].split(',')[0].split('=')[1]
    			param = {'resource':got_hash, 'apikey': lio.api_key}
    			url = base + "file/report"
    			data = urllib.urlencode(param)
    			result = urllib2.urlopen(url,data)
    			jdata =  json.loads(result.read())
    			if jdata['positives']==0:
        			result_line = str(str(unchecked_hashes[list_line])+", Response_code: "+ str(jdata["response_code"])+","+" positives: "+str(jdata["positives"])+'/'+str(jdata["total"]))
        			#print (result_line)
        			results_list.append(result_line)
                        elif jdata['positives']>=1:
                                result_line = str(str(unchecked_hashes[list_line])+", Response_code: "+ str(jdata["response_code"])+","+" positives: "+str(jdata["positives"])+'/'+str(jdata["total"]))
                                print "WARNING HASH CHECK FOUND POSITIVE IN VIRUS TOTAL RESULTS"
				print (result_line)
				
                                results_list.append(result_line)
    			else:
        			print (jdata)
		del unchecked_hashes[1:5]
		for line in results_list:
    			file2.write("%s\n" % line)
		results_list=[]
		file2.close()
		file1=open(os.path.abspath('docs/unchecked-hashes'),"w")
		for line in unchecked_hashes:
    			file1.write("%s\n" % line)
		file1.close()
		return
	else:
		print ("unchecked hash list less than 4 lines, skipping processing")
