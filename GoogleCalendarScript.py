from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
from _datetime import timedelta

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        #else: # Needed only for compatibility with Python 2.6
        #    credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def getEvents(exportFile='BICTeamCalendarExport', numEvents=1000, emailId='primary', credentials='', http='', service='', startDate=''):
    '''
    This function grabs 2500 event from a calendar and dumps the results to csv.
    This is not grabbing every field from the google calendar, but is grabbing
    some of the essentials. In this use-case a single row in the csv export is
    a single calendar event. Alternatively you can have each row be a single
    participant of a meeting, therefore having the meeting information duplicated
    across multiple rows. For this I ended up flattening the structure and am 
    only keeping track of the unique 6 domains part of a meeting invite.
    '''
    print('Getting the upcoming ' + str(numEvents) + ' events for ' + emailId)
    eventsResult = service.events().list(
        calendarId=emailId, timeMin=startDate, maxResults=numEvents, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    
    if not events:
        print('No upcoming events found.')
    for event in events:
        try:
            start = event['start']['dateTime']            
            if datetime.date(int(start[0:4]), int(start[5:7]), int(start[8:10])) > datetime.date(int(str(datetime.datetime.now() + timedelta(days=100))[0:4]), int(str(datetime.datetime.now() + timedelta(days=100))[5:7]), int(str(datetime.datetime.now() + timedelta(days=100))[8:10])):
                #print(datetime.date(int(start[0:4]), int(start[5:7]), int(start[8:10])))
                #print(datetime.date(int(str(datetime.datetime.now() + timedelta(days=100))[0:4]), int(str(datetime.datetime.now() + timedelta(days=100))[5:7]), int(str(datetime.datetime.now() + timedelta(days=100))[8:10])))
                break
        except:
            start = 'error'
        
        try:
            end = event['end']['dateTime'] 
        except:
            end = 'error'
            
        try:
            created = event['created'] 
        except:
            created = 'error'
            
        try:
            summary = event['summary'].replace(',', '')
        except:
            summary = ''
            
        try:
            numberRecipients = str(len(event['attendees']))
        except:
            numberRecipients = '0'
            
        emails = []
        index = 0
        while True:
            try:
                e = event['attendees'][index]['email'].split('@')[1].lower()
                if e == 'gmail.com':
                    e = event['attendees'][index]['email'].lower()
                index+=1
                if e != 'sisense.com' and e != 'resource.calendar.google.com' and e not in emails:
                    emails.append(e)
            except:
                break
        if len(emails) > 0:
            email0 = emails[0]
        else:
            email0 = ''
        if len(emails) > 1:
            email1 = emails[1]
        else:
            email1 = ''
        if len(emails) > 2:
            email2 = emails[2]
        else:
            email2 = ''
        if len(emails) > 3:
            email3 = emails[3]
        else:
            email3 = ''
        if len(emails) > 4:
            email4 = emails[4]
        else:
            email4 = ''
        if len(emails) > 5:
            email5 = emails[5]
        else:
            email5 = ''
            
        #print(emailId, start, summary, email0, email1, email2, email3, email4, email5)
        try:
            exportFile.write(emailId + ',' + start + ',' + end + ',' + created + ',' + summary + ',' + numberRecipients + ',' + email0 + ',' + email1 + ',' + email2 + ',' + email3 + ',' + email4 + ',' + email5)
            exportFile.write('\n')
        except:
            exportFile.write(emailId + ',' + start + ',' + end + ',' + created + ',' + '' + ',' + numberRecipients + ',' + email0 + ',' + email1 + ',' + email2 + ',' + email3 + ',' + email4 + ',' + email5)
            exportFile.write('\n')
        
if __name__ == '__main__':
    #an array of google calendars to export
    ids = ['elliott.herz@sisense.com',
            ]
    
    #create/overwrite the export csv file
    exportFile = open('GoogleCalendarExport.csv','w')
    #header for the csv file
    exportFile.write('emailId,start,end,created,summary,numberRecipients,email0,email1,email2,email3,email4,email5\n')
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    #pulling in the last 2500 going back 250 days
    #2500 google calendar event API limitation per request 
    startDate = (datetime.datetime.now() - timedelta(days=250)).isoformat() + 'Z' # 'Z' indicates UTC time
    
    #loop through all the ids to export all employee calendars
    for emailId in ids:
        getEvents(exportFile=exportFile, emailId=emailId, numEvents=2500, credentials=credentials, http=http, service=service, startDate=startDate)
    exportFile.close()