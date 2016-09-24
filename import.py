import requests
from bs4 import BeautifulSoup
from getpass import getpass

LOGIN_URL = "https://a4.ucsd.edu/tritON/Authn/UserPassword"
TRITONLINK_URL = "http://mytritonlink.ucsd.edu/"
DASHBOARD_URL = "https://act.ucsd.edu/myTritonlink20/display.htm"

uname = input()
pword = getpass()

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
    try:
        r = s.post(target_url, data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        courses = []
        for tag in soup.find_all(class_ = "class"):
            course = list(map(lambda x: x.strip(), tag.text.split("\n")))
            print(course)

    except:
        print("Invalid Username/Password")

