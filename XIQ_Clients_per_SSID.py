#!/usr/bin/env python3
import requests
import json
import math
import time
import os
from requests.exceptions import HTTPError

today = time.strftime("%Y-%m-%d %H:%M")
PATH = os.path.dirname(os.path.abspath(__file__))

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
pagesize = '5'


def get_api_call(url,page=0,pageCount=0):
	url = '{}?ownerId={}&page={}'.format(url, ownerId, page)

	## used for page testing
	if pagesize:
		url = url+(f"&pageSize={pagesize}")
	if pageCount != 0:
		print(f"API call on {page} of {pageCount}")

	try:
		r = requests.get(url, headers=HEADERS, timeout=3)
	except HTTPError as http_err:
		secondtry.append(url)
		raise HTTPError(f'HTTP error occurred: {http_err} - on API {url}')  # Python 3.6
	except Exception as err:
		raise TypeError(f'Other error occurred: {err}: on API {url}')
	else:
		data = json.loads(r.text)
		if 'error' in data:
			if data['error']:
				failmsg = data['error']['message']
				raise TypeError(f"API Failed with reason: {failmsg} - on API {url}")
		return data

def clientCount(data):
	global ssidlist
	for client in data['data']:
		if client['ssid'] not in ssidlist:
			ssidlist[client['ssid']]=[]
		ssidlist[client['ssid']].append(client['clientId'])

#add second try
def main():
	url = (f"{baseurl}/xapi/v1/monitor/clients")
	pageCount = 0
	success = 0
	count = 0
	while success == 0:
		if count > 5:
			success = 2
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
			print(f"{url} - successful connection")
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
	if not os.path.exists('data.json'):
		ssid_dic = {}
	else:
		with open('{}/data.json'.format(PATH), 'r') as f:
			try:
				ssid_dic = json.load(f)
			except ValueError:
				ssid_dic = {}

	ssid_dic[today]={}
	for ssid in ssidlist:
		ssid_dic[today][ssid]= len(ssidlist[ssid])
	if secondtry:
		print(secondtry)
	print(ssid_dic)
	#with open('{}/data.json'.format(PATH), 'w') as f:
	#	json.dump(ssid_dic, f)
	
if __name__ == '__main__':
	main()
