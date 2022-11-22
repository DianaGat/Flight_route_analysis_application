# -*- coding: utf-8 -*-
#first file. Takes variables and gets data from API. Then preprocees it to csv format and svaes with a given name, name is chnages for diff routes??

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime as dt
import os


def GetAndProcessFlightData(input_dep_airport, input_arr_airport, 
                            iata_flight_number, csv_path, local_database_path,
                            flights_api_key,
                            air_labs_api_key,
                            weather_api_key):
    input_flight_number = iata_flight_number[2:] # Remove airline designator
    if(flights_api_key != ""):
        flights_of_interest_pd = GetFlightsFromAPI(input_dep_airport, 
                                                   input_arr_airport, 
                                                   input_flight_number, 
                                                   iata_flight_number, 
                                                   flights_api_key)
    else:
        flights_of_interest_pd = GetFlightsFromLocalDatabase(input_dep_airport, 
                                                             input_arr_airport, 
                                                             input_flight_number, 
                                                             iata_flight_number, 
                                                             local_database_path)
    if flights_of_interest_pd.empty: 
        return False        
    else:
        PreProcessData(flights_of_interest_pd, input_dep_airport, input_arr_airport
                   , csv_path, air_labs_api_key, weather_api_key)
        return True
    
def GetFlightsFromLocalDatabase(input_dep_airport, input_arr_airport, 
                            input_flight_number, iata_flight_number, 
                            local_database_path):
    
    json_filenames = [pos_json for pos_json in os.listdir(local_database_path) if pos_json.endswith('.json')]
    localdatabase = []
    for json_filename in json_filenames:
        with open(os.path.join(local_database_path, json_filename)) as json_data:
            localdatabase = localdatabase + json.load(json_data)
            
    landed_flights = [flight 
                  for flight in localdatabase 
                  if flight["status"] != "unknown"
                  and flight["status"] != "scheduled"
                  and flight["flight"]["iataNumber"] == iata_flight_number
                  and flight["status"] != "active"
                  and flight["departure"]["iataCode"] == input_dep_airport
                  and flight["arrival"]["iataCode"] == input_arr_airport
                  and flight["flight"]["iataNumber"] == iata_flight_number
                  and flight["flight"]["number"] == input_flight_number
                  ]
    flights_of_interest_pd = pd.DataFrame.from_dict(landed_flights)
    flights_of_interest_pd.reset_index(drop = True, inplace=True)

    return flights_of_interest_pd
    

def GetFlightsFromAPI(input_dep_airport, 
                      input_arr_airport, 
                      iata_flight_number, 
                      input_flight_number, 
                      flights_api_key):
    
    #input by default, max date from today = 1 year, min datde from today = 3 days, max days called = 30
    date_start = ["2022-01-01", "2022-01-11", "2022-01-22", 
                  "2022-02-01", "2022-02-11", "2022-02-22", 
                  "2022-03-01", "2022-03-11", "2022-03-22", 
                  "2022-04-01", "2022-04-11", "2022-04-22", 
                  "2022-05-01", "2022-05-11", "2022-05-22", 
                  "2022-06-01", "2022-06-11", "2022-06-22", 
                  "2022-07-01", "2022-07-11", "2022-07-22", 
                  "2022-08-01", "2022-08-11", "2022-08-22",  
                  "2022-09-01", "2022-09-11", "2022-09-22"]
    date_end = ["2022-01-10", "2022-01-21", "2022-01-31", 
                "2022-02-10", "2022-02-21", "2022-02-28", 
                "2022-03-10", "2022-03-21", "2022-03-31", 
                "2022-04-10", "2022-04-21", "2022-04-30", 
                "2022-05-10", "2022-05-21", "2022-05-31", 
                "2022-06-10", "2022-06-21", "2022-06-30", 
                "2022-07-10", "2022-07-21", "2022-07-31", 
                "2022-08-10", "2022-08-21", "2022-08-31",  
                "2022-09-10", "2022-09-21", "2022-09-30"]
    api_key = flights_api_key
    
    # call API for every 30/31 days and created a united pandas table
    count = 0
    flights_of_interest_pd = pd.DataFrame()
    api_response = list([])
    while count != len(date_start):
        api_result =requests.get(
            "https://aviation-edge.com/v2/public/flightsHistory?key="+api_key+
            "&code="+input_arr_airport+
            "&type=arrival&date_from="+
            date_start[count]+
            "&date_to="+date_end[count]+
            "&flight_number="+input_flight_number)
        api_response = api_result.json()
        landed_flights = [flight 
                      for flight in api_response 
                      if flight["status"] != "unknown"
                      and flight["status"] != "scheduled"
                      and flight["flight"]["iataNumber"] == iata_flight_number
                      and flight["status"] != "active"
                      ]
        flights_of_interest = landed_flights
        flights_of_interest_pd = pd.concat([flights_of_interest_pd, 
                                            pd.DataFrame.from_dict(
                                                flights_of_interest)])
        count = count + 1
    flights_of_interest_pd.reset_index(drop = True, inplace=True)
    return flights_of_interest_pd
    
    
