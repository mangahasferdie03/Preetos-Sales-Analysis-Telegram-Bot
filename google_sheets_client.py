import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("pandas not available - using basic list operations")

load_dotenv()

class GoogleSheetsClient:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, credentials_file=None, spreadsheet_id=None):
        self.credentials_file = credentials_file or os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
        self.spreadsheet_id = spreadsheet_id or os.getenv('SPREADSHEET_ID')
        self.service = None
        self.creds = None

        if not self.credentials_file:
            raise ValueError("Credentials file path is required")
        if not self.spreadsheet_id:
            raise ValueError("Spreadsheet ID is required")

        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        # Check if it's a service account or OAuth2 credentials file
        with open(self.credentials_file, 'r') as f:
            creds_data = json.load(f)

        if creds_data.get('type') == 'service_account':
            # Service Account authentication
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=self.SCOPES)
        else:
            # OAuth2 authentication (original flow)
            creds = None
            token_file = 'token.json'

            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)

                with open(token_file, 'w') as token:
                    token.write(creds.to_json())

        self.creds = creds
        self.service = build('sheets', 'v4', credentials=creds)

    def read_sheet(self, range_name='A:Z', sheet_name=None, skip_header_rows=True):
        """Read data from Google Sheet

        Args:
            range_name: Range to read (e.g., 'A:Z', 'A1:E10')
            sheet_name: Name of the sheet tab
            skip_header_rows: If True, skips first 3 rows and uses row 4 as headers
        """
        try:
            if sheet_name:
                range_name = f"{sheet_name}!{range_name}"

            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])

            if not values:
                print('No data found.')
                return {'headers': [], 'data': []}

            if skip_header_rows and len(values) > 3:
                # Skip first 3 rows, use row 4 as headers
                headers = values[3]  # Row 4 becomes headers
                data_rows = values[4:]  # Row 5+ becomes data

                return {
                    'headers': headers,
                    'data': data_rows,
                    'raw_data': values  # Keep original data for debugging
                }
            else:
                # Return raw data if skip_header_rows is False or not enough rows
                return values

        except HttpError as error:
            print(f'An error occurred: {error}')
            return {'headers': [], 'data': []}

    def write_sheet(self, data, range_name='A1', sheet_name=None, clear_existing=False):
        """Write data to Google Sheet"""
        try:
            if sheet_name:
                range_name = f"{sheet_name}!{range_name}"

            if clear_existing:
                self.clear_sheet(range_name)

            if PANDAS_AVAILABLE and hasattr(data, 'columns'):  # pandas DataFrame
                values = [data.columns.tolist()] + data.values.tolist()
            elif isinstance(data, list):
                values = data
            else:
                raise ValueError("Data must be a pandas DataFrame or list of lists")

            body = {
                'values': values
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()

            print(f'{result.get("updatedCells")} cells updated.')
            return result

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def append_sheet(self, data, sheet_name=None):
        """Append data to Google Sheet"""
        try:
            range_name = sheet_name if sheet_name else 'Sheet1'

            if PANDAS_AVAILABLE and hasattr(data, 'values'):  # pandas DataFrame
                values = data.values.tolist()
            elif isinstance(data, list):
                values = data if isinstance(data[0], list) else [data]
            else:
                raise ValueError("Data must be a pandas DataFrame or list of lists")

            body = {
                'values': values
            }

            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()

            print(f'{result.get("updates").get("updatedCells")} cells appended.')
            return result

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def clear_sheet(self, range_name='A:Z', sheet_name=None):
        """Clear data from Google Sheet"""
        try:
            if sheet_name:
                range_name = f"{sheet_name}!{range_name}"

            result = self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                body={}
            ).execute()

            print('Sheet cleared successfully.')
            return result

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def get_sheet_info(self):
        """Get information about the spreadsheet"""
        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()

            sheets = result.get('sheets', [])
            sheet_info = []

            for sheet in sheets:
                properties = sheet.get('properties', {})
                sheet_info.append({
                    'sheet_id': properties.get('sheetId'),
                    'title': properties.get('title'),
                    'index': properties.get('index'),
                    'sheet_type': properties.get('sheetType'),
                    'grid_properties': properties.get('gridProperties', {})
                })

            return sheet_info

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
