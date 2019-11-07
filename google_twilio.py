import argparse
import ast
import os
import pickle
from threading import Thread
import time

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from twilio.rest import Client

GOOGLE_SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
GOOGLE_RANGE_NAME = os.environ.get('RANGE_NAME')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')


def get_google_data():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))


def send_twilio_texts(timestamp_msg):
    for timestamp, msg in timestamp_msg.items():
        Thread(target=send_msg_later, args=(msg, int(timestamp))).start()


def send_msg_later(msg, delay):
    time.sleep(delay)
    message = TWILIO_CLIENT.messages.create(
        to="", from_="", body=msg
    )


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Send text on interval")
    parser.add_argument('-d', '--data', help="Text message data")
    # main()
    args = parser.parse_args()
    print(args.data)

    if not TWILIO_ACCOUNT_SID:
        TWILIO_ACCOUNT_SID = input("TWILIO_ACCOUNT_SID: ")
    if not TWILIO_AUTH_TOKEN:
        TWILIO_AUTH_TOKEN = input("TWILIO_AUTH_TOKEN: ")
    TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    data = ast.literal_eval(args.data)
    send_twilio_texts(data)
    print("threads are running...")
