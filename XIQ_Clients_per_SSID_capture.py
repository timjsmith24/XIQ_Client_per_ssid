#!/usr/bin/env python3
import requests
import json
import math
import time
import os
import datetime
import pytz
from requests.exceptions import HTTPError

UTC = pytz.utc 
today = datetime.datetime.now(UTC)
PATH = os.path.dirname(os.path.abspath(__file__))

# Used to setting times in API call
API_start_time = today - datetime.timedelta (days=1)
API_start_time = API_start_time.strftime('%Y-%m-%dT%H:00:00.000Z')
API_start_time = datetime.datetime.strptime(API_start_time, '%Y-%m-%dT%H:%M:%S.000Z')
API_start_time = UTC.localize(API_start_time)
iteration_hours = 1

# Change to correct values 
CLIENTID = 'e4aac13f'
SECRET = '6593120f5e4360af47918d70c8df9924'
REDIRECT_URI = 'https://gthill.com'
TOKEN = '7FKFvMHIWvOa2IEceBrNJ_RC_b01-k1pe4aac13f'
ownerId = '94009'
DATACENTER = 'ava'

# Used to build API call
baseurl = 'https://{}.extremecloudiq.com'.format(DATACENTER)
HEADERS= {
	'X-AH-API-CLIENT-ID':CLIENTID,
	'X-AH-API-CLIENT-SECRET':SECRET,
	'X-AH-API-CLIENT-REDIRECT-URI':REDIRECT_URI,
	'Authorization':'Bearer {}'.format(TOKEN),
	'Content-Type': 'application/json'
	}

# Global Objects
ssidlist = {}
secondtry = []
faillist = []
pagesize = '' #Value can be added to set page size. If nothing in quotes default value will be used (500)


# initial API call
# if pageCount is defined (all calls per hour after initial call) if the call fails they will be added to the secondtry list 
def get_api_call(url,page=0,pageCount=0):
	url = '{}&ownerId={}&page={}'.format(url, ownerId, page)

	## used for page if pagesize is set manually
	if pagesize:
		url = url+(f"&pageSize={pagesize}")
	## the first call will not show as the data returned is used to collect the total count of Clients which is used for the page count
	if pageCount != 0:
		print(f"API call on {page} of {pageCount}")

	try:
		r = requests.get(url, headers=HEADERS, timeout=10)
	except HTTPError as http_err:
		if pageCount != 0:
			secondtry.append(url)
		raise HTTPError(f'HTTP error occurred: {http_err} - on API {url}')  
	except Exception as err:
		if pageCount != 0:
			secondtry.append(url)
		raise TypeError(f'Other error occurred: {err}: on API {url}')
	else:
		data = json.loads(r.text)
		if 'error' in data:
			if data['error']:
				failmsg = data['error']['message']
				raise TypeError(f"API Failed with reason: {failmsg} - on API {url}")
		return data

# Used for the 2nd try for API call. If failed they will be added to the faillist list
def Second_api_call(url):
	try:
		r = requests.get(url, headers=HEADERS, timeout=10)
	except HTTPError as http_err:
		raise HTTPError(f'\nAPI CALL FAILED SECOND TRY\nHTTP error occurred: {http_err} - on API {url}')  # Python 3.6
	except Exception as err:
		raise TypeError(f'\nAPI CALL FAILED SECOND TRY\nOther error occurred: {err}: on API {url}')
	else:
		data = json.loads(r.text)
		if 'error' in data:
			if data['error']:
				failmsg = data['error']['message']
				raise TypeError(f"\nAPI CALL FAILED SECOND TRY\nAPI Failed with reason: {failmsg} - on API {url}")
		return data

#builds a dictionary of SSIDs with a list of connected clientId. This is then later used to get the count of clients connected to the SSID
def clientCount(data):
	global ssidlist
	for client in data['data']:
		if client['ssid'] not in ssidlist:
			ssidlist[client['ssid']]=[]
		ssidlist[client['ssid']].append(client['clientId'])


