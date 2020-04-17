import urllib.request
import json

calendar_api = "https://mobile.eurowings.com/booking/scripts/FlightPlan/FlightPlanAjax.aspx?action=getflightplan"

def fetchCalendar(origin, destination, fromDate, toDate):
    '''*origin TLC of origin airport'''
    calendar_url = (
        "%s&arrivalstation=%s&departurestation=%s&fromdate=%s&todate=%s&culture=en-GB" 
        % (calendar_api, destination, origin, fromDate, toDate)
    )
    response = urllib.request.urlopen(calendar_url)

    return json.loads(response.read())

def getFlightInfo():
    cal = fetchCalendar("CGN", "BER", "2020-11-16", "2020-11-22")
    #TODO map date to weekday
    #weekDate = cal[0]['dates']
    y = filter(lambda info: 'flightInfo' in info, cal)
    x = map(addFlyingDays, y)

    return list(x)

def test_1():
    flights = getFlightInfo()
    for flight in flights:
        print(flight['departureTime'])

def addFlyingDays(item):
    flightInfo = item['flightInfo']
    flightInfo['Monday'] = item['Monday']
    flightInfo['Tuesday'] = item['Tuesday']
    flightInfo['Wednesday'] = item['Wednesday']
    flightInfo['Thursday'] = item['Thursday']
    flightInfo['Friday'] = item['Friday']
    flightInfo['Saturday'] = item['Saturday']
    flightInfo['Sunday'] = item['Sunday']
    return flightInfo

def test_2():
    cal = fetchCalendar("CGN", "BER", "2020-11-16", "2020-11-22")
    weekDates = cal[0]['dates']
    flightInfos = list(filter(lambda info: 'flightInfo' in info, cal))
    for weekDate in weekDates:
        print(weekDate + " : " + weekDates[weekDate])
        for flightInfo in flightInfos:
            if(flightInfo[weekDate]):
                flight = flightInfo['flightInfo'] 
                departure = "🛫" + flight['departureTime']
                arrival = "🛬" + flight['arrivalTime']

                print(departure + " : " + arrival)
        print("====================")
    return ""

def getFlightsByDay():
    flightsByDay = []
    cal = fetchCalendar("CGN", "BER", "2020-11-16", "2020-11-22")
    weekDates = cal[0]['dates']
    flightInfos = list(filter(lambda info: 'flightInfo' in info, cal))
    for weekDate in weekDates:
        flightDay = {}
        flightDay['weekDay'] = weekDate
        flightDay['date'] = weekDates[weekDate]
        flightDay['flights'] = []
        
        for flightInfo in flightInfos:
            if(flightInfo[weekDate]):
                flightDay['flights'].append(flightInfo['flightInfo'])
        flightsByDay.append(flightDay)
    return flightsByDay

if __name__ == "__main__":
    print(getFlightsByDay())