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
