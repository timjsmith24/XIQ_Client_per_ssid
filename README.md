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

The output of the script will be a *_data.json file. The file name will include the current data and time. so for example if the script was ran on Nov 23, 2020 at 5pm the file name would be 112320_1700_data.json.

in addition to client info the initial API call will return the total number of clients as well as how many clients were included in this AP call. The default will only return the first 500 clients but that can be adjusted (preferably lower) with the pagesize variable. Using the total number of clients from this AP call this script will calculate how many pages of API calls will need to be made to collect all the client information. API urls are built and the information collected. 

At the end of each iteration the script will write all data collected to the data.json file. So iteration 2 will write over the data.json file created at the end of iteration 2 but will include all data from iteration 1 and 2, as well as any data that was in the data.json file when the script was started. 


### API Errors and User input
Any API call that fails will print and Error message on the screen. 

If the script trys and fails 5 times during the intial call of a time iteration the user will be prompted to enter if they would like to continue trying 5 additional times. The user will need to enter a 'y' or 'n'. If 'y' is entered the script will try that same API call 5 times. If 'n' is entered the script will bypass that time iteration and move to the next. Some API Error will ask for user input immediately
```
unknown API error: on API https://ava.extremecloudiq.com/xapi/v1/monitor/clients?ownerId=94009&startTime=2020-11-20T19:00:00.000Z&endTime=2020-11-20T20:00:00.000Z
Would you like to try this call again? (y/n)y
Unknown API error - attempt 2 of 5
```

If the script fails on one of the pagination API calls the script will automatically try a second time after all other pages of the iteration have finished.
```
There were 3 API calls that failed

Retry 1 of 3: Successful
Retry 2 of 3: Successful
Retry 3 of 3: Failure - added to Failed list
unknown API error: on API https://ava.extremecloudiq.com/xapi/v1/monitor/clients?ownerId=94009&startTime=2020-11-21T19:00:00.000Z&endTime=2020-11-21T20:00:00.000Z&page=8
```

If the call fails a second time the API link will be saved in a list and be presented at the end of the script allowing the user to keep attempting. 
```
There are 1 API calls that have failed attempts. Would you like to rety these? (y/n)y
Trying 1 of 1: Success
```
If no is selected for the failed list the API links will be printed so the infomation can be gathered a different way.
```
There are 1 API calls that have failed attempts. Would you like to rety these? (y/n)n
https://ava.extremecloudiq.com/xapi/v1/monitor/clients?ownerId=94009&startTime=2020-11-21T19:00:00.000Z&endTime=2020-11-21T20:00:00.000Z&page=5::2020-11-21T19:00:00.000Z
```