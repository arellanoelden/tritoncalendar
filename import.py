import requests
from bs4 import BeautifulSoup
from getpass import getpass
from apiclient import discovery
import httplib2
import os
import re
import datetime
import oauth2client
from oauth2client import client
from oauth2client import tools

SCOPES = 'https://www.googleapis.com/auth/calendar'
LOGIN_URL = "https://a4.ucsd.edu/tritON/Authn/UserPassword"
TRITONLINK_URL = "http://mytritonlink.ucsd.edu/"
DASHBOARD_URL = "https://act.ucsd.edu/myTritonlink20/display.htm"
WEEKDAYS = ["MO", "TU", "WE", "TH", "FR"]

TIMEZONE = "America/Los_Angeles"
FIRST_DAY = (2016, 9, 26)

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'clt.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets("creds.scrt", SCOPES)
        flow.user_agent = "Command Line Testing"
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_datetime(i, hour, minute):
    datetime.datetime(FIRST_DAY[0], FIRST_DAY[1], FIRST_DAY[2] + i % 5, hour, minute)).isoformat(),

def parse_datetimes(i, time):
    s_hour, s_minute, e_hour, e_minute, ampm = 
                    re.match(r"(\d+):(\d+) - (\d+):(\d+)(a|p)m", start).groups()
    s_hour, e_hour = (s_hour + 12, e_hour + 12) if ampm = "p" else (s_hour, e_hour)
    start = {'dateTime': get_datetime(i, s_hour, s_minute), 
             'timeZone': TIMEZONE}

    end = {'dateTime': get_datetime(i, e_hour, e_minute),
           'timeZone': TIMEZONE}
    return start, end

def build_event(i, course_string):
    event = {}
    event["recurrence"] = ["RRULE:FREQ=WEEKLY;COUNT=10;BYDAY={}".format(day)]
    event["start"], event["end"] = parse_datetimes(i, course_string[1])
    event["location"] = course_string[3] 
    event["summary"] = course_string[2]
    return event

def get_page(uname, pword):
    payload = {
            "urn:mace:ucsd.edu:sso:authmethod": "urn:mace:ucsd.edu:sso:studentsso",
            "submit": "submit",
            "urn:mace:ucsd.edu:sso:username": uname,
            "urn:mace:ucsd.edu:sso:password": pword,
            "initAuthMethod": "urn:mace:ucsd.edu:sso:studentsso"
            }

    with requests.Session() as s:
        # Login post
        r = s.get(TRITONLINK_URL)
        r = s.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))
        
        # Manually complete login
        soup = BeautifulSoup(r.text, "html.parser")
        payload = {}
        for inputs in soup.find_all('input'):
            payload[inputs.get('name')] = inputs.get('value')
        target_url = soup.find('form').get('action')

        # Scrape course information
        r = s.post(target_url, data=payload)
        return r


uname = input()
pword = getpass()


    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    soup = BeautifulSoup(r.text, "html.parser")
    for i, tag in enumerate(soup.find_all("table")[0].find_all("td")):
        day = WEEKDAYS[i % 5]
        course = list(map(lambda x: x.strip(), tag.span.text.split("\n")))
                service.events().insert(calendarId='primary', body=event).execute()



