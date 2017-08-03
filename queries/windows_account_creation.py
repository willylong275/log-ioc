#!/usr/bin/env python
def main(df_hits, lock):
	from logIoc import logIoc
	import os
	lio = logIoc()
	
	print "executing windows account creation query"
	lock.acquire()
	lio.update_last_timestamp('windows_account_creation', df_hits.iloc[(len(df_hits)-1)]['@timestamp'])
	#lio.update_last_timestamp('windows_account_creation', df_hits.iloc[(len(df_hits))]['@timestamp'])
	local_df=df_hits[(df_hits['@timestamp'] > lio.get_last_timestamp('windows_account_creation')) & (df_hits['_source.event_id'] == 4720)]
	lock.release()
	
	if len(local_df) != 0:			
		for index, row in local_df.iterrows():
			host = row["_source.computer_name"]
			new_user = row["_source.event_data.TargetUserName"]
			orig_id = row["_id"]
			by_user = row["_source.event_data.SubjectUserName"]
			message=str("New user: "+str(new_user)+" created on windows host "+ str(host)+" by username: "+ str(by_user))
			lio.log_alert(orig_id, message, "warning",host)
	return 	


if __name__ == "__main__":
        main()
	exit()

