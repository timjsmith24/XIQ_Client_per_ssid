#!/usr/bin/env python3
import requests
import json
import math
import time
import os

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

def get_api_call(url,page=0):
	url = '{}{}?ownerId={}&page={}'.format(baseurl, url, ownerId, page)

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

url = "/xapi/v1/monitor/clients"
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


with open('{}/data.json'.format(PATH), 'w') as f:
	json.dump(ssid_dic, f)