def PreProcessData(flights_of_interest_pd, input_dep_airport, input_arr_airport
                   , csv_path, air_labs_api_key, weather_api_key):
        
    #from dict to pandas
    #departure
    dep_terminal=[]
    dep_gate =[]
    dep_delay=[]
    dep_actual=[]
    dep_iata=[]
    dep_time=[]
    line = 0
    while line != len(flights_of_interest_pd):
        dep_iata = np.append(dep_iata, 
                             flights_of_interest_pd["departure"][line]["iataCode"])
        dep_time = np.append(dep_time, 
                             flights_of_interest_pd["departure"][line]["scheduledTime"])
        if "terminal" in flights_of_interest_pd["departure"][line]:
            dep_terminal = np.append(dep_terminal, 
                                     flights_of_interest_pd["departure"][line]["terminal"])
        else:
            dep_terminal = np.append(dep_terminal, np.NaN)
        if "gate" in flights_of_interest_pd["departure"][line]:
            dep_gate = np.append(dep_gate, 
                                 flights_of_interest_pd["departure"][line]["gate"])
        else:
            dep_gate = np.append(dep_gate, np.NaN)
        if "delay" in flights_of_interest_pd["departure"][line]:
            dep_delay = np.append(dep_delay, 
                                  flights_of_interest_pd["departure"][line]["delay"])
        else:
            dep_delay = np.append(dep_delay, np.NaN)
        if "actualTime" in flights_of_interest_pd["departure"][line]:
            dep_actual = np.append(dep_actual, 
                                   flights_of_interest_pd["departure"][line]["actualTime"])
        else:
            dep_actual = np.append(dep_actual, 0) 
        line = line + 1
        
    flights_of_interest_pd["dep_iata"] = dep_iata
    flights_of_interest_pd["dep_time"]=dep_time
    flights_of_interest_pd["dep_delay"] =dep_delay
    flights_of_interest_pd["dep_actual"]=dep_actual
    flights_of_interest_pd["dep_terminal"]= dep_terminal
    flights_of_interest_pd["dep_gate"] = dep_gate
    
    flights_of_interest_pd = flights_of_interest_pd.drop(columns="departure")
        
    #arrival
    arr_terminal=[]
    arr_gate =[]
    arr_delay=[]
    arr_actual=[]
    arr_iata=[]
    arr_time=[]
    line = 0
    while line != len(flights_of_interest_pd):
        arr_iata = np.append(arr_iata, 
                             flights_of_interest_pd["arrival"][line]["iataCode"])
        arr_time = np.append(arr_time, 
                             flights_of_interest_pd["arrival"][line]["scheduledTime"])
        if "terminal" in flights_of_interest_pd["arrival"][line]:
            arr_terminal = np.append(arr_terminal, 
                                     flights_of_interest_pd["arrival"][line]["terminal"])
        else:
            arr_terminal = np.append(arr_terminal, np.NaN)
        if "gate" in flights_of_interest_pd["arrival"][line]:
            arr_gate = np.append(arr_gate, 
                                 flights_of_interest_pd["arrival"][line]["gate"])
        else:
            arr_gate = np.append(arr_gate, np.NaN)
        if "delay" in flights_of_interest_pd["arrival"][line]:
            arr_delay = np.append(arr_delay, 
                                  flights_of_interest_pd["arrival"][line]["delay"])
        else:
            arr_delay = np.append(arr_delay, 0)
        if "actualTime" in flights_of_interest_pd["arrival"][line]:
            arr_actual = np.append(arr_actual, 
                                   flights_of_interest_pd["arrival"][line]["actualTime"])
        else:
            arr_actual = np.append(arr_actual, 0) 
        line = line + 1
        
    flights_of_interest_pd["arr_iata"] = arr_iata
    flights_of_interest_pd["arr_time"]=arr_time
    flights_of_interest_pd["arr_delay"] =arr_delay
    flights_of_interest_pd["arr_actual"]=arr_actual
    flights_of_interest_pd["arr_terminal"]= arr_terminal
    flights_of_interest_pd["arr_gate"] = arr_gate
    
    flights_of_interest_pd = flights_of_interest_pd.drop(columns="arrival")
    
    #airline column
    airline_iata=[]
    line = 0
    while line != len(flights_of_interest_pd):
        if "iataCode" in flights_of_interest_pd["airline"][line]:
            airline_iata = np.append(airline_iata, 
                                     flights_of_interest_pd["airline"][line]["iataCode"])
        else:
            airline_iata = np.append(airline_iata, np.NaN)
        line = line + 1
        
    flights_of_interest_pd["airline_iata"] = airline_iata
    
    flights_of_interest_pd = flights_of_interest_pd.drop(columns="airline")
       
    #flight column
    flight_iata=[]
    line = 0
    while line != len(flights_of_interest_pd):
        if "iataNumber" in flights_of_interest_pd["flight"][line]:
            flight_iata = np.append(flight_iata, 
                                    flights_of_interest_pd["flight"][line]["iataNumber"])
        else:
            flight_iata = np.append(flight_iata, np.NaN)
        line = line + 1
        
    flights_of_interest_pd["flight_iata"] = flight_iata
    
    flights_of_interest_pd = flights_of_interest_pd.drop(columns="flight")
    
            
    flights_of_interest_pd = flights_of_interest_pd[[#'type',
     'status',
     'flight_iata',
     'dep_iata',
     'dep_time',
     'dep_delay',
     'dep_actual',
     'dep_terminal',
     'dep_gate',
     'arr_iata',
     'arr_time',
     'arr_delay',
     'arr_actual',
     'arr_terminal',
     'arr_gate',
     'airline_iata',
    # 'cs_airline_iata'
    ]]
     
    #call for aiport to get location. Lication in needed for wrather detection
    params_airport = {
      'api_key': air_labs_api_key,
      'params1': ""
    }
    method_airport = "airports?iata_code="
    api_base_airport = 'http://airlabs.co/api/v9/'
    api_result_airport = requests.get(
        api_base_airport+
        method_airport+
        input_dep_airport, 
        params_airport)
    api_response_airport = api_result_airport.json()
    
    ## dep airport
    #lat and lng
    dep_airport_lat = api_response_airport["response"][0]["lat"]
    dep_airport_lng = api_response_airport["response"][0]["lng"]
    
    params_airport = {
      'api_key': air_labs_api_key,
      'params1': ""
    }
    method_airport = "airports?iata_code="
    api_base_airport = 'http://airlabs.co/api/v9/'
    api_result_airport = requests.get(
        api_base_airport+
        method_airport+
        input_arr_airport, 
        params_airport)
    api_response_airport = api_result_airport.json()
    
    ## arr airport
    #lat and lng
    arr_airport_lat = api_response_airport["response"][0]["lat"]
    arr_airport_lng = api_response_airport["response"][0]["lng"]
    
    
    #add to pandas lat and lng 
    flights_of_interest_pd["arr_airport_lat"] = arr_airport_lat
    flights_of_interest_pd["arr_airport_lng"] = arr_airport_lng
    flights_of_interest_pd["dep_airport_lat"] = dep_airport_lat
    flights_of_interest_pd["dep_airport_lng"] = dep_airport_lng
    
    #format time from string to dttime     
    line = 0
    while line != len(flights_of_interest_pd):
        flights_of_interest_pd["dep_time"][line] = dt.strptime(flights_of_interest_pd["dep_time"][line], 
                                                               '%Y-%m-%dt%H:%M:00.000')
        line = line + 1
    
    line = 0
    while line != len(flights_of_interest_pd):
        if flights_of_interest_pd["dep_actual"][line] !="0":
            flights_of_interest_pd["dep_actual"][line] = dt.strptime(flights_of_interest_pd["dep_actual"][line], 
                                                                     '%Y-%m-%dt%H:%M:00.000')
        else:
            flights_of_interest_pd["dep_actual"][line] = np.NaN
        line = line + 1
    
    line = 0
    while line != len(flights_of_interest_pd):
        flights_of_interest_pd["arr_time"][line] = dt.strptime(flights_of_interest_pd["arr_time"][line], 
                                                               '%Y-%m-%dt%H:%M:00.000')
        line = line + 1
        
    line = 0
    while line != len(flights_of_interest_pd):
        if flights_of_interest_pd["arr_actual"][line] !="0":
            flights_of_interest_pd["arr_actual"][line] = dt.strptime(flights_of_interest_pd["arr_actual"][line], 
                                                                     '%Y-%m-%dt%H:%M:00.000')
        else:
            flights_of_interest_pd["arr_actual"][line] = np.NaN
        line = line + 1
     
    #chnage name
    delay_ML = flights_of_interest_pd[['status',
     'flight_iata',
     'dep_iata',
     'dep_time',
     'dep_delay',
     'dep_actual',
     'dep_terminal',
     'dep_gate',
     'arr_iata',
     'arr_time',
     'arr_delay',
     'arr_actual',
     'arr_terminal',
     'arr_gate',
     'airline_iata',
    # 'cs_airline_iata',
     'arr_airport_lat',
     'arr_airport_lng',
     'dep_airport_lat',
     'dep_airport_lng']]

    delay_ML = delay_ML.reset_index(drop= True)
    
    ### flind dates and time for weather
    ## arrival
    #find unique dates of arrival
    unique_dates = pd.to_datetime(delay_ML["arr_time"].unique())
    unique_dates = unique_dates.date
    unique_dates = pd.to_datetime(unique_dates).unique()
    unique_dates = unique_dates.date
    
    ### call weather for every day, hourly
    #weather
    ## arrival
    API = "key=" + weather_api_key + "&"
    method = "q="+str(arr_airport_lat)+","+str(arr_airport_lng)+"&"
    api_base = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?'
    line = 0
    weather_pd = pd.DataFrame([])
    weather_date = []
    while line != len(unique_dates):
        date = str(unique_dates[line])
        requestURL = api_base+API+method+"format=json&"+"date="+date+"&tp=1"
        print(requestURL)
        api_result_weather = requests.get(requestURL)
        api_response_weather = api_result_weather.json()
        weather_pd = weather_pd.append(pd.DataFrame.from_dict(
            api_response_weather["data"]["weather"][0]["hourly"]))
        weather_date = np.append(weather_date, [date] * 24)
        line = line + 1
    
    # attach date for every day. Since every day weather has 24 hour obf observations, I multiply date by 24
    weather_pd["arr_date"] = weather_date
    
    weather_pd = weather_pd[['time', #hmm
     'tempC',
    # 'tempF',
    # 'windspeedMiles',
     'windspeedKmph',
     'winddirDegree',
    # 'winddir16Point',
     'weatherCode',
    # 'weatherIconUrl',
     'weatherDesc',
     'precipMM',
    # 'precipInches',
     'humidity',
     'visibility',
    # 'visibilityMiles',
     'pressure', 
    # 'pressureInches',
     'cloudcover',
     'HeatIndexC',
    # 'HeatIndexF',
     'DewPointC',
    # 'DewPointF',
     'WindChillC',
    # 'WindChillF',
    # 'WindGustMiles',
     'WindGustKmph',
     'FeelsLikeC',
     "arr_date",
    # 'FeelsLikeF',
    # 'uvIndex'
    ]]
    weather_pd = weather_pd.reset_index(drop = True)
    
    
    #show just date instead of date and time as it is by deafult
    line = 0
    while line != len(weather_pd):
        weather_pd["arr_date"][line] = dt.strptime(weather_pd["arr_date"][line], 
                                                   '%Y-%m-%d').date()
        line = line + 1
    
    #reformat time in weather_pd pandas. In pandas time is a string in format "0000" that is "00:00"
    weather_line = 0
    while weather_line != len(weather_pd):
        line = 0
        while line != 24:
            if line <= 9:
                weather_pd["time"][weather_line] = weather_pd["time"][weather_line][0]+":00"
            elif line >9: 
                weather_pd["time"][weather_line] = weather_pd["time"][weather_line][0:2]+":00"
            line = line + 1
            weather_line = weather_line + 1
        
    # now, when it is in "00:00" format, I transform it to dttime from string
    line = 0
    while line != len(weather_pd["time"]):
        weather_pd["time"][line] = dt.strptime(weather_pd["time"][line], 
                                               '%H:%M').time()
        line = line + 1
    
    ### arrival
    # arr date and time connect to weather time
    # first, crate date and time columns in target dataset
    delay_ML["arr_date"] = [np.NaN] * len(delay_ML)
    delay_ML["arr_time_hm"] = [np.NaN] * len(delay_ML)
    
    #secind, fill dummies with date and time values
    line = 0
    while line != len(delay_ML):
        delay_ML["arr_date"][line], delay_ML["arr_time_hm"][line]= delay_ML.arr_time[line].date(), 
                                                                   delay_ML.arr_time[line].time()
        line = line + 1
       
    
    ### compare time and choose the closest to minutes = 00. Since we have hourly weather, we should have time hour format
    line = 0
    while line != len(delay_ML):
        if delay_ML["arr_time_hm"][line].minute <= 30 
        and delay_ML["arr_time_hm"][line].minute != 0: 
            delay_ML["arr_time_hm"][line] = dt.strptime(
                str(delay_ML["arr_time_hm"][line].hour)+":00", '%H:%M').time()
        elif delay_ML["arr_time_hm"][line].minute > 30 
        and delay_ML["arr_time_hm"][line].minute != 0:
            if delay_ML["arr_time_hm"][line].hour+1 != 24:
                delay_ML["arr_time_hm"][line] = dt.strptime(
                    str(delay_ML["arr_time_hm"][line].hour+1)+":00", '%H:%M').time()
            else:
                delay_ML["arr_time_hm"][line] = dt.strptime("00:00", '%H:%M').time()
        else:
            delay_ML["arr_time_hm"][line] = delay_ML["arr_time_hm"][line]
        line = line + 1
    
    # connect delay_ML and weather_pd by date and time
    line_flights = 0
    line_weather = 0
    weather_arr = pd.DataFrame([])
    while line_flights != len(delay_ML):
        if (delay_ML["arr_date"][line_flights] 
            and delay_ML["arr_time_hm"][line_flights]) == (weather_pd["arr_date"][line_weather] 
                                                           and weather_pd["time"][line_weather]):
            weather_arr = weather_arr.append(weather_pd.iloc[line_weather, :], 
                                             ignore_index=True)
            line_flights = line_flights + 1
            line_weather = line_weather + 1
        else:
            line_weather = line_weather + 1
        
    # extract weather description to pandas
    line = 0
    while line != len(weather_arr):
        weather_arr["weatherDesc"][line] = weather_arr["weatherDesc"][line][0]["value"]
        line = line + 1
        
    weather_arr = weather_arr[['time',
     'tempC',
     'windspeedKmph',
     'winddirDegree',
    # 'weatherCode',
     'weatherDesc',
     'precipMM',
     'humidity',
     'visibility',
     'pressure',
     'cloudcover',
     'HeatIndexC',
     'DewPointC',
     'WindChillC',
     'WindGustKmph',
     'FeelsLikeC',
     "arr_date"]]
    
    
    delay_ML[[
     'arr_tempC',
     'arr_windspeedKmph',
     'arr_winddirDegree',
    # 'weatherCode',
     'arr_weatherDesc',
     'arr_precipMM',
     'arr_humidity',
     'arr_visibility',
     'arr_pressure',
     'arr_cloudcover',
     'arr_HeatIndexC',
     'arr_DewPointC',
     'arr_WindChillC',
     'arr_WindGustKmph',
     'arr_FeelsLikeC']] = weather_arr[[
     'tempC',
     'windspeedKmph',
     'winddirDegree',
    # 'weatherCode',
     'weatherDesc',
     'precipMM',
     'humidity',
     'visibility',
     'pressure',
     'cloudcover',
     'HeatIndexC',
     'DewPointC',
     'WindChillC',
     'WindGustKmph',
     'FeelsLikeC'
    ]]
         
             
         
    ############## deparure
    # same transformations for departure varables
    unique_dates = pd.to_datetime(delay_ML["dep_time"].unique())
    unique_dates = unique_dates.date
    unique_dates = pd.to_datetime(unique_dates).unique()
    unique_dates = unique_dates.date
    #weather
    ## arrival
    API = "key=" + weather_api_key + "&"
    method = "q="+str(dep_airport_lat)+","+str(dep_airport_lng)+"&"
    api_base = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?'
    line = 0
    weather_pd = pd.DataFrame([])
    weather_date = []
    while line != len(unique_dates):
        date = str(unique_dates[line])
        api_result_weather = requests.get(api_base+
                                          API+
                                          method+
                                          "format=json&"+
                                          "date="+date+
                                          "&tp=1")
        api_response_weather = api_result_weather.json()
        weather_pd = weather_pd.append(pd.DataFrame.from_dict(
            api_response_weather["data"]["weather"][0]["hourly"]))
        weather_date = np.append(weather_date, [date] * 24)
        line = line + 1
        
    weather_pd["dep_date"] = weather_date
    weather_pd = weather_pd[['time', #hmm
     'tempC',
    # 'tempF',
    # 'windspeedMiles',
     'windspeedKmph',
     'winddirDegree',
    # 'winddir16Point',
     'weatherCode',
    # 'weatherIconUrl',
     'weatherDesc',
     'precipMM',
    # 'precipInches',
     'humidity',
     'visibility',
    # 'visibilityMiles',
     'pressure', 
    # 'pressureInches',
     'cloudcover', 
     'HeatIndexC',
    # 'HeatIndexF',
     'DewPointC',
    # 'DewPointF',
     'WindChillC',
    # 'WindChillF',
    # 'WindGustMiles',
     'WindGustKmph',
     'FeelsLikeC',
     "dep_date",
    # 'FeelsLikeF',
    # 'uvIndex'
    ]]
    weather_pd = weather_pd.reset_index(drop = True)
    
    #show just date
    line = 0
    while line != len(weather_pd):
        weather_pd["dep_date"][line] = dt.strptime(weather_pd["dep_date"][line], 
                                                   '%Y-%m-%d').date()
        line = line + 1
    
    #reformat time
    weather_line = 0
    while weather_line < len(weather_pd):
        line = 0
        while line != 24:
            if line <= 9:
                weather_pd["time"][weather_line] = weather_pd["time"][weather_line][0]+":00"
                line = line + 1
                weather_line = weather_line + 1
            elif line >9: 
                weather_pd["time"][weather_line] = weather_pd["time"][weather_line][0:2]+":00"
                line = line + 1
                weather_line = weather_line + 1
        
    line = 0
    while line != len(weather_pd["time"]):
        weather_pd["time"][line] = dt.strptime(weather_pd["time"][line], 
                                               '%H:%M').time()
        line = line + 1
    
    #dep date and time to connect to weather
    delay_ML["dep_date"] = [np.NaN] * len(delay_ML)
    delay_ML["dep_time_hm"] = [np.NaN] * len(delay_ML)
    line = 0
    while line != len(delay_ML):
        delay_ML["dep_date"][line], delay_ML["dep_time_hm"][line]= delay_ML.dep_time[line].date(), 
                                                                   delay_ML.dep_time[line].time()
        line = line + 1
    
    
    ### compare time and choose the closest
    line = 0
    while line != len(delay_ML):
        if delay_ML["dep_time_hm"][line].minute <= 30 
        and delay_ML["dep_time_hm"][line].minute != 0: 
            delay_ML["dep_time_hm"][line] = dt.strptime(
                str(delay_ML["dep_time_hm"][line].hour)+":00", '%H:%M').time()
        elif delay_ML["dep_time_hm"][line].minute > 30 
        and delay_ML["dep_time_hm"][line].minute != 0:
            if delay_ML["dep_time_hm"][line].hour+1 != 24:
                delay_ML["dep_time_hm"][line] = dt.strptime(
                    str(delay_ML["dep_time_hm"][line].hour+1)+":00", '%H:%M').time()
            else:
                delay_ML["dep_time_hm"][line] = dt.strptime("00:00", '%H:%M').time()
        else:
            delay_ML["dep_time_hm"][line] = delay_ML["dep_time_hm"][line]
        line = line + 1
         
    line_flights = 0
    line_weather = 0
    weather_dep = pd.DataFrame([])
    while line_flights != len(delay_ML):
        if (delay_ML["dep_date"][line_flights] 
            and delay_ML["dep_time_hm"][line_flights]) == (weather_pd["dep_date"][line_weather] 
                                                           and weather_pd["time"][line_weather]):
            weather_dep = weather_dep.append(weather_pd.iloc[line_weather, :], 
                                             ignore_index=True)
            line_flights = line_flights + 1
            line_weather = line_weather + 1
        else:
            line_weather = line_weather + 1
        
    
    line = 0
    while line != len(weather_dep):
        weather_dep["weatherDesc"][line] = weather_dep["weatherDesc"][line][0]["value"]
        line = line + 1
        
    weather_dep = weather_dep[['time',
     'tempC',
     'windspeedKmph',
     'winddirDegree',
    # 'weatherCode',
     'weatherDesc',
     'precipMM',
     'humidity',
     'visibility',
     'pressure',
     'cloudcover',
     'HeatIndexC',
     'DewPointC',
     'WindChillC',
     'WindGustKmph',
     'FeelsLikeC',
     "dep_date"]]
    
    delay_ML[[
     'dep_tempC',
     'dep_windspeedKmph',
     'dep_winddirDegree',
    # 'weatherCode',
     'dep_weatherDesc',
     'dep_precipMM',
     'dep_humidity',
     'dep_visibility',
     'dep_pressure',
     'dep_cloudcover',
     'dep_HeatIndexC',
     'dep_DewPointC',
     'dep_WindChillC',
     'dep_WindGustKmph',
     'dep_FeelsLikeC']] = weather_dep[[
     'tempC',
     'windspeedKmph',
     'winddirDegree',
    # 'weatherCode',
     'weatherDesc',
     'precipMM',
     'humidity',
     'visibility',
     'pressure',
     'cloudcover',
     'HeatIndexC',
     'DewPointC',
     'WindChillC',
     'WindGustKmph',
     'FeelsLikeC']]
         
    delay_ML = delay_ML[[
        "status",
    'flight_iata',
     'dep_iata',
     'dep_time',
     'dep_delay',
     'dep_actual',
     'dep_terminal',
    # 'dep_gate',
     'arr_iata',
     'arr_time',
     'arr_delay', 
     'arr_actual',
     'arr_terminal',
    # 'arr_gate',
     'airline_iata',
    # 'cs_airline_iata',
     'arr_airport_lat',
     'arr_airport_lng',
     'dep_airport_lat',
     'dep_airport_lng',
     'arr_date',
     'arr_time_hm',
     'arr_tempC',
     'arr_windspeedKmph',
     'arr_winddirDegree',
     'arr_weatherDesc',
     'arr_precipMM',
     'arr_humidity',
     'arr_visibility',
     'arr_pressure',
     'arr_cloudcover',
    # 'arr_HeatIndexC',
     'arr_DewPointC',
     'arr_WindChillC',
     'arr_WindGustKmph',
    # 'arr_FeelsLikeC',
     'dep_date',
     'dep_time_hm',
     'dep_tempC',
     'dep_windspeedKmph',
     'dep_winddirDegree',
     'dep_weatherDesc',
     'dep_precipMM',
     'dep_humidity',
     'dep_visibility',
     'dep_pressure',
     'dep_cloudcover',
    # 'dep_HeatIndexC',
     'dep_DewPointC',
     'dep_WindChillC',
     'dep_WindGustKmph',
    # 'dep_FeelsLikeC',
    # 'arr_time_hm_half',
    # 'dep_time_hm_half'
    ]]
    
    line = 0
    while line != len(delay_ML):
        if str(delay_ML["dep_delay"][line]) =="nan":
            delay_ML["dep_delay"][line] = int(0)
        line = line + 1
        
    line = 0
    while line != len(delay_ML):
        if str(delay_ML["arr_delay"][line]) =="nan":
            delay_ML["arr_delay"][line] = int(0)
        line = line + 1
    
    delay_ML.to_csv(csv_path)

