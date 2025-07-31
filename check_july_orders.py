from google_sheets_client import GoogleSheetsClient

def main():
    try:
        print("Today's date: July 31, 2025")
        print()
        
        # Initialize the client
        client = GoogleSheetsClient()
        
        # Read ALL data from ORDER sheet
        print("Checking all 748+ orders for today's date...")
        result = client.read_sheet(range_name='A:Z', sheet_name='ORDER')
        
        if isinstance(result, dict) and 'headers' in result:
            headers = result['headers']
            
            # Find the "Order Date" column index
            try:
                date_column_idx = headers.index('Order Date')
                name_column_idx = headers.index('Name')
                sold_by_idx = headers.index('Sold By')
                status_idx = headers.index('Status')
            except ValueError as e:
                print(f"Could not find required column: {e}")
                return
            
            # Look for July 31, 2025 orders
            target_date = "July 31, 2025"
            todays_orders = []
            
            print(f"Searching through {len(result['data'])} total records...")
            
            for i, row in enumerate(result['data']):
                if len(row) > date_column_idx and row[date_column_idx]:
                    order_date = str(row[date_column_idx]).strip()
                    
                    # Check if the order date matches today
                    if target_date in order_date:
                        customer_name = row[name_column_idx] if len(row) > name_column_idx else 'Unknown'
                        sold_by = row[sold_by_idx] if len(row) > sold_by_idx else 'Unknown'
                        status = row[status_idx] if len(row) > status_idx else 'Unknown'
                        
                        todays_orders.append({
                            'row': i + 5,  # +5 because we skip first 3 rows + header row
                            'name': customer_name,
                            'sold_by': sold_by,
                            'status': status,
                            'date': order_date
                        })
            
            # Display results
            print(f"\n=== RESULTS FOR JULY 31, 2025 ===")
            print(f"Total orders today: {len(todays_orders)}")
            
            if todays_orders:
                print("\nToday's orders:")
                for i, order in enumerate(todays_orders, 1):
                    print(f"{i}. {order['name']} (Sold by: {order['sold_by']}, Status: {order['status']})")
            else:
                print("No orders found for July 31, 2025")
                
                # Show some recent dates for reference
                print("\nRecent order dates found (last 10):")
                recent_dates = []
                for row in result['data'][-10:]:
                    if len(row) > date_column_idx and row[date_column_idx]:
                        recent_dates.append(row[date_column_idx])
                
                for date in recent_dates:
                    print(f"- {date}")
                    
        else:
            print("Could not read order data")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()