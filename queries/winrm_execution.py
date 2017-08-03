#!/usr/bin/env python
def main(df_hits, lock):
	from logIoc import logIoc
	import os
	lio = logIoc()
	query='winrm_execution'
	print "executing windows powershell execution query"
	lock.acquire()
	lio.update_last_timestamp(query, df_hits.iloc[(len(df_hits)-1)]['@timestamp'])
	#lio.update_last_timestamp('windows_account_creation', df_hits.iloc[(len(df_hits))]['@timestamp'])
	local_df=df_hits[(df_hits['@timestamp'] > lio.get_last_timestamp(query)) & (df_hits['_source.event_id'] == 1)]
	lock.release()
	
	if len(local_df) != 0:			
		for index, row in local_df.iterrows():
			host = row["_source.computer_name"]
			parent_image = row["_source.event_data.ParentImage"]
			orig_id = row["_id"]
			command_line = row["_source.event_data.CommandLine"]
			user = row['_source.event_data.User']
			if "wsmprovhost.exe" in str(parent_image):
				message=str("command :"+command_line+" executed via winrm with user: "+user)
				lio.log_alert(orig_id, message, "caution", host)
	return 	


if __name__ == "__main__":
        main()
	exit()

