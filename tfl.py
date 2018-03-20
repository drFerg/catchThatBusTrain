# TfL API
# 
import requests
import datetime

#northern/Arrivals/940GZZLUHCL
stationURL = "https://api.tfl.gov.uk/Line/{}?direction=inbound&app_id={}&app_key={}"
busStopURL = "https://api.tfl.gov.uk/StopPoint/{}/Arrivals?app_id={}&app_key={}"

def getBuses(stopPoint, apiId, apiKey):

    # Grab data using the TfL API for a particular stop point (bus)
    #
    busJson = requests.get(busStopURL.format(stopPoint, apiId, apiKey)).json()

    # Parse json based data, grabbing ID and arrival times
    buses = []
    for bus in busJson:
        print bus['vehicleId'], bus['expectedArrival'], bus['timeToStation']
        t = datetime.datetime.strptime(bus['expectedArrival'][:-2], "%Y-%m-%dT%H:%M:%S")
        buses += [(bus['lineName'], t.strftime("%H:%M:%S"), int(bus['timeToStation'])/60)]
        print buses[-1]
    
    return buses

def getTrains(stationPlatform, apiId, apiKey):
    # Grab tube related data for the Northern line platform at Hendon Central
    tubeJson = requests.get(stationURL.format(stationPlatform, apiId, apiKey)).json()
    trains = []

    # Parse the json data, recognising different branches of trains
    for tube in tubeJson:
        print 
        t = datetime.datetime.strptime(tube['expectedArrival'][:-2], "%Y-%m-%dT%H:%M:%S")
        train = (tube['towards'], t.strftime("%H:%M:%S"), int(tube['timeToStation'])/60)
        trains += [train]

    return trains
