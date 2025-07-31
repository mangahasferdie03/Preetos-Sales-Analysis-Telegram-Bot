from google_sheets_client import GoogleSheetsClient

def main():
    try:
        # Initialize the client
        client = GoogleSheetsClient()
        
        print("[SUCCESS] Connected to Google Sheets!")
        print()
        
        # Get sheet information
        print("=== Available Sheets ===")
        sheet_info = client.get_sheet_info()
        for sheet in sheet_info:
            print(f"- {sheet['title']}")
        print()
        
        # Read data from ORDER sheet
        print("=== Reading from ORDER sheet ===")
        data = client.read_sheet(range_name='A1:E5', sheet_name='ORDER')
        
        if data:
            print("First 5 rows from ORDER sheet:")
            for i, row in enumerate(data):
                print(f"Row {i+1}: {row}")
        else:
            print("No data found in ORDER sheet")
        print()
        
        # Test writing data
        print("=== Writing Test Data ===")
        test_data = [
            ['Test Name', 'Test Value', 'Timestamp'],
            ['Claude Test', 'Connection Success', '2025-01-31']
        ]
        
        result = client.write_sheet(
            data=test_data, 
            range_name='Z1', 
            sheet_name='ORDER'
        )
        
        if result:
            print("[SUCCESS] Wrote test data to ORDER sheet (column Z)")
        else:
            print("[ERROR] Failed to write data")
            
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()