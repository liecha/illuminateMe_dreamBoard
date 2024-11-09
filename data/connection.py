import os.path
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try: 
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    start = '2024-11-04T00:00:00.000000Z'
    #date = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat() + "Z"  # 'Z' indicates UTC time
    #print(type(date))
    print("Getting the upcoming events from 2024-11-04")
    calendars = [
        'primary',  # food
        'sc3ios5mprpkoi8179bh2argg0@group.calendar.google.com', # walk
        '2e7bb5ea43738363ea033e8081f6c250499d1b16604d331bf5033b8f6f56413d@group.calendar.google.com' # training
        ] 
    
    for j in range(0, len(calendars)):
        events_result = (
            service.events()
            .list(
                calendarId=calendars[j],
                timeMin=start,
                maxResults=100,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        df_events = pd.DataFrame(events)
        storage = []
        for i in range(0, len(df_events)):
            if calendars[j] == 'primary':               
                data = {
                    'label': df_events['summary'].iloc[i],
                    'start': df_events['start'].iloc[i].get("dateTime", df_events['start'].iloc[i].get("date")),
                    'end': df_events['end'].iloc[i],
                    'note': df_events['description'].iloc[i],
                    'unknown_1': df_events['sequence'].iloc[i],
                    }
                storage.append(data)
            else:
                data = {
                    'label': df_events['summary'].iloc[i],
                    'start': df_events['start'].iloc[i].get("dateTime", df_events['start'].iloc[i].get("date")),
                    'end': df_events['end'].iloc[i],
                    'note': df_events['sequence'].iloc[i],
                    'unknown_1': df_events['sequence'].iloc[i],
                    }
                storage.append(data)
        if calendars[j] == 'primary':            
            df_food = pd.DataFrame(storage)
            df_food.to_csv('irl_calendars/food_irl.csv', index=False)
        if calendars[j] == 'sc3ios5mprpkoi8179bh2argg0@group.calendar.google.com':
            df_walk = pd.DataFrame(storage)
            df_walk.to_csv('irl_calendars/walk_irl.csv', index=False)
        if calendars[j] == '2e7bb5ea43738363ea033e8081f6c250499d1b16604d331bf5033b8f6f56413d@group.calendar.google.com':
            df_training = pd.DataFrame(storage)
            df_training.to_csv('irl_calendars/training_irl.csv', index=False)
        
    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()