# Google Sheets API Direct Connection

A Python client for connecting directly to Google Sheets API with easy-to-use methods for reading and writing data.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Google Sheets API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create credentials (OAuth 2.0 Client ID) for a desktop application
5. Download the credentials JSON file

### 3. Configuration

1. Copy `.env.example` to `.env`
2. Update the `.env` file with your credentials:
   ```
   GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/your/credentials.json
   SPREADSHEET_ID=your_google_sheet_id_here
   SHEET_NAME=Sheet1
   ```

3. Get your Spreadsheet ID from the Google Sheets URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

## Usage

### Basic Example

```python
from google_sheets_client import GoogleSheetsClient
import pandas as pd

# Initialize client
client = GoogleSheetsClient()

# Read data
df = client.read_sheet(range_name='A1:E10', sheet_name='Sheet1')
print(df)

# Write data
data = pd.DataFrame({
    'Name': ['Alice', 'Bob'],
    'Age': [25, 30]
})
client.write_sheet(data, range_name='A1', sheet_name='Sheet1')

# Append data
new_row = [['Charlie', 35]]
client.append_sheet(new_row, sheet_name='Sheet1')
```

### Available Methods

- `read_sheet(range_name, sheet_name)` - Read data from sheet
- `write_sheet(data, range_name, sheet_name, clear_existing)` - Write data to sheet
- `append_sheet(data, sheet_name)` - Append data to sheet
- `clear_sheet(range_name, sheet_name)` - Clear sheet data
- `get_sheet_info()` - Get spreadsheet information

## Authentication

On first run, the script will open a browser window for OAuth authentication. After granting permissions, a `token.json` file will be created for future use.

## Error Handling

The client includes comprehensive error handling for common issues like:
- Missing credentials
- Invalid spreadsheet ID
- Network errors
- Authentication failures