#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def create_replay(departure, destination, flight):
    departure_tlc = departure.split(',')[1]
    destination_tlc = destination.split(',')[1]
    date = flight['date']
    reply = f"{flight['weekDay']} {date}\n"
    for f in flight['flights']:
        url = f'https://www.eurowings.com/de/buchen/fluege/sparkalender.html?origin={departure_tlc}&adults=1&toDate={date}&destination={destination_tlc}&dateDate={date}'
        departure_line = "🛫" + f['departureTime']
        arrival_line = "🛬" + f['arrivalTime']
        reply += f'[{departure_line} : {arrival_line}]({url})\n'

    return reply


def main():
    flight = {'departureTime': '7:10 AM', 'arrivalTime': '8:20 AM', 'flightNr': 'EW24', 'via': '', 'viaTLC': '',
              'viaFlightNr': '', 'Monday': True, 'Tuesday': False, 'Wednesday': False, 'Thursday': False,
              'Friday': False, 'Saturday': False, 'Sunday': False}
    msg = create_replay(flight)
    print(msg)


if __name__ == "__main__":
    main()
