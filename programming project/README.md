# Covid Updates App
***
## Introduction
***
Welcome to the Covid Updates App!
This is a simple dashboard designed to help the user keep track of local and national infection rates, as well as news headlines on Covid-19.

The interface includes:
* The last cumulative 7 days of local infections.
* The last cumulative 7 days of national infections.
* The amount of people currently hospitalised in the nation due to Covid-19.
* The amount of recorded deaths Covid-19 has caused in the selected nation since the outbreak.

The website automatically refreshes every 60 seconds to ensure it is regularly updated; however, it can also be manually refreshed.
If you want to refresh the website manually, please ensure the link in the URL is http://127.0.0.1:5000/index beforehand.

The dashboard also provides options to schedule updates:
* The user can label their update (please note that new updates must have different labels to previous ones!)
* The user can choose what to update from the following options:
	* Covid-19 information.
	* News articles.
	* Repeating updates.

\* Please note that the user must select either Covid-19 information or news articles to be updated for new schedules to appear.

## Prerequisites
***
The version of Python used to develop this app is Python 3.10. Please ensure your Python is up to date in your system for the app to function correctly.

## Installation
***
Please ensure that the following modules\* have been installed for the app to function correctly:
* logging
* csv
* json
* datetime
* threading
* flask
* sched
* time
* pandas

The following API are used in the program:
* newsapi\**
* uk_covid19

\*To install modules, use the 'pip install' command within the terminal.
\**Please ensure that your own API key from the News API has been generated to use the program. You can generate your own API code using the following link: https://newsapi.org/. You can then till out the API key in the config file.

## Getting started
***
To use the interface, run the app in a Python Shell.
Then proceed to navigate to the following link:
http://127.0.0.1:5000/

Note that if the app does not run, the API used to generate the information may be down.

Below are links to the documentation of the APIs used:
* uk_covid19 - https://github.com/publichealthengland/coronavirus-dashboard-api-python-sdk
* newsapi - https://newsapi.org/docs

You can change the national and local location the API is using for Covid-19 updates.
In order to accomplish this, change the 'location' and 'nation location' in the config file accordingly. Make sure that your location names are placed within speechmarks.

## Testing
*** 
Tests have been provided in the 'test' folder to ensure the code is working. Feel free to add more tests as seen fit.

You can use the module 'pytest' to automatically run all the tests, or you can manually run them in Python Shell.

To install pytest, use the command:
* pip install pytest

Please regularly test the program to ensure everything is still functioning correctly. It is recommended to test the program at least once a month.

Docstrings have been included in the code in case errors do occur and need to be fixed.

## Logging
***
A log file (sys.log) has been provided to keep track of the app as it runs.

## Details
***
Author: Destyny Ho

License: MIT Licence

Link to documentation source: docs/build/html/index.html

Acknowledgements:
* newsapi 
* uk_covid19
* Please note that the character chibi attached of Zhong-Li belongs to Mihoyo. It simply serves as a placeholder. It can be replaced with any image in the static/images directory as long as that image is named 'zhongli.jpg'.

## References
***
Below are sources used to write the code for the interface:
* https://stackoverflow.com/
* https://www.w3schools.com/
