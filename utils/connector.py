import logging

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


CREDENTIALS_FILE = 'utils\connect.json' # YOUR KEY

spreadsheet_id_1 = " # YOUR spreadsheet_id_1 for all users "
spreadsheet_id_2 = ' # YOUR spreadsheet_id_2 for users who passed face control'
spreadsheet_id_3 = ' # YOUR spreadsheet_id_3 for users who whenever passed face control'


class Connector:
    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = build('sheets', 'v4', http=httpAuth)
     
    def insert_values(self, sheet_id, values, range_):
        try:
            self.service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id,
                                                             body={"valueInputOption": "USER_ENTERED",
                                                                   "data": [{"range": range_,
                                                                             "majorDimension": "ROWS",
                                                                             "values": [values]}]}).execute()
        except Exception as e:
            logging.info(e)
    
    def append_values(self, sheet_id, values, range_):
        try:
            self.service.spreadsheets().values().append(spreadsheetId=sheet_id,
                                                        range=range_,
                                                        valueInputOption="USER_ENTERED",
                                                        body={"majorDimension": "ROWS",
                                                              "values": [values]}).execute()
        
        except Exception as e:
            logging.info(e)
    
    def clear_sheet(self, spreadsheet_id, range_="A2:Z200"):
        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_,
            ).execute()
        except Exception as e:
            logging.info(e)
    
    def get_telegram_ids(self, spreadsheet_id, range_="A2:A"):
        try:
            values = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_,
                majorDimension='COLUMNS'
            ).execute()
            return values
        except Exception as e:
            logging.info(e)

