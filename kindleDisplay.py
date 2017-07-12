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

import urllib2
from xml.dom import minidom
import datetime
import codecs
import requests
import secrets

#
# MetOffice API Key - Store in secrets file (don't add to git)
#
myApiKey=secrets.metOfficeAPIKey

# MetOffice Location ID
location="324151" #BARNET
#location="352409" #LONDON

#
#  temps_display=true:  kindle displays 'High' temp + 'Feels Like' temp 
#               false:  kindle displays 'Feels Like' + Wind
#
temps_display=1


#
#  SVG template
#
template = 'weather-script-preprocess_temps.svg'

#
#  Map the MetOffice weather codes to Icons. 
# ( See http://www.metoffice.gov.uk/datapoint/product/uk-3hourly-site-specific-forecast )
#
mapping = [ 
[0 , 'skc     '],  #  Clear night                     skc.svg
[1 , 'skc     '],  #  Sunny day                       skc.svg
[2 , 'sct     '],  #  Partly cloudy (night)           sct.svg
[3 , 'sct     '],  #  Partly cloudy (day)             sct.svg
[4 , '        '],  #  Not used                        -
[5 , 'fg      '],  #  Mist                            fg.svg
[6 , 'fg      '],  #  Fog                             fg.svg
[7 , 'bkn     '],  #  Cloudy                          bkn.svg
[8 , 'ovc     '],  #  Overcast                        ovc.svg
[9 , 'hi_shwrs'],  #  Light rain shower (night)       hi_shwrs.svg
[10, 'hi_shwrs'],  #  Light rain shower (day)         hi_shwrs.svg
[11, 'hi_shwrs'],  #  Drizzle                         hi_shwrs.svg
[12, 'ra1     '],  #  Light rain                      ra1.svg
[13, 'ra      '],  #  Heavy rain shower (night)       ra.svg
[14, 'ra      '],  #  Heavy rain shower (day)         ra.svg
[15, 'ra      '],  #  Heavy rain                      ra.svg
[16, 'rasn    '],  #  Sleet shower (night)            rasn.svg
[17, 'rasn    '],  #  Sleet shower (day)              rasn.svg
[18, 'rasn    '],  #  Sleet                           rasn.svg
[19, 'ip      '],  #  Hail shower (night)             ip.svg
[20, 'ip      '],  #  Hail shower (day)               ip.svg
[21, 'ip      '],  #  Hail                            ip.svg
[22, 'sn      '],  #  Light snow shower (night)       sn.svg
[23, 'sn      '],  #  Light snow shower (day)         sn.svg
[24, 'sn      '],  #  Light snow                      sn.svg
[25, 'sn      '],  #  Heavy snow shower (night)       sn.xvg
[26, 'sn      '],  #  Heavy snow shower (day)         sn.svg
[27, 'sn      '],  #  Heavy snow                      sn.svg
[28, 'tsra    '],  #  Thunder shower (night)          tsra.svg
[29, 'tsra    '],  #  Thunder shower (day)            tsra.svg
[30, 'tsra    '],  #  Thunder                         tsra.svg
]

#
# Wind - I'm mapping to one of 8 direction icons. Will do the 
# full 16 at some point...
#
wind_mapping = {
'N'  : '8',
'NNE': '8',
'NE' : '14',
'ENE': '14',
'E'  : '12',
'ESE': '12',
'SE' : '10',
'SSE': '10',
'S'  : '0',
'SSW': '0',
'SW' : '6',
'WSW': '6',
'W'  : '4',
'WNW': '4',
'NW' : '2',
'NNW': '2',
}

# 
# minimum mph value for each number on the bft scale 0-12
#
beaufort_scale = [ 0, 1, 4, 8, 13, 18, 25, 31, 39, 47, 55, 64, 74 ]



#
# Download and parse weather data based on location specified above
#
url='http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/xml/' + location + '?res=daily&key=' + myApiKey
weather_xml = urllib2.urlopen(url).read()
dom = minidom.parseString(weather_xml)



