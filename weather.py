import urllib2
from xml.dom import minidom
import datetime

#
#  Map the MetOffice weather codes to Icons. 
# ( See http://www.metoffice.gov.uk/datapoint/product/uk-3hourly-site-specific-forecast )
#

# SVG contains all these icons mapped to these ids
mapping = [ 
  'skc',       #  Clear night                     skc.svg
  'skc',       #  Sunny day                       skc.svg
  'sct',       #  Partly cloudy (night)           sct.svg
  'sct',       #  Partly cloudy (day)             sct.svg
  '',          #  Not used                        -
  'fg',        #  Mist                            fg.svg
  'fg',        #  Fog                             fg.svg
  'bkn',       #  Cloudy                          bkn.svg
  'ovc',       #  Overcast                        ovc.svg
  'hi_shwrs',  #  Light rain shower (night)       hi_shwrs.svg
  'hi_shwrs',  #  Light rain shower (day)         hi_shwrs.svg
  'hi_shwrs',  #  Drizzle                         hi_shwrs.svg
  'ra1',       #  Light rain                      ra1.svg
  'ra',        #  Heavy rain shower (night)       ra.svg
  'ra',        #  Heavy rain shower (day)         ra.svg
  'ra',        #  Heavy rain                      ra.svg
  'rasn',      #  Sleet shower (night)            rasn.svg
  'rasn',      #  Sleet shower (day)              rasn.svg
  'rasn',      #  Sleet                           rasn.svg
  'ip',        #  Hail shower (night)             ip.svg
  'ip',        #  Hail shower (day)               ip.svg
  'ip',        #  Hail                            ip.svg
  'sn',        #  Light snow shower (night)       sn.svg
  'sn',        #  Light snow shower (day)         sn.svg
  'sn',        #  Light snow                      sn.svg
  'sn',        #  Heavy snow shower (night)       sn.xvg
  'sn',        #  Heavy snow shower (day)         sn.svg
  'sn',        #  Heavy snow                      sn.svg
  'tsra',      #  Thunder shower (night)          tsra.svg
  'tsra',      #  Thunder shower (day)            tsra.svg
  'tsra',      #  Thunder                         tsra.svg
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
beaufort_scale = [0, 1, 4, 8, 13, 18, 25, 31, 39, 47, 55, 64, 74]


def getWeatherInfo(apiKey, location):
  weather = {'highs': [], 'feels': [],
             'icons': [], 'wind_icon': [],
             'speed_bft': []}
  #
  # Download and parse weather data based on location specified above
  #
  url = 'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/xml/' + location + '?res=daily&key=' + apiKey
  weather_xml = urllib2.urlopen(url).read()
  dom = minidom.parseString(weather_xml)



  # get date
  periods = dom.getElementsByTagName('Period')
  today_str = periods[0].getAttribute('value')
  weather['today_dt'] = datetime.datetime.strptime(today_str, '%Y-%m-%dZ')
  print "DAY:", weather['today_dt']


  weather['dtnow'] = datetime.datetime.now().strftime("%d-%b %H:%M")
  weather['dt'] = datetime.datetime.now().strftime("%d-%b")

  print "NOW:", weather['dtnow']

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

  for period in periods:
    data = period.getElementsByTagName('Rep')
       # temps
    weather['highs'] += [data[0].getAttribute('Dm')]  # 0 = Day 1= Night
    weather['feels'] += [data[0].getAttribute('FDm')]
       # weather 
    conditions = int(data[0].getAttribute('W'))
    weather['icons'] += [mapping[conditions]]
    
    # wind speed. Ignoring Gust for now
    direction = data[0].getAttribute('D') 
    speed_mph = int(data[0].getAttribute('S'))
    weather['wind_icon'] += ["wind" + wind_mapping[direction]]

    for bft, min_mph in enumerate(beaufort_scale):
       if speed_mph <= min_mph:
          break;

    # pad the string so they centre on the icon when printed
    # bug (?) with imagemagick convert 6.3.7 
    #  - works fine with 6.6.0 - the padding on the smaller 3 icons is messed up
    weather['speed_bft'] += str(bft)
    if bft < 10 :
       weather['speed_bft'] = weather['speed_bft'][-1] + " "
  
  return weather
