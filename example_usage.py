from google_sheets_client import GoogleSheetsClient

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

def main():
    # Initialize the Google Sheets client
    # Make sure to set up your .env file with the credentials path and spreadsheet ID
    try:
        client = GoogleSheetsClient()

        # Get sheet information
        print("=== Sheet Information ===")
        sheet_info = client.get_sheet_info()
        for sheet in sheet_info:
            print(f"Sheet: {sheet['title']} (ID: {sheet['sheet_id']})")
        print()

        # Example 1: Read data from ORDER sheet
        print("=== Reading Data from ORDER sheet ===")
        data = client.read_sheet(range_name='A1:E10', sheet_name='ORDER')
        print("Data from ORDER sheet:")
        if PANDAS_AVAILABLE and hasattr(data, 'head'):
            print(data.head())
        else:
            for i, row in enumerate(data[:5] if data else []):  # Show first 5 rows
                print(f"Row {i+1}: {row}")
        print()

        # Example 2: Write sample data to sheet
        print("=== Writing Sample Data ===")
        if PANDAS_AVAILABLE:
            sample_data = pd.DataFrame({
                'Name': ['Alice', 'Bob', 'Charlie'],
                'Age': [25, 30, 35],
                'City': ['New York', 'London', 'Tokyo'],
                'Score': [85.5, 92.3, 78.9]
            })
        else:
            sample_data = [
                ['Name', 'Age', 'City', 'Score'],
                ['Alice', 25, 'New York', 85.5],
                ['Bob', 30, 'London', 92.3],
                ['Charlie', 35, 'Tokyo', 78.9]
            ]

        result = client.write_sheet(
            data=sample_data,
            range_name='G1',
            sheet_name='ORDER'
        )
        print("Sample data written successfully!")
        print()

        # Example 3: Append data to sheet
        print("=== Appending Data ===")
        new_row = [['David', 28, 'Berlin', 88.7]]
        client.append_sheet(data=new_row, sheet_name='ORDER')
        print("New row appended!")
        print()

        # Example 4: Read the updated data
        print("=== Reading Updated Data ===")
        updated_data = client.read_sheet(range_name='G:J', sheet_name='ORDER')
        print("Updated data:")
        if PANDAS_AVAILABLE and hasattr(updated_data, 'head'):
            print(updated_data)
        else:
            for i, row in enumerate(updated_data):
                print(f"Row {i+1}: {row}")

    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease make sure to:")
        print("1. Create a .env file based on .env.example")
        print("2. Add your Google Sheets credentials file path")
        print("3. Add your spreadsheet ID")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
