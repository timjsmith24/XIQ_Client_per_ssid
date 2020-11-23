#!/usr/bin/env python3
import json
import os
import pandas


PATH = os.path.dirname(os.path.abspath(__file__))

filename = 'data.json'

def clientperssid(data):
	msg='TIME/,/ SSID/,/ CLIENT COUNT\n'
	for timestamp in data:
		for ssid in data[timestamp]:
			msg += (f"{timestamp}/,/ {ssid}/,/ {data[timestamp][ssid]}\n")
	return(msg)

def main():
	if not os.path.exists(filename):
		print("failed to open file")
		exit()
	else:
		with open('{}/data.json'.format(PATH), 'r') as f:
			try:
				data = json.load(f)
			except ValueError:
				data = {}

	
	cpssid_msg = clientperssid(data)
	cpssid_data = pandas.DataFrame([sub.split("/,/") for sub in cpssid_msg.splitlines()])
	

	# Create a Pandas Excel writer using XlsxWriter as the engine
	writer = pandas.ExcelWriter('{}/XIQ_report.xlsx'.format(PATH), engine='xlsxwriter')
	
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


if __name__ == '__main__':
	main()