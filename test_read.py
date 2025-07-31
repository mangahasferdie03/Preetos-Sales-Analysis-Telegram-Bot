from google_sheets_client import GoogleSheetsClient

def main():
    try:
        # Initialize the client
        client = GoogleSheetsClient()
        
        print("Connected to Google Sheets!")
        print()
        
        # Read data from ORDER sheet (with header skipping)
        print("=== Reading from ORDER sheet (Clean Format) ===")
        result = client.read_sheet(range_name='A1:E10', sheet_name='ORDER')
        
        if isinstance(result, dict) and 'headers' in result:
            print("Headers:", result['headers'])
            print(f"Found {len(result['data'])} data rows:")
            for i, row in enumerate(result['data']):
                print(f"Data row {i+1}: {row}")
        else:
            print("No properly formatted data found")
            
        print("\n=== Raw Data (for comparison) ===")
        raw_data = client.read_sheet(range_name='A1:E10', sheet_name='ORDER', skip_header_rows=False)
        if raw_data:
            print(f"Raw data has {len(raw_data)} total rows:")
            for i, row in enumerate(raw_data):
                print(f"Raw row {i+1}: {row}")
        else:
            print("No raw data found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()