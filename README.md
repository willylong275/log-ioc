Welcome to logIoc, this is definitely a work in progress!

Essentially logIoc has one purpose, to provide a simple way to interact with logs in elasticsearch and provide an easy modular way to add "questions of the network" in the form of query scripts.

This was built and currently alerts using log data from windows sysinternals sysmon, future queries will alert from linux, infrastucture, hypervisor and native windows. In the docs dir i added a copy of my sysmon configuration xml file. 

Of note: this class will build and use a new index in your es instance for management and for log-alerts. The name of the management index is configured in configs/logIoc.ini. The log-alert index is currently configured as "logstash-log-alert-YYYY.MM.DD". The log-alert index must be added to your kibana instance.

The class build and maintains a moving window of logs in a pandas dataframe. This dataframe is accessible for any query added to the queries dir. If an IOC is identified within log messages the class provides the "log_alert" method to add an alert record to your ES instance.

The width of the window in time is configured in configs/logIoc.ini as well as the wait period before the window walks to "now".

Also configured in logIoc.ini is the cycle rate for all queries in the queries dir. Queries can be configured to run at any interval. Utilizing the "update_last_timestamp" method each query will never analyze the same log message twice. An example query will be in the queries dir in the near future.

End state, focus on parsing list of results for indicators of compromise in logs and let logIoc handle elasticsearch.

