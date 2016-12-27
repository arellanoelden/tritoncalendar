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
import cgi

SCOPES = 'https://www.googleapis.com/auth/calendar'
LOGIN_URL = "https://a4.ucsd.edu/tritON/Authn/UserPassword"
TRITONLINK_URL = "http://mytritonlink.ucsd.edu/"
DASHBOARD_URL = "https://act.ucsd.edu/myTritonlink20/display.htm"

TIMEZONE = "America/Los_Angeles"
WEEKDAYS = ["MO", "TU", "WE", "TH", "FR"] 
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

def get_datetime(day, hour, minute):
    
    return datetime.datetime(FIRST_DAY[0], FIRST_DAY[1], 
                             FIRST_DAY[2] + day, 
                             hour, minute).isoformat()
    

def parse_datetime(time):

    hour, minute, ampm = re.match(r"(\d+):(\d+)(a|p)m", time).groups()
    hour, minute = int(hour), int(minute)
    return hour + 12 if ampm == "p" else hour, minute

def parse_datetimes(day, time):

    # Parse Times
    s_time, e_time = time.split(" - ")
    s_hour, s_minute = parse_datetime(s_time)
    e_hour, e_minute = parse_datetime(e_time)

    # Build google api calendar time structures 
    start = {'dateTime': get_datetime(day, s_hour, s_minute), 
             'timeZone': TIMEZONE}

    end = {'dateTime': get_datetime(day, e_hour, e_minute),
           'timeZone': TIMEZONE}

    return start, end

def build_event(day, course_string):
    
    event = {}
    event["recurrence"] = ["RRULE:FREQ=WEEKLY;COUNT=10;BYDAY={}".format(WEEKDAYS[day])]
    event["start"], event["end"] = parse_datetimes(day, course_string[1])
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


def get_calendar(service, calendar_name):

    # Check if calendar exists
    calendar_list = service.calendarList().list().execute()
    for calendar in calendar_list["items"]:
        if calendar["summary"] == calendar_name:
            return calendar["id"]

    # if not, create one
    calendar_id = service.calendars().insert(body={'summary':calendar_name, 
                                                   'timeZone': TIMEZONE}).execute()['id']
    service.calendarList().insert(body={"id": calendar_id}).execute()
    return calendar_id


#uname = input("Username: ");
#pword = getpass();

form = cgi.FieldStorage();
uname = form.getvalue('uname');
pword = form.getvalue('pword');

credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)

calendar_name = input("Calendar Name: ")
calendar_id = get_calendar(service, calendar_name)

r = get_page(uname, pword)
soup = BeautifulSoup(r.text, "html.parser")

for i, tag in enumerate(soup.find_all("table")[0].find_all("td")[:-1]):
    day = i % 5
    if tag.span is not None:
        course = list(map(lambda x: x.strip(), tag.span.text.split("\n")))
        event = build_event(day, course)
        service.events().insert(calendarId=calendar_id, body=event).execute()

