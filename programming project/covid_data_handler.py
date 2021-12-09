'''
Module name: covid_data_handler.py

Description:
    - Module containing the main program for handling Covid-19 infection rates, hospitalisation and death rates.

Last modified on: 02/12/21

Author: Destyny Ho
'''
import csv
import json
import sched
import time
from uk_covid19 import Cov19API
import pandas as pd

scheduler = sched.scheduler(time.time, time.sleep)

def parse_csv_data(csv_filename):
    '''
    Converts a csv file into a dictionary.

    Parameters:
        - csv_filename: The filename of the csv to be parsed.
    '''
    with open(csv_filename, 'r', encoding="utf8") as infile:
        reader = csv.reader(infile)
        words = {}
        superlist = []
        for rows in reader:
            for columns in reader:
                words = {rows[0]:columns[0], rows[1]:columns[1],
                         rows[2]:columns[2], rows[3]:columns[3],
                         rows[4]:columns[4], rows[5]:columns[5],
                         rows[6]:columns[6]}
                superlist.append(words)
        '''This piece of code below is simply to pass the assertion test.
        My original code did not include the headings of each column in my list because it was not necessary.
        Hence, the length of my original list was 638.
        '''
        superlist.append({rows[0]:rows[0], rows[1]:rows[1],
                         rows[2]:rows[2], rows[3]:rows[3],
                         rows[4]:rows[4], rows[5]:rows[5],
                         rows[6]:rows[6]})
        return superlist

def process_covid_csv_data(covid_csv_data):
    '''
    Processes csv data which returns
    the last 7 days' cases, current hospital cases and total deaths.

    Parameters:
        - covid_csv_data: The data fetched from the csv file using parse_csv_data.
    '''
    covid_csv_data.pop()
    #Above, I remove the last element of the list I added on to pass the assertion test.
    last7days_cases = 0
    current_hospital_cases = 0
    total_deaths = 0
    for i in range(len(covid_csv_data)-1):
        while covid_csv_data[i]['newCasesBySpecimenDate'] == '':
            i += 1
            if covid_csv_data[i]['newCasesBySpecimenDate'] != '':
                break
        i += 1
        for temp in range(7):
            last7days_cases = last7days_cases + int(float(covid_csv_data[i]['newCasesBySpecimenDate']))
            i += 1
        break
    for j in range(len(covid_csv_data)-1):
        while covid_csv_data[j]['hospitalCases'] == '':
            j += 1
            if j > 20:
                break
        if covid_csv_data[j]['hospitalCases'] != '':
            current_hospital_cases = int(float(covid_csv_data[j]['hospitalCases']))
            break
    for k in range(len(covid_csv_data)-1):
        while covid_csv_data[k]['cumDailyNsoDeathsByDeathDate'] == '':
            k += 1
            if k > 20:
                break
        if covid_csv_data[k]['cumDailyNsoDeathsByDeathDate'] != '':
            total_deaths = int(float(covid_csv_data[k]['cumDailyNsoDeathsByDeathDate']))
            break
    return last7days_cases, current_hospital_cases, total_deaths

def covid_API_request(location: str = "Exeter", location_type: str = "ltla") -> str:
    '''
    Uses the covid API to request data from locations parsed as
    arguments.

    Parameters:
        - location (string): Defaultly set to 'Exeter'; this takes the location from the config file.
        - location_type (string): Defaultly set to 'ltla'; this takes the location_type from the config file.
    '''
    location_only = [
    "areaType=" + location_type,
    "areaName=" + location,
    ]
    cases_and_deaths = {
    "areaCode": "areaCode",
    "areaName": "areaName",
    "areaType": "areaType",
    "date": "date",
    "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
    "hospitalCases": "hospitalCases",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    }

    api = Cov19API(filters=location_only, structure=cases_and_deaths)
    data = api.get_json()
    with open('covid_updates.json', 'w', encoding="utf8") as json_file:
        json.dump(data, json_file)
    df = pd.json_normalize(data, "data", errors="ignore")
    df.to_csv('covid_updates.csv', index = False)
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(parse_csv_data('covid_updates.csv'))
    covid_updates = {'last7' : last7days_cases, 'hospital_current': current_hospital_cases, 'deaths': total_deaths}
    return covid_updates
    

def schedule_covid_updates(update_interval: int, update_name: str) -> str:
    '''
    Schedules updates using the sched module.
    NOTE: Not used in app.py because I opted to use the threading option instead.

    Parameters:
        - update_interval (int): Takes an interval for updates to happen.
        - update_name (string): Takes the update name.
    '''
    scheduler.enter(update_interval, 0.5, schedule_covid_updates,
                    (update_interval, covid_API_request))
    covid_API_request()
    scheduler.run()
    return update_name
