from google_sheets_client import GoogleSheetsClient

def main():
    try:
        # Initialize the client
        client = GoogleSheetsClient()
        
        print("Testing full data access...")
        print()
        
        # Read ALL data from ORDER sheet (no row limit)
        print("=== Reading ALL data from ORDER sheet ===")
        result = client.read_sheet(range_name='A:Z', sheet_name='ORDER')  # Read all columns A-Z
        
        if isinstance(result, dict) and 'headers' in result:
            print("Headers:", result['headers'])
            print(f"Total data rows found: {len(result['data'])}")
            
            # Show first 5 rows (with safe encoding)
            print("\nFirst 5 data rows:")
            for i, row in enumerate(result['data'][:5]):
                safe_row = [str(cell).encode('ascii', 'ignore').decode('ascii') if cell else '' for cell in row]
                print(f"Row {i+1}: {safe_row}")
            
            # Show last 5 rows if there are more than 5
            if len(result['data']) > 5:
                print(f"\nLast 5 data rows:")
                for i, row in enumerate(result['data'][-5:]):
                    actual_row_num = len(result['data']) - 5 + i + 1
                    safe_row = [str(cell).encode('ascii', 'ignore').decode('ascii') if cell else '' for cell in row]
                    print(f"Row {actual_row_num}: {safe_row}")
                    
            print(f"\n📊 SUMMARY: Found {len(result['data'])} total order records")
        else:
            print("No properly formatted data found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()