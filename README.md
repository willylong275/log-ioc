Welcome to logIoc, this is definitely a work in progress!

Essentially logIoc has one purpose, to provide a simple way to repeatedly query elasticsearch and return a list of dictionarys as results to each query.

The class has two modes of operation, batch querys and individual queries. Both can be run at once with run-all.sh

The batch query function will gather all records from its last run time and present them as a list of hits to all queries in the batch_queries directory.
The time cycle for the batch query loop is configured in configs/logIoc.ini

The individual query functionality comes from a saeparate method. This gives the analyst the abillity to specify an amount of time to pass between gathering all records. These records again are presented to that query as a list of hits. The individual query method will get all queries in the /queries dir and then look for the analyst time cycle to be configured for each query in /queries. 

currently all wait configs in logIoc.ini are in seconds.

Also untill fixed when using the individual queries functionality, a thread continues to run for each query after hitting control+c. Control+z then killall python will stop all threads.

End state, focus on parsing list of results for indicators of compromise in logs and let logIoc handle elasticsearch.

If indicator from your queries are found, a future method will index a "log-alert" into your es instance. 
