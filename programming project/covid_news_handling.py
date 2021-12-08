'''
Module name: covid_news_handling.py

Description:
    - Module containing the main program for handling all Covid-19 related news.

Last modified on: 02/12/21

Author: Destyny Ho
'''
import json
from datetime import date, timedelta
import pandas as pd
from newsapi import NewsApiClient

today = date.today()
twodaysago = today - timedelta(2)
today = today.strftime("%Y-%m-%d")
twodaysago = twodaysago.strftime('%Y-%m-%d')

with open('config.json', encoding="utf8") as json_file:
    data = json.load(json_file)
    api = data["API key"]

newsapi = NewsApiClient(api_key=api)

def news_API_request(covid_terms: str = "Covid COVID-19 coronavirus"):
    '''
    Fetches all the covid articles that include the terms parsed into the argument.

    Parameters:
        - covid_terms (string): Set defaultly to "Covid COVID-19 coronavirus", this searches all the terms for covid in the news articles.

    Returns the covid articles gathered from the news API.
    '''
    covid_articles = newsapi.get_everything(q=covid_terms,
                                      from_param=twodaysago,
                                      to=today,
                                      language='en',
                                      page=2)
    return covid_articles

def update_news(update_name: str = "temp variable"):
    '''
    Updates the covid news.

    Parameters:
        - update_name (string): Takes the update name.

    Returns the update name.
    '''
    articles = news_API_request()
    with open('covid_articles.json', 'w', encoding="utf8") as json_file:
        json.dump(articles, json_file)
    df = pd.json_normalize(articles, "articles", errors="ignore")
    df.to_csv('covid_articles.csv', index = False)
    return update_name
