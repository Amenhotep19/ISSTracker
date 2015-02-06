#!/usr/bin/env python

# iss.py by Carl Monk (@ForToffee)
# https://github.com/ForToffee/ISSTracker
# no unicorns were harmed in the making of this code

import urllib2
import json
from time import sleep 
import unicornhat as UH
from pyorbital.orbital import Orbital
from datetime import datetime 
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from os import path

refresh = 15    #refresh time in secs

tle_url = "http://celestrak.com/NORAD/elements/stations.txt"
source_dir = path.dirname(path.realpath(__file__))
tle_filename = source_dir + "stations.txt"

feed_url = "https://api.wheretheiss.at/v1/satellites/25544"

location = [0.710173,51.548189]	#tickfield centre, Southend on Sea
origin = [-20,-5]
deg_per_pixel = 22.5 #180/8

lcd = Adafruit_CharLCDPlate()

#retrieve and load the JSON data into a JSON object
def getJSON():
	try:
		jsonFeed = urllib2.urlopen(feed_url)
		feedData = jsonFeed.read()
		#print feedData
		jsonFeed.close()
		data = json.loads(feedData)
		return data
	except urllib2.HTTPError, e:
		print 'HTTPError = ' + str(e.code)
	except urllib2.URLError, e:
		print 'URLError = ' + str(e.reason)
	except httplib.HTTPException, e:
		print 'HTTPException'
	except Exception:
		import traceback
		print 'generic exception: ' + traceback.format_exc()

	return []		


#retrieve latest TLE file from web  
def getTLEData():
	try:
		tle = urllib2.urlopen(tle_url)
		with open(tle_filename, "wb") as local_file:
			local_file.write(tle.read())
		
	except urllib2.HTTPError, e:
		print 'HTTPError = ' + str(e.code)
		pass 
	except urllib2.URLError, e:
		print 'URLError = ' + str(e.reason)
		pass 
	except Exception:
		import traceback
		print 'generic exception: ' + traceback.format_exc()
		pass 

#use this method to retrieve from web API
def parseISSDataFeed():
	data = getJSON()

	if len(data) == 0:
		return []
	
	lat = data['latitude']
	lng = data['longitude']
	alt = data['altitude']
	
	return [lng, lat, alt]

#
def parseISSTLEFile():
	orb = Orbital("iss (zarya)",tle_filename)
	utc_time = datetime.utcnow()
	return orb.get_lonlatalt(utc_time) + orb.get_observer_look(utc_time, location[0], location[1], 0)

	
	
#refresh the displayed pixels
def drawISS(lng,lat):
	lng = lng - origin[0]
	lat = lat - origin[1]


	x = abs(int((lng + 90) /22.5))
	if x > 7:
		x = 15 - x
	
	y = abs(int(((lat * -1) +90) /22.5))

	print 'x-value: %i, y-value: %i' % (x, y)
	UH.clear()
	if (lng < -90) or (lng > 90):	#'behind earth
		UH.set_pixel(x,y, 0, 0, 0xFF)
		UH.brightness(0.2)
	else:
		UH.set_pixel(x,y, 0xFF, 0xFF, 0)
		UH.brightness(0.4)
	
	UH.show()
	
def updateLCD(data):
	if data[4] > 60:
		backlight = lcd.GREEN 
	elif data[4] > 10:
		backlight = lcd.YELLOW
	else:
		backlight = lcd.ON
		
	lcd.clear()
	lcd.message('lng:%.2f\nlat:%.2f' % (data[0],data[1]))
	lcd.backlight(backlight)
	sleep(5)

	lcd.clear()
	lcd.message('alt:%.2f km' % (data[2]))
	sleep(5)

	lcd.clear()
	lcd.message('azimuth:%.2f\nelevation:%.2f' % ( data[3], data[4]))
	sleep(5)



#main program

UH.rotation(90)
UH.set_pixel(0,0, 0xFF,0,0)
UH.show()
sleep(5)
#download latest TLE file 
getTLEData()

while True:
	#data = parseISSDataFeed()
	data = parseISSTLEFile()
    
	if len(data) > 0:
		print 'long: %f, lat: %f, alt: %f, az:%f, elv:%f' % (data[0], data[1], data[2], data[3], data[4])
		drawISS(data[0], data[1])
		updateLCD(data)
	else:
		print 'no data'
		
	#sleep(refresh)

