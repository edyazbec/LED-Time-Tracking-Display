import requests
import json
import datetime

if __name__ == '__main__':
	#get the current day and figure out the most recent monday
	today = datetime.date.today()
	lastMonday = datetime.date.today() - datetime.timedelta(days=today.weekday())
	#parameters for the api call
	url='https://api.track.toggl.com/reports/api/v2/weekly'
	api_key=''#enter your api key from the website
	params={'user_agent':'python_api_test','workspace_id':'','since':lastMonday} #enter your workspace id
	#make the api call
	response=requests.get(url,auth=(api_key,'api_token'),params=params)
	response.json=json.loads(response.text)
	#save the json file
	if(response.ok):
		with open('togglData.json', 'w') as f:
			json.dump(response.json, f)