# get date
periods=dom.getElementsByTagName('Period')
today_str = periods[0].getAttribute('value')
today_dt= datetime.datetime.strptime(today_str, '%Y-%m-%dZ')
print "DAY:",today_dt


dtnow=datetime.datetime.now().strftime("%d-%b %H:%M")
dt = datetime.datetime.now().strftime("%d-%b")

print "NOW:",dtnow


# # #  This is the xml format from the met Office
# # #  - One <period> for each day of the forecast. Within it theres a line for Day and one for Night
# # #
#<DV dataDate="2014-04-03T11:00:00Z" type="Forecast">
#  <Location i="352448" lat="51.6555" lon="0.0698" name="LOUGHTON" country="ENGLAND" continent="EUROPE" elevation="52.0">
#    <Period type="Day" value="2014-04-03Z">
#      <Rep D="ESE" Gn="18" Hn="71" PPd="8" S="11" V="MO" Dm="17" FDm="15" W="7" U="2">Day</Rep>
#      <Rep D="SSW" Gm="16" Hm="89" PPn="11" S="7" V="MO" Nm="10" FNm="9" W="8">Night</Rep>
#    </Period>
#    <Period type="Day" value="2014-04-04Z">
#      <Rep D="WSW" Gn="18" Hn="58" PPd="5" S="9" V="GO" Dm="15" FDm="13" W="7" U="3">Day</Rep>
#      <Rep D="SW" Gm="11" Hm="87" PPn="5" S="7" V="GO" Nm="6" FNm="6" W="2">Night</Rep>
#    </Period>



# get temps:  Dm is Day Max, FDm is Feels Like Day Max
# get weather: W is weather type
# get wind:    D is wind dir, S is Speed, Gn is Gust at Noon


highs = [None]*7
feels = [None]*7
icons     =  [None]*7
wind_icon =  [None]*7 
speed_bft =  [""]*7 

i=0
for period in periods:
    thisDay=period.getAttribute('value')
    print "period:",i
    Reps = period.getElementsByTagName('Rep')
       # temps
    highs[i] = Reps[0].getAttribute('Dm')  # 0 = Day 1= Night
    feels[i] = Reps[0].getAttribute('FDm')
    print "   DayMax:",highs[i]
    print "   Feels :",feels[i]
       # weather 
    weather= int(Reps[0].getAttribute('W'))
    icons[i] = mapping[weather][1];
    icons[i] = icons[i].rstrip(' ')
    print "      Weather :",weather,icons[i]+'.svg'
       # wind speed. Ignoring Gust for now
    dir       =     Reps[0].getAttribute('D') 
    speed_mph = int(Reps[0].getAttribute('S'))
    wind_icon[i] = "wind"+wind_mapping[dir]

    for bft, min_mph in enumerate(beaufort_scale):
       if speed_mph <= min_mph:
          break;

    # pad the string so they centre on the icon when printed
    # bug (?) with imagemagick convert 6.3.7 
    #  - works fine with 6.6.0 - the padding on the smaller 3 icons is messed up
    speed_bft[i] = str(bft)
    if i== 0 and bft < 10 :
       speed_bft[i] = speed_bft[i]+" "
    print "      Wind    :",dir , speed_mph ,"mph", wind_icon[i], "Force ",speed_bft[i]+"<<<"
     
     # and loop
    i=i+1


#
# Preprocess SVG
#

# Open SVG to process
output = codecs.open(template , 'r', encoding='utf-8').read()

# Insert weather icons and temperatures
output = output.replace('ICON_ONE',icons[0])
output = output.replace('ICON_TWO',icons[1])
output = output.replace('ICON_THREE',icons[2])
#output = output.replace('ICON_FOUR',icons[3])

if temps_display:
   output = output.replace('H1',str(highs[0]))
   output = output.replace('H2',str(highs[1]))
   output = output.replace('H3',str(highs[2]))
   output = output.replace('H4',str(highs[3]))
