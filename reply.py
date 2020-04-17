def createReply(flight):
    reply = flight['weekDay'] + flight['date'] + '\n'
    for f in flight['flights']:
        departure = "🛫" + f['departureTime']
        arrival = "🛬" + f['arrivalTime']
        reply += departure + " : " + arrival + '\n'
    return reply

def main():
    flight = {'departureTime': '7:10 AM', 'arrivalTime': '8:20 AM', 'flightNr': 'EW24', 'via': '', 'viaTLC': '', 'viaFlightNr': '', 'Monday': True, 'Tuesday': False, 'Wednesday': False, 'Thursday': False, 'Friday': False, 'Saturday': False, 'Sunday': False}
    msg = createReply(flight)
    print(msg)

if __name__ == "__main__":
    main()