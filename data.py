#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json

calendar_api = "https://mobile.eurowings.com/booking/scripts/FlightPlan/FlightPlanAjax.aspx?action=getflightplan"


def fetch_calendar(origin, destination, fromDate, toDate):
    """*origin TLC of origin airport"""
    calendar_url = (
            "%s&arrivalstation=%s&departurestation=%s&fromdate=%s&todate=%s&culture=en-GB"
            % (calendar_api, destination, origin, fromDate, toDate)
    )
    response = urllib.request.urlopen(calendar_url)

    return json.loads(response.read())


def fetch_weeks(departure, arrival):
    url = f'https://mobile.eurowings.com/booking/scripts/FlightPlan/FlightPlanAjax.aspx?' \
          f'action=getweekinfo&culture=en-GB&departurestation={departure}&arrivalstation={arrival}'

    response = urllib.request.urlopen(url)

    return json.loads(response.read())


def get_flights_by_day(origin, destination, from_date, to_date):
    flights_by_day = []
    cal = fetch_calendar(origin, destination, from_date, to_date)
    week_dates = cal[0]['dates']
    flight_infos = list(filter(lambda info: 'flightInfo' in info, cal))
    for weekDate in week_dates:
        flight_day = \
            {'weekDay': weekDate, 'date': week_dates[weekDate], 'flights': []
             }

        for flightInfo in flight_infos:
            if flightInfo[weekDate]:
                flight_day['flights'].append(flightInfo['flightInfo'])
        flights_by_day.append(flight_day)
    return flights_by_day


if __name__ == "__main__":
    # print(get_flights_by_day("CGN", "BER", "2020-11-16", "2020-11-22"))
    print(fetch_weeks("HAM", "STR"))
