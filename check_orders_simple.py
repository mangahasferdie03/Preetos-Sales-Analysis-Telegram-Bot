from google_sheets_client import GoogleSheetsClient

def main():
    try:
        print("Today's date: July 31, 2025")
        print()
        
        # Initialize the client
        client = GoogleSheetsClient()
        
        # Read ALL data from ORDER sheet
        print("Checking all orders where Column C (Order Date) and Column L have values...")
        result = client.read_sheet(range_name='A:Z', sheet_name='ORDER')
        
        if isinstance(result, dict) and 'headers' in result:
            print(f"Searching through {len(result['data'])} total records...")
            
            valid_orders_today = []
            all_valid_orders = []
            
            for i, row in enumerate(result['data']):
                # Column C is index 2 (Order Date)
                # Column L is index 11 (Customer Order)
                column_c = row[2] if len(row) > 2 and row[2] else ""
                column_l = row[11] if len(row) > 11 and row[11] else ""
                
                # Check if both columns have values
                if column_c.strip() and column_l.strip():
                    order_info = {
                        'row': i + 5,  # Actual row number in sheet
                        'order_date': column_c.strip(),
                        'customer_order': column_l.strip()[:100] + "..." if len(column_l.strip()) > 100 else column_l.strip(),
                        'customer_name': row[3] if len(row) > 3 else 'Unknown'
                    }
                    
                    all_valid_orders.append(order_info)
                    
                    # Check if it's today's date (July 31, 2025)
                    if "July 31, 2025" in column_c:
                        valid_orders_today.append(order_info)
            
            # Display results
            print(f"\n=== RESULTS ===")
            print(f"Total valid orders (Column C + Column L filled): {len(all_valid_orders)}")
            print(f"Orders for July 31, 2025: {len(valid_orders_today)}")
            
            if valid_orders_today:
                print(f"\nToday's orders (July 31, 2025):")
                for i, order in enumerate(valid_orders_today, 1):
                    print(f"{i}. Row {order['row']}: {order['customer_name']}")
                    print(f"   Date: {order['order_date']}")
                    print(f"   Order: {order['customer_order']}")
                    print()
            else:
                print("No orders found for July 31, 2025")
                
                # Show last 5 valid orders for reference
                if all_valid_orders:
                    print(f"\nLast 5 valid orders for reference:")
                    for order in all_valid_orders[-5:]:
                        print(f"- Row {order['row']}: {order['order_date']} - {order['customer_name']}")
                    
        else:
            print("Could not read order data")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()