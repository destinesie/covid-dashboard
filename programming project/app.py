'''
Module name: app.py

Description:
    - Module containing the main program for running the COVID tracking website.
    - This program writes to an 'index.html' template using Flask.

Last modified on: 07/12/21

Author: Destyny Ho
'''
import logging
import csv
import json
from datetime import datetime, timedelta
from threading import Timer
from flask import Flask, render_template, request, Markup
from covid_data_handler import (parse_csv_data, process_covid_csv_data,
                                covid_API_request)
from covid_news_handling import update_news

app = Flask(__name__)
logging.basicConfig(filename='sys.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level = logging.DEBUG)

with open('config.json', encoding="utf8") as json_file:
    data = json.load(json_file)
    covid_location = data["location"]
    covid_location_type = data["location type"]
    nation_location = data["nation location"]
    nation_location_type = data["nation location type"]

threads = []
update_tracking = []
list_of_updates = []
deleted_articles = []

def get_local_infections():
    '''
    Gets the local infection rates of the last seven days.
    
    Returns this value.
    '''
    covid_local = covid_API_request(covid_location, covid_location_type)
    covid_cases = covid_local['last7']
    logging.info('Infection rates fetched.')
    return covid_cases

def get_national_infections():
    '''
    Gets the national infection rates, hospital cases and death rates.
    
    Returns these values.
    '''
    updates = covid_API_request(nation_location, nation_location_type)
    covid_cases = updates['last7']
    hospital_covid_cases = updates['hospital_current']
    covid_deaths = updates['deaths']
    logging.info('National infection rates, hospital cases and deaths fetched.')
    return covid_cases, hospital_covid_cases, covid_deaths

def get_news():
    '''
    Gets the news from the news API.
    
    Returns a list of dictionaries of articles.
    '''
    update_news()
    words = {}
    articles_list = []
    with open('covid_articles.csv', 'r', encoding="utf8") as infile:
        reader = csv.reader(infile)
        for rows in reader:
            for columns in reader:
                news_titles = columns[1]
                news_hyperlink = columns[3]
                news_hyperlink = news_hyperlink
                news_contents = columns[6]
                words = {'title':news_titles, 'content':news_contents + " " + Markup('<a href={}>Read more</a>'.format(str(news_hyperlink)))}
                articles_list.append(words)
                logging.info('News fetched from News API.')
    return articles_list

def schedule_update(update_name: str, hour_input: int, minute_input: int, repeat: str, covid: str, news: str, update_time: str) -> list:
    '''
    Schedules updates for either the news or covid,
    taking into consideration whether repeats have been taken or not.
    
    Parameters:
        - update_name (string): The name of the update the user has entered in the update label.
        - hour_input (int): The hour input of the user, converted into an integer.
        - minute_input (int): The minute input of the user, converted into an integer.
        - repeat (string): If repeat is 'repeat', then the user has checked the 'repeat' box; else, the user has not.
        - covid (string): If covid is 'covid', then the user has checked the 'covid' box; else, the user has not.
        - news (string): If news is 'news', then the user has checked the 'news' box; else, the user has not.
        - update_time (string): The time input of the user so that it can be appended to the contents of the widget.
        
    Returns a list to be appended to the widgets list, so that the widgets can be updated.
    '''
    global list_of_updates
    global threads
    global update_tracking
    today = datetime.today()
    time = str(today.time())
    hour_now = int(time[0]+time[1])
    minute_now = int(time[3]+time[4])
    def fetch_news():
        '''
        Fetches the news and checks to make sure there are no repeat articles.
        Begins the timing for the scheduling if there is a repeat.
        '''
        global list_of_articles
        list_of_articles = get_news()
        for i in range(len(list_of_articles)):
            if list_of_articles[i] in deleted_articles:
                del list_of_articles[i]
                logging.info('News fetched from News API.')
        if repeat == "repeat":
            t1 = Timer(60*60*24, schedule_update, args=(update_name, hour_input, minute_input,
                                                        repeat, covid, news, update_time))
            threads.append(t1)
            update_tracking.append(update_name)
            t1.start()
            logging.info(update_name + ': Repeat scheduled.')
        else:
            for i in range(len(list_of_updates)):
                try:
                    if list_of_updates[i]['title'] == update_name:
                        cancel_update(update_name)
                        del list_of_updates[i]
                        logging.info(update_name + ': Widget removed.')
                except IndexError:
                    logging.error(update_name + ': IndexError.')
                    break
    def fetch_covid():
        '''
        Fetches the covid data.
        Begins the timing for the scheduling if there is a repeat.
        '''
        global list_of_updates
        global local_infections, national_infections
        global hospital_cases, deaths
        local_infections = get_local_infections()
        national_infections, hospital_cases, deaths = get_national_infections()
        hospital_cases = str(hospital_cases) + ' hospital cases'
        deaths = str(deaths) + ' total deaths'
        logging.info('Infection rates fetched from Covid API.')
        if repeat == "repeat":
            t1 = Timer(60*60*24, schedule_update, args=(update_name, hour_input, minute_input,
                                                        repeat, covid, news, update_time))
            threads.append(t1)
            update_tracking.append(update_name)
            t1.start()
            logging.info(update_name + ': Repeat scheduled.')
        else:
            for i in range(len(list_of_updates)):
                try:
                    if list_of_updates[i]['title'] == update_name:
                        cancel_update(update_name)
                        del list_of_updates[i]
                        logging.info(update_name + ': Widget removed.')
                except IndexError:
                    logging.error(update_name + ': IndexError.')
                    break
    temp_string = 'Next update at: ' + update_time
    if  (hour_now > hour_input) or ((hour_now == hour_input) and (minute_now >= minute_input)):
        timing = today.replace(day = today.day+1, hour = hour_input,
                               minute = minute_input, second = 0,
                               microsecond = 0) + timedelta(days=1)
    else:
        timing = today.replace(hour = hour_input, minute = minute_input,
                               second = 0, microsecond = 0)
    delta_t = timing-today
    secs = delta_t.seconds+1
    if news == "news":
        t = Timer(secs, fetch_news)
        temp_string = temp_string + '; updating news'
        threads.append(t)
        update_tracking.append(update_name)
        t.start()
    if covid == "covid-data":
        t = Timer(secs, fetch_covid)
        temp_string = temp_string + '; updating covid data'
        threads.append(t)
        update_tracking.append(update_name)
        t.start()
    if repeat == "repeat":
        temp_string = temp_string + '; repeating daily'
    temp_dict = {'title': update_name, 'content': temp_string}
    temp_list = []
    temp_list.append(temp_dict)
    return temp_list

def cancel_update(update_name: str):
    '''
    Cancels scheduled updates.
    
    Parameters:
        - update_name (string): The name of the update the user has entered in the update label. Used to keep track of threads to cancel.
    '''
    global update_tracking
    global threads
    for i in range(len(update_tracking)):
        if update_tracking[i] == update_name:
            threads[i].cancel()
            logging.info(update_name + ': Update cancelled.')
        try:
            assert len(update_tracking) == len(threads)
        except AssertionError:
            logging.error(update_name + ": Assertion Error.")
            pass

local_infections = get_local_infections()
national_infections, hospital_cases, deaths = get_national_infections()
hospital_cases = str(hospital_cases) + ' hospital cases'
deaths = str(deaths) + ' total deaths'
list_of_articles = get_news()

@app.route('/')
def index():
    '''
    What is first observed when the site is brought up.
    '''
    with app.app_context():
        return render_template('index.html', image = "zhongli.jpg", title="COVID API", location = covid_location,
                               local_7day_infections = local_infections,
                               national_7day_infections = national_infections,
                               nation_location = nation_location, hospital_cases = hospital_cases,
                               deaths_total = deaths, news_articles = list_of_articles,
                               updates = list_of_updates)
        

@app.route('/index', methods=['GET'])
def get_update():
    '''
    Handles website interface.
    '''
    if request.method == 'GET':
        repeated = False
        page_title = "COVID API"
        update_name = request.values.get("two")
        update_time = request.values.get("update")
        update_time = str(update_time)
        repeat = request.values.get("repeat")
        covid = request.values.get("covid-data")
        news = request.values.get("news")
        full_url = str(request.url)
        global list_of_updates
        for i in range(len(list_of_updates)):
            if list_of_updates[i]['title'] == update_name:
                page_title = "MESSAGE: Sorry, that update title is already in use."
                repeated = True
        if repeated is False:
            if ((update_name is not None) and (update_time != '') and ((covid is not None) or (news is not None))):
                hour_input = int(update_time[0]+update_time[1])
                minute_input = int(update_time[3]+update_time[4])
                temp_list = schedule_update(update_name, hour_input, minute_input,
                                                repeat, covid, news, update_time)
                list_of_updates = list_of_updates + temp_list
                page_title = "COVID API"
            elif ((update_time == '') or ((covid is None) or (news is None))):
                if "index?update" in full_url:
                    page_title = "MESSAGE: You either did not enter a time or pick an update option!"
        if "update_item=" in full_url:
            title = full_url.split("update_item=", 1)[1]
            title = title.replace("+", " ")
            title = title.replace("%3A", ":")
            title = title.replace("%7C", "|")
            title = title.replace("%2C", ",")
            title = title.replace("%27", "'")
            title = title.replace("%21", "!")
            if "&" in title:
                title = title.split("&", 1)[0]
            for i in range(len(list_of_updates)):
                try:
                    if list_of_updates[i]['title'] == title:
                        cancel_update(title)
                        del list_of_updates[i]
                        logging.info(title + ': Widget removed.')
                        page_title = "COVID API"
                except IndexError:
                    logging.error("Index error.")
                    break
        if "notif=" in full_url:
            global list_of_articles
            # Replaces all the values in the URL to match the title.
            news_title = full_url.split("notif=", 1)[1]
            news_title = news_title.replace("+", " ")
            news_title = news_title.replace("%3A", ":")
            news_title = news_title.replace("%7C", "|")
            news_title = news_title.replace("%2C", ",")
            news_title = news_title.replace("%27", "'")
            news_title = news_title.replace("%21", "!")
            news_title = news_title.replace("%26", "&")
            news_title = news_title.replace("%25", "%")
            news_title = news_title.replace("%22", '"')
            news_title = news_title.replace("%3B", ";")
            news_title = news_title.replace("%3F", "?")
            news_title = news_title.replace("%24", "$")
            for i in range(len(list_of_articles)):
                try:
                    if list_of_articles[i]['title'] == news_title:
                        deleted_articles.append(list_of_articles[i])
                        del list_of_articles[i]
                        page_title = "COVID API"
                except IndexError:
                    logging.error("Index error.")
                    break
        return render_template('index.html', image = "zhongli.jpg", title=page_title, location = covid_location,
                               local_7day_infections = local_infections,
                               national_7day_infections = national_infections,
                               nation_location = nation_location, hospital_cases = hospital_cases,
                               deaths_total = deaths, news_articles = list_of_articles,
                               updates = list_of_updates)
    else:
        pass

if __name__ == '__main__':
    app.run()
