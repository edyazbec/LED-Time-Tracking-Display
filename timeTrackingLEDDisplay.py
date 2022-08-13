#!/usr/bin/python
'''imports for toggl api calls'''
import requests
import json
import datetime
import time
'''imports for neoPixles'''
import time
import board
import neopixel
'''imports for graceful exits'''
from signal import signal, SIGINT
from sys import exit
'''other imports'''
import math


'''These are global variables for the toggl api'''
requestRate=60 #time between requests in seconds, min 1
apiKey='' #enter your api key
workspaceID='' #enter the id from your workspace


'''These are global variables for the neopixels'''
pixelPin = board.D18 #must connecct to D10, D12, D18, or D21
projectPixels = 93
lumPixels = 91
numPixels = projectPixels + lumPixels
pixels = neopixel.NeoPixel(pixelPin,numPixels,brightness=0.2,auto_write=False,pixel_order=neopixel.GRB)
leds=[(0,0,0)]*numPixels


def handler(signal_received, frame):
	#Handles greaceful exiting of the program
	pixels.fill((0,0,0))
	pixels.show()
	print('SIGINT or CTRL-C detected. Exiting gracefully')
	exit(0)


'''These functions are for the toggl api calling and processing'''
class project:
	def __init__(self, resp, total):
		self.name = resp['title']['project']
		self.color = resp['title']['hex_color']
		self.colorRGB=hexToFloats(self.color)
		self.hours = resp['totals'][7]/1000/60/60
		self.percent=round(self.hours/(total/1000/60/60)*100)
		self.numPixels=mapInt(self.percent,0,100,0,projectPixels)

def updateProjects():
	#get the current day and figure out the most recent monday
	today = datetime.date.today()
	monday = datetime.date.today() - datetime.timedelta(days = today.weekday())
	#parameters for the api call
	url='https://api.track.toggl.com/reports/api/v2/weekly'
	params={'user_agent':'python_api_test','workspace_id':workspaceID,'since':monday}
	#make the api call
	response=requests.get(url,auth=(apiKey,'api_token'),params=params)
	response.json=json.loads(response.text)
	#create / update the projects
	projects=[]
	if(response.ok):
		for i in range(len(response.json['data'])):
			projects.append(project(response.json['data'][i],response.json['week_totals'][-1]))
		#sort by time
		projects.sort(key=lambda x: x.hours,reverse=True)
	#return all the projects
	return projects

def updateProjectPixels(projects):
	if(projects==[]):
		print('something went very wrong')
		pixels.fill(255,0,0)
	else:
		j=0;
		for i in range(len(projects)):
			print(projects[i].name,"\t",projects[i].percent,"\t",projects[i].numPixels,"\t",projects[i].colorRGB)
			for k in range(j,j+projects[i].numPixels):
				if k < projectPixels:
					leds[k]=projects[i].colorRGB
			j=j+projects[i].numPixels

'''Utility Functions'''
def mapInt(x,inMin,inMax,outMin,outMax):
	#linear scale x in range inMin to inMax to y in range outMin to outMax
	return round((x-inMin)*(outMax-outMin)/(inMax-inMin)+outMin)

def hexToFloats(h):
    #Takes a hex rgb string (e.g. #ffffff) and returns an RGB tuple (float, float, float)
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) # skip '#'


'''Main Function'''
def main():
	startTime=time.time()
	#get the current project data
	projects=updateProjects()
	#update colors
	updateProjectPixels(projects)
	while(True):
		#every minute update catagory values
		if (time.time()-startTime>=requestRate):
			projects=updateProjects()
			updateProjectPixels(projects)
			startTime=time.time()
		else:
			for i in range(numPixels):
				if i < projectPixels:
					pixels[i]=leds[i]
					#scale=(math.sin(time.time()*(-2))+1)/2
					#pixels[i]=(round(leds[i][0]*scale),round(leds[i][1]*scale),round(leds[i][2]*scale))
				else:
					scale=((math.sin(time.time()*2)+1)/2)
					pixels[i]=(round(212*scale),round(175*scale),round(55*scale))
			pixels.show()
			#print('waiting')

if __name__ == '__main__':
	signal(SIGINT,handler)
	main()
