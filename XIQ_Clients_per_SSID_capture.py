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

API_start_time = today - datetime.timedelta (days=1)
API_start_time = API_start_time.strftime('%Y-%m-%dT%H:00:00.000Z')
API_start_time = datetime.datetime.strptime(API_start_time, '%Y-%m-%dT%H:%M:%S.000Z')
API_start_time = UTC.localize(API_start_time)
iteration_hours = 1


CLIENTID = 'e4aac13f'
SECRET = '6593120f5e4360af47918d70c8df9924'
REDIRECT_URI = 'https://gthill.com'
TOKEN = '7FKFvMHIWvOa2IEceBrNJ_RC_b01-k1pe4aac13f'
ownerId = '94009'
DATACENTER = 'ava'

baseurl = 'https://{}.extremecloudiq.com'.format(DATACENTER)
HEADERS= {
	'X-AH-API-CLIENT-ID':CLIENTID,
	'X-AH-API-CLIENT-SECRET':SECRET,
	'X-AH-API-CLIENT-REDIRECT-URI':REDIRECT_URI,
	'Authorization':'Bearer {}'.format(TOKEN),
	'Content-Type': 'application/json'
	}

ssidlist = {}
secondtry = []
faillist = []
pagesize = '2'

def get_api_call(url,page=0,pageCount=0):
	url = '{}&ownerId={}&page={}'.format(url, ownerId, page)

	## used for page testing
	if pagesize:
		url = url+(f"&pageSize={pagesize}")
	if pageCount != 0:
		print(f"API call on {page} of {pageCount}")

	try:
		r = requests.get(url, headers=HEADERS, timeout=10)
	except HTTPError as http_err:
		if pageCount != 0:
			secondtry.append(url)
		raise HTTPError(f'HTTP error occurred: {http_err} - on API {url}')  # Python 3.6
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
	if not os.path.exists('data.json'):
		ssid_dic = {}
	else:
		with open('{}/data.json'.format(PATH), 'r') as f:
			try:
				ssid_dic = json.load(f)
			except ValueError:
				ssid_dic = {}

	
	while today > API_start_time:
		startTime = API_start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		endTime = API_start_time + datetime.timedelta (hours=iteration_hours)
		endTime = endTime.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		print(f"collecting client data for {startTime}")
		url = "{}/xapi/v1/monitor/clients?startTime={}&endTime={}".format(baseurl, startTime, endTime)

		pageCount = 0
		success = 0 
		count = 0
		while success == 0:
			if count > 5:
				success =2
				print(f"API call has failed more than 5 times: {url}")
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
		
		totalCount = data['pagination']['totalCount']
		countInPage = data['pagination']['countInPage']
	
		clientCount(data)
		
		if countInPage < totalCount:
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

		ssid_dic[startTime]={}
		for ssid in ssidlist:
			ssid_dic[startTime][ssid]= len(ssidlist[ssid])
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

		with open('{}/data.json'.format(PATH), 'w') as f:
			json.dump(ssid_dic, f)
		
		print(f"completed capture at {API_start_time}")
		API_start_time = API_start_time + datetime.timedelta (hours=iteration_hours)
		secondtry = []
	if faillist:
		print("\nThese API calls failed 2 times and data was not collected:")
		for failurl in faillist:
			print(failurl)
		
if __name__ == '__main__':
	main()