else:
   output = output.replace('WIND_ONE'  ,wind_icon[0])
   output = output.replace('WIND_TWO'  ,wind_icon[1])
   output = output.replace('WIND_THREE',wind_icon[2])
   output = output.replace('WIND_FOUR' ,wind_icon[3])
   output = output.replace('BFT_ONE'  ,speed_bft[0])
   output = output.replace('BFT_TWO'  ,speed_bft[1])
   output = output.replace('BFT_THREE',speed_bft[2])
   output = output.replace('BFT_FOUR' ,speed_bft[3])


output = output.replace('L1',str(feels[0]))
output = output.replace('L2',str(feels[1]))
output = output.replace('L3',str(feels[2]))
output = output.replace('L4',str(feels[3]))

# Insert current time
output = output.replace('DATE_VALPLACE',str(dtnow))

output = output.replace('DATE', str(dt))

# Insert days of week
one_day = datetime.timedelta(days=1)
print " ONE DAY:",one_day

days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
print days_of_week[(today_dt + 2*one_day).weekday()]
print days_of_week[(today_dt + 3*one_day).weekday()]

output = output.replace('DAY_THREE',days_of_week[(today_dt + 2*one_day).weekday()])
output = output.replace('DAY_FOUR',days_of_week[(today_dt + 3*one_day).weekday()])



# TfL API
# 
# Grab data using the TfL API for a particular stop point (bus)
#
data = requests.get("https://api.tfl.gov.uk/StopPoint/490008060C/Arrivals?app_id=7dcae5c1&app_key={}".format(secrets.tflAPIKey))

# Parse json based data, grabbing ID and arrival times
json = data.json()
buses = []
for bus in json:
    print bus['vehicleId'], bus['expectedArrival'], bus['timeToStation']
    t = datetime.datetime.strptime(bus['expectedArrival'][:-2], "%Y-%m-%dT%H:%M:%S")
    print t.strftime("%H:%M:%S"), int(bus['timeToStation'])/60
    buses += [(bus['lineName'], t.strftime("%H:%M:%S"), int(bus['timeToStation'])/60)]

# Sort buses by arrival time and add times to SVG output
arrivals = sorted(buses, key=lambda bus:bus[2])
count = 0
for bus in arrivals:
    info = str(bus[0]) + ' - ' + str(bus[2]) + 'min ' + bus[1]
    output = output.replace('BUS' + str(count), info)
    count += 1
    if count == 3:
        break

# Grab tube related data for the Northern line platform at Hendon Central
tubeJson = requests.get("https://api.tfl.gov.uk/Line/northern/Arrivals/940GZZLUHCL?direction=inbound&app_id=7dcae5c1&app_key={}".format(secrets.tflAPIKey)).json()
MAX_TRAINS = 4 #4 trains
MAX_BUSES = 2 #2 buses
trains = []

# Parse the json data, recognising different branches of trains
for tube in tubeJson:
    t = datetime.datetime.strptime(tube['expectedArrival'][:-2], "%Y-%m-%dT%H:%M:%S")
    if "Bank" in tube['towards']:
        train = ("Bank", t, t.strftime("%H:%M:%S"))
    else:
        train = ("CX  ", t, t.strftime("%H:%M:%S"))
    trains += [train]



# Sort trains by arrival time and add to SVG output

arrivals = sorted(trains, key=lambda train:train[1])
print arrivals
count = 0

for train in arrivals:
    info = train[0] + ' - ' + train[2]
    output = output.replace('TRAIN' + str(count), info)
    count += 1
    if count == MAX_TRAINS:
        break

if count < MAX_TRAINS:
    for i in range(count, MAX_TRAINS):
        output = output.replace('TRAIN' + str(i), "")

# Write SVG output
codecs.open('kindleOutput.svg', 'w', encoding='utf-8').write(output)

# EOF
