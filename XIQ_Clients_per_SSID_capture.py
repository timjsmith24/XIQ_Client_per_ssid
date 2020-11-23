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

# function that makes the API call with the provided url
# if pageCount is defined (all calls per hour after initial call) if the call fails they will be added to the secondtry list 
def get_api_call(url, page=0, pageCount=0):
	## used for page if pagesize is set manually
	if pagesize:
		url = "{}&pageSize={}".format(url, pagesize)
	## the first call will not show as the data returned is used to collect the total count of Clients which is used for the page count
	#print(f"####{url}####")
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
				failmsg = (f"Status Code {data['error']['status']}: {data['error']['message']}")
				raise TypeError(f"API Failed with reason: {failmsg} - on API {url}")
		return data

#builds a dictionary of SSIDs with a list of connected clientId. This is then later used to get the count of clients connected to the SSID
def clientCount(data):
	global ssidlist
	for client in data['data']:
		if client['ssid'] not in ssidlist:
			ssidlist[client['ssid']]=[]
		ssidlist[client['ssid']].append(client['clientId'])

def faillist_attempt():
	global faillist
	templist = {}
	faildic = {}
	while faillist:
		removelist = []
		countoffailures = len(faillist)
		prompt_user = input(f"There are {countoffailures} API calls that have failed attempts. Would you like to rety these? (y/n)")
		while prompt_user.lower() != 'y' and prompt_user.lower() != 'n':
			prompt_user = input("Please enter 'y' or 'n'")
		if prompt_user.lower() == 'n':
			for failurltime in faillist:
				print(failurltime)
			return faildic	
		elif prompt_user.lower() == 'y':
			failcount = 1
			for failurltime in faillist:
				print(f"Trying {failcount} of {len(faillist)}",end=": ")
				failurl, failtime = failurltime.split("::")
				try:
					data = get_api_call(failurl)
				except TypeError as e:
					
					print("Failure")
					print(f"{e}")
					
				except HTTPError as e:
					
					print("Failure")
					print(f"{e}")
					
				except:
					
					print("Failure")
					print(f"unknown API error: on API {failurl}")
					
				else:
					faildic[failtime]={}
					for client in data['data']:
						if client['ssid'] not in templist:
							templist[client['ssid']]=[]
							templist[client['ssid']].append(client['clientId'])
					for ssid in templist:
						faildic[failtime][ssid]=len(templist[ssid])
					removelist.append(f"{failurl}::{failtime}")
					print("Success")
				failcount += 1
		for item in removelist:
			faillist.remove(item)		
	return faildic
		
	
