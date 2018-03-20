#!/usr/bin/python

# Kindle Weather, Tube and Bus Ambient Display
# Fergus Leahy (http://fergusleahy.co.uk)
# July 2017
#
# Inspired by a weather based display by Matthew Petroff (http://www.mpetroff.net/)
# September 2012
#
# Owen Bullock - UK Weather - MetOffice - Aug 2013
# Apr 2014 - amended for Wind option
#


import datetime
import codecs
import secrets
import weather
import tfl
#
# MetOffice API Key - Store in secrets file (don't add to git)
#
myApiKey = secrets.metOfficeAPIKey

# MetOffice Location ID
location = "324151" #BARNET
#location="352409"  #LONDON

#
#  SVG template
#
# Open SVG to add weather, tube and bus times
template = 'catchThatBusTrain_src.svg'
output = codecs.open(template , 'r', encoding='utf-8').read()


# Get weather and insert into SVG
myWeather = weather.getWeatherInfo(secrets.metOfficeAPIKey, location)
# Insert weather icon and temperatures
output = output.replace('ICON_ONE', myWeather['icons'][0])
output = output.replace('H1', str(myWeather['highs'][0]))
output = output.replace('L1', str(myWeather['feels'][0]))
# Insert current time
output = output.replace('DATE_VALPLACE', str(myWeather['dtnow']))
output = output.replace('DATE', str(myWeather['dt']))


#TFL
stopPoint = '490008060C'
stationLine = 'northern/Arrivals/940GZZLUHCL'
MAX_BUSES = 3 #2 buses
MAX_TRAINS = 4 #4 trains

buses = tfl.getBuses(stopPoint, secrets.tflAPIID, secrets.tflAPIKey)
# Sort buses by arrival time and add times to SVG output
arrivals = sorted(buses, key=lambda bus:bus[2])
count = 0
for bus in arrivals:
    busNum = str(bus[0]) + ' in ' + str(bus[2]) + ('min' if bus[2] == 1 else 'mins')
    busTime = bus[1]
    output = output.replace('BUS' + str(count), busNum)
    output = output.replace('BUSTIME' + str(count), busTime)
    count += 1
    if count == MAX_BUSES:
        break


trains = tfl.getTrains(stationLine, secrets.tflAPIID, secrets.tflAPIKey)

# Sort trains by arrival time and add to SVG output
arrivals = sorted(trains, key=lambda train:train[1])
print arrivals

count = 0
for train in arrivals:
    branch = 'Bank' if 'Bank' in train[0] else 'CX'
    info = branch + ' in ' + str(train[2]) + ('min' if train[2] == 1 else 'mins')
    trainTime = train[1]
    output = output.replace('TRAIN' + str(count), info)
    output = output.replace('TRAINTIME' + str(count), trainTime)

    count += 1
    if count == MAX_TRAINS:
        break

if count < MAX_TRAINS:
    for i in range(count, MAX_TRAINS + 1):
        output = output.replace('TRAIN' + str(i), "")
        output = output.replace('TRAINTIME' + str(i), "")

# Write SVG output
codecs.open('kindleOutput.svg', 'w', encoding='utf-8').write(output)