def main():
	global today
	global API_start_time
	global secondtry
	#checks if data.json file exists. If it exists it loads it into the ssid_dic dictionary. If not creates a empty ssid_dic dictionary
	if not os.path.exists('data.json'):
		ssid_dic = {}
	else:
		with open('{}/data.json'.format(PATH), 'r') as f:
			try:
				ssid_dic = json.load(f)
			except ValueError:
				ssid_dic = {}

	# loops until API_start_time (current time - 1 day) equals current time. At the end of the loop 1 hour is added to API_start_time
	while today > API_start_time:
		# gets the startTime in correct format to be added to the API call
		startTime = API_start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		# gets the endTime in correct format to be added to the API call
		endTime = API_start_time + datetime.timedelta (hours=iteration_hours)
		endTime = endTime.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		print(f"collecting client data for {startTime}")
		# adds the base url info as well as the startTime and endTime to the url
		url = "{}/xapi/v1/monitor/clients?startTime={}&endTime={}".format(baseurl, startTime, endTime)

		# default values for next while loop
		pageCount = 0
		success = 0 
		count = 0

		# initial API call will try 5 times and if fails script will terminate.
		while success == 0:
			if count > 5:
				success =2
				print(f"API call has failed more than 5 times: {url}")
				exit()
			try:
				data = get_api_call(url)
			except TypeError as e:
				count=+1
				print(f"{e} - attempt {count} of 5")
				
			except HTTPError as e:
				print(f"{e}")
				exit()
			except:
				print(f"unknown API error: on API {url}")
				exit()
			else:
				print(f"successful connection")
				success = 1
		# gets total count of clients and the count of clients in the initial call
		totalCount = data['pagination']['totalCount']
		countInPage = data['pagination']['countInPage']
	
		clientCount(data)
		
		# checks to see if client info is missing from initial call
		if countInPage < totalCount:
			# calculates the number of pages needed to get all client info (rounded up)
			pageCount = math.ceil(int(totalCount)/int(countInPage))
			for page in range(int(pageCount)):
				page+=1
				try:
					data = get_api_call(url,str(page),pageCount)
				except TypeError as e:
					print(f"{e}")
					continue
				except HTTPError as e:
					print(f"{e}")
					continue
				except:
					print(f"unknown API error: on API {url}")
					continue
				clientCount(data)
		# adds a dictionary inside of ssid_dic with the value of the startTime
		ssid_dic[startTime]={}
		for ssid in ssidlist:
			# adds each ssid and the count of clients into the startTime dictionary
			ssid_dic[startTime][ssid]= len(ssidlist[ssid])
		# checks if there are any API calls to try again
		if secondtry:
			for url in secondtry:
				try:
					data = Second_api_call(url)
				except TypeError as e:
					faillist.append(url)
					print(f"{e}")
					continue
				except HTTPError as e:
					faillist.append(url)
					print(f"{e}")
					continue
				except:
					faillist.append(url)
					print(f"unknown API error: on API {url}")
					continue
				print(f"Retry Successful for {url}")
				clientCount(data)
		# over writes the json file with the collected data which includes:
		### all data imported from the data.json file at the beginning
		### all data from previous API_start_time values while the script has been running
		### current API_start_time data
		with open('{}/data.json'.format(PATH), 'w') as f:
			json.dump(ssid_dic, f)
		
		print(f"completed capture at {API_start_time}")
		# adds hour iteration to the API_start_time for the next loop
		API_start_time = API_start_time + datetime.timedelta (hours=iteration_hours)
		# empties the secondtry list for the next loop
		secondtry = []
	# if any APIs fail the secondtry they are added to the faillist list. 
	# this prints the list to be collected seperately
	if faillist:
		print("\nThese API calls failed 2 times and data was not collected:")
		for failurl in faillist:
			print(failurl)
		
if __name__ == '__main__':
	main()