def main():
	global today
	global API_start_time
	global secondtry
	filenamedate = today.strftime('%Y-%m-%d_%H00')
	
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
		url = "{}/xapi/v1/monitor/clients?ownerId={}&startTime={}&endTime={}".format(baseurl, ownerId, startTime, endTime)

		# default values for next while loop
		pageCount = 0
		success = 0 
		count = 1
		
		# initial API call will try 5 times and if fails script will terminate.
		while success == 0:
			if count > 5:
				print(f"API call has failed more than 5 times: {url}")
				prompt_user = input('Would you like to continue trying 5 more times? (y/n)')
				while prompt_user.lower() != 'y' and prompt_user.lower() != 'n':
					prompt_user = input("Please enter 'y' or 'n'")
				if prompt_user.lower() == 'y':
					count = 0
				elif prompt_user.lower() == 'n':
					print("Please try running the following API call in 'other script'.")
					print(f"{url}")

					prompt_user = input("\nWould you like to continue with the next iteration? (y/n)")
					while prompt_user.lower() != 'y' and prompt_user.lower() != 'n':
						prompt_user = input("Please enter 'y' or 'n'")
					if prompt_user.lower() == 'y':
						print(f"Skipping {API_start_time}")
						success = 2
						break
					elif prompt_user.lower() == 'n':
						exit()					
			try:
				data = get_api_call(url)
			except TypeError as e:
				count+=1
				print(f"{e} - attempt {count} of 5")		
			except HTTPError as e:
				print(f"{e}")		
				prompt_user = input("Would you like to try this call again? (y/n)")
				while prompt_user.lower() != 'y' and prompt_user.lower() != 'n':
					prompt_user = input("Please enter 'y' or 'n'")
				if prompt_user.lower() == 'y':
					count+=1
					print(f"{e} - attempt {count} of 5")
				elif prompt_user.lower() == 'n':
					if not data:
						data = {}
					success = 2
					break
			except:
				print(f"unknown API error: on API {url}")
				prompt_user = input("Would you like to try this call again? (y/n)")
				while prompt_user.lower() != 'y' and prompt_user.lower() != 'n':
					prompt_user = input("Please enter 'y' or 'n'")
				if prompt_user == 'y':
					count+=1
					print(f"Unknown API error - attempt {count} of 5")
				elif prompt_user == 'n':
					success = 2
					break
			else:
				print("successful connection")
				success = 1
		if success == 2:
			continue
		
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
				pagedurl = '{}&page={}'.format(url, page)
				try:
					data = get_api_call(pagedurl,page=page,pageCount=pageCount)
				except TypeError as e:
					print(f"{e}")
					secondtry.append(pagedurl)
					continue
				except HTTPError as e:
					print(f"{e}")
					secondtry.append(pagedurl)
					continue
				except:
					print(f"unknown API error: on API {pagedurl}")
					secondtry.append(pagedurl)
					continue

				clientCount(data)
		
		# checks if there are any API calls to try again
		if secondtry:
			print(f"\nThere were {len(secondtry)} API calls that failed\n")
			retrycount = 1
			for url in secondtry:
				print(f"Retry {retrycount} of {len(secondtry)}",end=": ")
				try:
					data = get_api_call(url)
				except TypeError as e:
					faillist.append(f"{url}::{startTime}")
					print("Failure - added to Failed list")
					print(f"{e}")
					retrycount += 1
					continue
				except HTTPError as e:
					faillist.append(f"{url}::{startTime}")
					print("Failure - added to Failed list")
					print(f"{e}")
					retrycount += 1
					continue
				except:
					faillist.append(f"{url}::{startTime}")
					print("Failure - added to Failed list")
					print(f"unknown API error: on API {url}")
					retrycount += 1
					continue
				print(f"Successful")
				retrycount += 1
				clientCount(data)
			print("\n")
			
		# adds a dictionary inside of ssid_dic with the value of the startTime
		ssid_dic[startTime]={}
		for ssid in ssidlist:
			# adds each ssid and the count of clients into the startTime dictionary
			ssid_dic[startTime][ssid]= len(ssidlist[ssid])
 
		# over writes the json file with the collected data which includes:
		### all data imported from the data.json file at the beginning
		### all data from previous API_start_time values while the script has been running
		### current API_start_time data
		with open('{}/{}_data.json'.format(PATH,filenamedate), 'w') as f:
			json.dump(ssid_dic, f)

		print(f"completed capture at {API_start_time}\n")
		
		# adds hour iteration to the API_start_time for the next loop
		API_start_time = API_start_time + datetime.timedelta (hours=iteration_hours)
		# empties the secondtry list for the next loop
		secondtry = []
	# if any APIs fail the secondtry they are added to the faillist list. 
	# this prints the list to be collected seperately

	if faillist:
		faileddata = faillist_attempt()
		for starttime in faileddata:
			if starttime not in ssid_dic:
				ssid_dic[starttime]={}
			for failedssid in faileddata[starttime]:
				if failedssid not in ssid_dic[starttime]:
					ssid_dic[starttime][failedssid] = faileddata[starttime][failedssid]
				else:
					totalclientcount = ssid_dic[starttime][failedssid] + faileddata[starttime][failedssid]
					ssid_dic[starttime][failedssid] = totalclientcount

	# over writes the json file with the collected data which includes:
	### all data imported from the data.json file at the beginning
	### all data from previous API_start_time values while the script has been running
	### current API_start_time data from failedlist

	with open('{}/{}_data.json'.format(PATH,filenamedate), 'w') as f:
		json.dump(ssid_dic, f)

	#print(ssid_dic)
	

if __name__ == '__main__':
	main()
