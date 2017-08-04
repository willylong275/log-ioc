#!/usr/bin/env python
def main(df_hits, lock):
	from logIoc import logIoc
	import os
	lio = logIoc()
	query = 'windows_login'
	print "executing windows login query"
	lock.acquire()
	lio.update_last_timestamp(query, df_hits.iloc[(len(df_hits)-1)]['@timestamp'])
	#lio.update_last_timestamp('windows_account_creation', df_hits.iloc[(len(df_hits))]['@timestamp'])
	local_df=df_hits[(df_hits['@timestamp'] > lio.get_last_timestamp(query)) & (df_hits['_source.event_id'] == 4624)]
	lock.release()
	
	if len(local_df) != 0:			
		for index, row in local_df.iterrows():
			host = row["_source.computer_name"]
			username = row["_source.event_data.TargetUserName"]
			orig_id = row["_id"]
			logon_type = row["_source.event_data.LogonType"]
			workstation_name = row["_source.event_data.WorkstationName"]
			if logon_type == "2" and "DWM" not in username:
				message=str("user: "+str(username)+" successfully logged on to "+ str(host))
				lio.log_alert(orig_id, message, "info",host)
	return 	


if __name__ == "__main__":
        main()
	exit()

