# XIQ Collecting Client Count per SSID
## XIQ_Clients_per_SSID_capture.py
### Purpose
This script will collect the number of clients connected to each SSID over the last 24 hours. The amount of times data is collected can be adjusted but default is set to collect every hour. This data is stored in the data.json file.
### User Input Data
interation_hours (default 1 hour). This is how frequently the script will pull data

###### line 20
```
iteration_hours = 1
```
API info.

###### lines 23-28
```
CLIENTID = 'e4aac13f'
SECRET = '6593120f5e4360af47918d70c8df9924'
REDIRECT_URI = 'https://bmatwifi.com'
TOKEN = '7FKFvMHIWvOa2IEceBrNJ_RC_b01-k1pe4aac13f'
ownerId = '94009'
DATACENTER = 'ava'
```
#### Optional: 
pagesize (default is ''). This allows the page size of the API call to be adjusted from the default 500 clients. Added desired number between the ''. (ie '100' for 100 clients per call)

###### line 44
```
pagesize = ''
```

### More information
This script will use the current UTC time and collect client counts per SSID over the last 24 hours. collection is done every hour but this can be adjusted by changing the iteration_hours variable. 

in addition to client info the initial API call will return the total number of clients as well as how many clients were included in this AP call. The default will only return the first 500 clients but that can be adjusted (preferably lower) with the pagesize variable.

#!/usr/bin/env python3
# Used to setting times in API call
# Change to correct values 
# Used to build API call
# Global Objects
#Value can be added to set page size. If nothing in quotes default value will be used (500)
# initial API call
# if pageCount is defined (all calls per hour after initial call) if the call fails they will be added to the secondtry list 
## used for page if pagesize is set manually
## the first call will not show as the data returned is used to collect the total count of Clients which is used for the page count
# Used for the 2nd try for API call. If failed they will be added to the faillist list
# Python 3.6
#builds a dictionary of SSIDs with a list of connected clientId. This is then later used to get the count of clients connected to the SSID
#checks if data.json file exists. If it exists it loads it into the ssid_dic dictionary. If not creates a empty ssid_dic dictionary
# loops until API_start_time (current time - 1 day) equals current time. At the end of the loop 1 hour is added to API_start_time
# gets the startTime in correct format to be added to the API call
# gets the endTime in correct format to be added to the API call
# adds the base url info as well as the startTime and endTime to the url
# default values for next while loop
# initial API call will try 5 times and if fails script will terminate.
# gets total count of clients and the count of clients in the initial call
# checks to see if client info is missing from initial call
# calculates the number of pages needed to get all client info (rounded up)
# adds a dictionary inside of ssid_dic with the value of the startTime
# adds each ssid and the count of clients into the startTime dictionary
# checks if there are any API calls to try again
# over writes the json file with the collected data which includes:
### all data imported from the data.json file at the beginning
### all data from previous API_start_time values while the script has been running
### current API_start_time data
# adds hour iteration to the API_start_time for the next loop
# empties the secondtry list for the next loop
# if any APIs fail the secondtry they are added to the faillist list. 
# this prints the list to be collected seperately