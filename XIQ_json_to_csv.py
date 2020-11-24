#!/usr/bin/env python3
import json
import os
import pandas
import argparse
import re


PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser() 
parser.add_argument('jsonfile')
args = parser.parse_args()
filename = "{0}".format(args.jsonfile)



def clientperssid(data):
	msg='TIME/,/ SSID/,/ CLIENT COUNT\n'
	for timestamp in data:
		for ssid in data[timestamp]:
			msg += (f"{timestamp}/,/ {ssid}/,/ {data[timestamp][ssid]}\n")
	return(msg)

def main():
	if not os.path.exists(filename):
		print(f"failed to open file {filename}")
		exit()
	else:
		with open('{}/{}'.format(PATH, filename), 'r') as f:
			try:
				data = json.load(f)
			except ValueError:
				data = {}

	
	cpssid_msg = clientperssid(data)
	cpssid_data = pandas.DataFrame([sub.split("/,/") for sub in cpssid_msg.splitlines()])
	
	excelfilename = filename.replace('json', 'xlsx')
	# Create a Pandas Excel writer using XlsxWriter as the engine
	writer = pandas.ExcelWriter('{}/{}'.format(PATH, excelfilename), engine='xlsxwriter')
	
	# Create Sheets
	sheets = ['Clients per SSID']
	# Write each dataframe to a different worksheet
	try:
		cpssid_data.to_excel(writer, sheet_name=sheets[0], index=False, header=False)
	except NameError:
		print("There was no SSID info")
	except:
		print("Clients per SSID incountered an Unknown error")
	
	# Close the Pandas Excel writer and output the Excel file
	writer.save()
	print(f"Successfully wrote data to {excelfilename}")

if __name__ == '__main__':
	main()