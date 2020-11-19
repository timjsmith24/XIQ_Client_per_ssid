#!/usr/bin/env python3
import requests
import json
import math
import time
import os
import datetime

today = time.strftime("%Y-%m-%d %H:%M")
PATH = os.path.dirname(os.path.abspath(__file__))


totalstarttime = '2020-11-19T03:00:00.000Z'
iterationhours = 1
iterationdays = 1


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

def get_api_call(url,page=0):
	url = '{}&ownerId={}&page={}'.format(url, ownerId, page)

	## used for page testing
	#url = url+"&pageSize=10"
	#print(url)

	try:
		r = requests.get(url, headers=HEADERS, timeout=10)
	except:
		raise TypeError("API request failed")
	data = json.loads(r.text)
	if 'error' in data:
		if data['error']:
			failmsg = data['error']['message']
			raise TypeError("API Failed with reason: {}".format(failmsg))
	return data

def clientCount(data):
	global ssidlist
	for client in data['data']:
		if client['ssid'] not in ssidlist:
			ssidlist[client['ssid']]=[]
		ssidlist[client['ssid']].append(client['clientId'])


def main():
	if not os.path.exists('data.json'):
		ssid_dic = {}
	else:
		with open('{}/data.json'.format(PATH), 'r') as f:
			try:
				ssid_dic = json.load(f)
			except ValueError:
				ssid_dic = {}

	currenttime = datetime.datetime.strptime(totalstarttime, '%Y-%m-%dT%H:%M:%S.000Z')
	totalendtime = currenttime - datetime.timedelta (days=iterationdays)
	while currenttime > totalendtime:
		startTime = currenttime.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		endTime = currenttime + datetime.timedelta (hours=iterationhours)
		endTime = endTime.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		print(f"collecting client data for {startTime}")
		url = f"{baseurl}/xapi/v1/monitor/clients?startTime={startTime}&endTime={endTime}"
	
	
		pageCount = 0
		try:
			data = get_api_call(url)
		except TypeError as e:
			print("{} - on API {}".format(e, url))
			exit()
		except:
			print('unknown API error')
			exit()
		
		totalCount = data['pagination']['totalCount']
		countInPage = data['pagination']['countInPage']
		
		clientCount(data)
		
		if countInPage < totalCount:
			pageCount = math.ceil(int(totalCount)/int(countInPage))
			for page in range(int(pageCount)):
				page+=1
				try:
					data = get_api_call(url,str(page))
				except TypeError as e:
					print("{} - on API {}".format(e, url))
					exit()
				except:
					print('unknown API error')
					exit()
				clientCount(data)

		ssid_dic[startTime]={}
		for ssid in ssidlist:
			ssid_dic[startTime][ssid]= len(ssidlist[ssid])
		
		currenttime = currenttime - datetime.timedelta (hours=iterationhours)
	
	with open('{}/data.json'.format(PATH), 'w') as f:
		json.dump(ssid_dic, f)

if __name__ == '__main__':
	main()