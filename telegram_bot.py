import os
import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google_sheets_client import GoogleSheetsClient
import anthropic

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramGoogleSheetsBot:
    def __init__(self, telegram_token, anthropic_key, credentials_file, spreadsheet_id):
        self.telegram_token = telegram_token
        self.anthropic_key = anthropic_key
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.sheets_client = None
        self.anthropic_client = None
        
        # Initialize Google Sheets client
        try:
            # Check if we're on Railway (env vars) or local (file)
            if os.getenv('GOOGLE_PRIVATE_KEY'):
                # Railway environment - create credentials from env vars
                from google.oauth2 import service_account
                import json
                
                creds_data = {
                    "type": "service_account",
                    "project_id": "preetos-order-agent",
                    "private_key_id": "52ef2c399f9d49f7b6af42f061b10706419aeb89",
                    "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
                    "client_email": "preeetos-sheets-agent@preetos-order-agent.iam.gserviceaccount.com",
                    "client_id": "114633176250172838577",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/preeetos-sheets-agent%40preetos-order-agent.iam.gserviceaccount.com",
                    "universe_domain": "googleapis.com"
                }
                
                creds = service_account.Credentials.from_service_account_info(
                    creds_data, scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                
                # Create service directly
                from googleapiclient.discovery import build
                service = build('sheets', 'v4', credentials=creds)
                
                # Create a simple sheets client wrapper
                class SimpleGoogleSheetsClient:
                    def __init__(self, service, spreadsheet_id):
                        self.service = service
                        self.spreadsheet_id = spreadsheet_id
                    
                    def read_sheet(self, sheet_name, range_name=None):
                        try:
                            if range_name:
                                range_str = f"{sheet_name}!{range_name}"
                            else:
                                range_str = sheet_name
                            
                            result = self.service.spreadsheets().values().get(
                                spreadsheetId=self.spreadsheet_id, range=range_str
                            ).execute()
                            
                            values = result.get('values', [])
                            if not values:
                                return {'headers': [], 'data': []}
                            
                            headers = values[0] if values else []
                            data = values[1:] if len(values) > 1 else []
                            
                            return {'headers': headers, 'data': data}
                        except Exception as e:
                            logger.error(f"Error reading sheet: {e}")
                            return {'headers': [], 'data': []}
                
                self.sheets_client = SimpleGoogleSheetsClient(service, spreadsheet_id)
                logger.info("Google Sheets client initialized successfully (Railway)")
            else:
                # Local environment - use file
                self.sheets_client = GoogleSheetsClient(
                    credentials_file=credentials_file,
                    spreadsheet_id=spreadsheet_id
                )
                logger.info("Google Sheets client initialized successfully (Local)")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            print(f"Google Sheets init error: {e}")  # Also print to console
        
        # Initialize Anthropic client
        try:
            if not anthropic_key:
                raise ValueError("Anthropic API key is missing")
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
            logger.info("Anthropic client initialized successfully")
            print("Anthropic client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            print(f"Anthropic init error: {e}")  # Also print to console
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command"""
        welcome_message = """
Welcome to the Preetos.ai bot!

Available commands:
/sales_today - Get today's sales analysis with AI 
/sales_this_week - Get this week's sales analysis with AI 
        """
        await update.message.reply_text(welcome_message)
    
    async def list_sheets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /sheets command"""
        if not self.sheets_client:
            await update.message.reply_text("❌ Google Sheets connection not available")
            return
        
        try:
            sheet_info = self.sheets_client.get_sheet_info()
            if not sheet_info:
                await update.message.reply_text("❌ No sheets found")
                return
            
            message = "📊 Available Sheets:\n\n"
            for sheet in sheet_info:
                message += f"• {sheet['title']}\n"
            
            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Error listing sheets: {e}")
            await update.message.reply_text(f"❌ Error listing sheets: {str(e)}")
    
    async def read_sheet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /read command"""
        if not self.sheets_client:
            await update.message.reply_text("❌ Google Sheets connection not available")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please specify a sheet name. Example: /read ORDER")
            return
        
        sheet_name = ' '.join(context.args)
        
        try:
            data = self.sheets_client.read_sheet(sheet_name=sheet_name)
            
            if not data.get('headers') and not data.get('data'):
                await update.message.reply_text(f"❌ No data found in sheet '{sheet_name}'")
                return
            
            # Format response
            headers = data.get('headers', [])
            rows = data.get('data', [])
            
            message = f"📋 Data from '{sheet_name}':\n\n"
            
            if headers:
                message += "Headers: " + " | ".join(headers[:5]) + "\n\n"
            
            # Show first 5 rows
            for i, row in enumerate(rows[:5]):
                row_data = " | ".join([str(cell) for cell in row[:5]]) if row else "Empty row"
                message += f"Row {i+1}: {row_data}\n"
            
            if len(rows) > 5:
                message += f"\n... and {len(rows) - 5} more rows"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error reading sheet: {e}")
            await update.message.reply_text(f"❌ Error reading sheet '{sheet_name}': {str(e)}")
    
    async def write_sheet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /write command"""
        if not self.sheets_client:
            await update.message.reply_text("❌ Google Sheets connection not available")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ Please specify sheet name and data. Example: /write ORDER New order data")
            return
        
        sheet_name = context.args[0]
        data_text = ' '.join(context.args[1:])
        
        try:
            # Append the data as a new row
            data = [[data_text]]
            result = self.sheets_client.append_sheet(data, sheet_name=sheet_name)
            
            if result:
                await update.message.reply_text(f"✅ Data added to '{sheet_name}' successfully!")
            else:
                await update.message.reply_text(f"❌ Failed to add data to '{sheet_name}'")
                
        except Exception as e:
            logger.error(f"Error writing to sheet: {e}")
            await update.message.reply_text(f"❌ Error writing to sheet '{sheet_name}': {str(e)}")
    
    async def orders_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick access to ORDER sheet"""
        context.args = ['ORDER']
        await self.read_sheet_command(update, context)
    
    async def inventory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick access to INVENTORY sheet"""
        context.args = ['INVENTORY']
        await self.read_sheet_command(update, context)
    
    async def expenses_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick access to EXPENSES sheet"""
        context.args = ['EXPENSES']
        await self.read_sheet_command(update, context)
    
    async def sales_today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get today's sales analysis with AI insights"""
        if not self.sheets_client or not self.anthropic_client:
            # Debug which service is missing
            sheets_status = "✅" if self.sheets_client else "❌"
            anthropic_status = "✅" if self.anthropic_client else "❌"
            await update.message.reply_text(f"❌ Services not available\nSheets: {sheets_status} | Anthropic: {anthropic_status}")
            return
        
        try:
            await update.message.reply_text("📊 Analyzing today's sales data...")
            
            # Get today's date in multiple formats for debugging
            now = datetime.now()
            today_formats = [
                now.strftime('%B %d, %Y'),  # July 31, 2025 (matches your sheet format!)
                now.strftime('%m/%d/%Y'),  # 07/31/2025
                f"{now.month}/{now.day}/{now.year}",  # 7/31/2025
                now.strftime('%Y-%m-%d'),   # 2025-07-31
                now.strftime('%d/%m/%Y'),   # 31/07/2025
                f"{now.day}/{now.month}/{now.year}",  # 31/7/2025
            ]
            
            # Primary format for comparison
            today = today_formats[0]
            
            # Read ORDER sheet data with wider range to include Column AB (Price)
            data = self.sheets_client.read_sheet(sheet_name='ORDER', range_name='A:AF')
            
            if not data.get('headers') or not data.get('data'):
                await update.message.reply_text("❌ No order data found")
                return
            
            headers = data['headers']
            rows = data['data']
            
            
            # Find column indices
            try:
                date_col = headers.index('Order Date') if 'Order Date' in headers else 2  # Column C
                name_col = headers.index('Name') if 'Name' in headers else 3  # Column D
                payment_status_col = headers.index('Status Payment') if 'Status Payment' in headers else 7  # Column H
                delivery_status_col = headers.index('Status (Delivery)') if 'Status (Delivery)' in headers else 8  # Column I
                price_col = headers.index('Price') if 'Price' in headers else 27  # Column AB
                
                # Pouch columns (N, O, P, Q)
                p_chz_col = 13  # Column N
                p_sc_col = 14   # Column O
                p_bbq_col = 15  # Column P
                p_og_col = 16   # Column Q
                
                # Tub columns (T, U, V, W)
                t_chz_col = 19  # Column T
                t_sc_col = 20   # Column U
                t_bbq_col = 21  # Column V
                t_og_col = 22   # Column W
                
            except Exception as e:
                await update.message.reply_text(f"❌ Error finding columns: {str(e)}")
                return
            
            # Filter today's orders and calculate metrics
            today_orders = []
            total_revenue = 0
            customers = set()
            pouches = {'Cheese': 0, 'Sour Cream': 0, 'BBQ': 0, 'Original': 0}
            tubs = {'Cheese': 0, 'Sour Cream': 0, 'BBQ': 0, 'Original': 0}
            paid_customers = []
            unpaid_customers = []
            undelivered_orders = []
            
            # DEBUG: Track date matching
            debug_matches = []
            
            for row in rows:
                # Check if this is a valid order: Column C (date), D (name), or L (summary) has value
                if len(row) <= 11:  # Need at least 12 columns to check Column L
                    continue
                
                # Valid order if ANY of these have values: C, D, or L
                has_date = len(row) > 2 and str(row[2]).strip()
                has_name = len(row) > 3 and str(row[3]).strip()
                has_summary = len(row) > 11 and str(row[11]).strip()
                
                if not (has_date or has_name or has_summary):
                    continue  # Skip if none of the key fields have values
                
                # Check if order is from today using multiple date formats
                order_date = row[date_col] if date_col < len(row) else ''
                order_date_str = str(order_date).strip()
                
                # Try exact matching first, then substring matching
                is_today = False
                for today_format in today_formats:
                    # Try exact match
                    if order_date_str == today_format:
                        is_today = True
                        break
                    # Try substring match (for partial matches)
                    if today_format in order_date_str or order_date_str in today_format:
                        is_today = True
                        break
                
                # Add validation info to debug
                validation_info = f"Date:{has_date} Name:{has_name} Summary:{has_summary}"
                debug_matches.append(f"Row: {validation_info} | Date:'{order_date_str}' -> {'MATCH' if is_today else 'NO MATCH'}")
                
                if is_today:
                    today_orders.append(row)
                    
                    # Customer name (use "Unknown Customer" if missing)
                    customer_name = str(row[name_col]).strip() if name_col < len(row) and row[name_col] else 'Unknown Customer'
                    customers.add(customer_name)
                    
                    # Revenue (handle missing price gracefully)
                    try:
                        price_value = row[price_col] if price_col < len(row) and row[price_col] else 0
                        if price_value:
                            # Extract numeric value, removing currency symbols and commas
                            import re
                            price_str = str(price_value)
                            # Find all numeric parts (digits, dots, commas)
                            numeric_parts = re.findall(r'[0-9.,]+', price_str)
                            if numeric_parts:
                                # Take the first numeric part and clean it
                                clean_price = numeric_parts[0].replace(',', '')
                                price = float(clean_price)
                                total_revenue += price
                    except (ValueError, IndexError, AttributeError):
                        # Price not available or invalid, count as 0
                        pass
                    
                    # Pouches (handle missing data gracefully)
                    try:
                        pouches['Cheese'] += int(row[p_chz_col]) if p_chz_col < len(row) and str(row[p_chz_col]).strip().isdigit() else 0
                        pouches['Sour Cream'] += int(row[p_sc_col]) if p_sc_col < len(row) and str(row[p_sc_col]).strip().isdigit() else 0
                        pouches['BBQ'] += int(row[p_bbq_col]) if p_bbq_col < len(row) and str(row[p_bbq_col]).strip().isdigit() else 0
                        pouches['Original'] += int(row[p_og_col]) if p_og_col < len(row) and str(row[p_og_col]).strip().isdigit() else 0
                    except (ValueError, IndexError):
                        pass
                    
                    # Tubs (handle missing data gracefully)
                    try:
                        tubs['Cheese'] += int(row[t_chz_col]) if t_chz_col < len(row) and str(row[t_chz_col]).strip().isdigit() else 0
                        tubs['Sour Cream'] += int(row[t_sc_col]) if t_sc_col < len(row) and str(row[t_sc_col]).strip().isdigit() else 0
                        tubs['BBQ'] += int(row[t_bbq_col]) if t_bbq_col < len(row) and str(row[t_bbq_col]).strip().isdigit() else 0
                        tubs['Original'] += int(row[t_og_col]) if t_og_col < len(row) and str(row[t_og_col]).strip().isdigit() else 0
                    except (ValueError, IndexError):
                        pass
                    
                    # Payment status (default to unpaid if missing)
                    payment_status = str(row[payment_status_col]).strip() if payment_status_col < len(row) and row[payment_status_col] else 'Unpaid'
                    if 'Paid' in payment_status:
                        paid_customers.append(customer_name)
                    else:
                        unpaid_customers.append(customer_name)
                    
                    # Delivery status (only "Delivered" counts as delivered, everything else is undelivered)
                    delivery_status = str(row[delivery_status_col]).strip() if delivery_status_col < len(row) and row[delivery_status_col] else 'Pending'
                    if delivery_status != 'Delivered':
                        undelivered_orders.append(customer_name)
            
            # Prepare structured data for AI analysis
            sales_data = {
                "date": today,
                "revenue": total_revenue,
                "customer_count": len(customers),
                "pouches_sold": pouches,
                "tubs_sold": tubs,
                "payment_status": {
                    "paid": len(paid_customers),
                    "unpaid": len(unpaid_customers),
                    "paid_customers": paid_customers,
                    "unpaid_customers": unpaid_customers
                },
                "delivery_status": {
                    "undelivered_count": len(undelivered_orders),
                    "undelivered_customers": undelivered_orders
                }
            }
            
            
            # Calculate totals
            total_pouches = sum(pouches.values())
            total_tubs = sum(tubs.values())
            
            # Format customer names with numbers
            customer_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(sorted(customers))]) if customers else "None"
            
            # Format names with vertical enumeration
            def format_numbered_names(names):
                if not names:
                    return "None"
                
                sorted_names = sorted(names)
                # Create shortened names with numbers, each on its own line
                numbered_names = [f"{i+1}. {name.split()[0]} {name.split()[-1][0]}." for i, name in enumerate(sorted_names)]
                
                return "\n".join(numbered_names)
                
            paid_formatted = format_numbered_names(paid_customers)
            unpaid_formatted = format_numbered_names(unpaid_customers)
            undelivered_formatted = format_numbered_names(undelivered_orders)
            
            # Format date
            date_formatted = now.strftime('%b %d, %Y')
            
            # Get AI insights
            structured_summary = f"""📊 Sales Report for {date_formatted}

💰 Revenue: ₱{total_revenue:,.0f} | 👥 {len(customers)} Customers
{customer_list}

✏️ Order:
Pouches ({total_pouches})
Cheese {pouches['Cheese']} | Sour Cream {pouches['Sour Cream']} | BBQ {pouches['BBQ']} | Original {pouches['Original']}
Tubs ({total_tubs})
Cheese {tubs['Cheese']} | Sour Cream {tubs['Sour Cream']} | BBQ {tubs['BBQ']} | Original {tubs['Original']}

💳 Payment:
Paid ({len(paid_customers)}):
{paid_formatted}
Unpaid ({len(unpaid_customers)}):
{unpaid_formatted}

🚚 Delivery:
Undelivered ({len(undelivered_orders)}):
{undelivered_formatted}
            """
            
            # Get AI insights
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=200,
                    messages=[{
                        "role": "user",
                        "content": f"Give me a brief, conversational summary of today's sales performance. Keep it concise and friendly - no recommendations needed:\n\n{structured_summary}"
                    }]
                )
                ai_insights = response.content[0].text
            except Exception as e:
                ai_insights = f"AI analysis unavailable: {str(e)}"
            
            # Create final message with Claude Insights at the top
            final_message = f"""📊 Sales Report for {date_formatted if 'date_formatted' in locals() else week_start + ' - ' + week_end}

🎇 Claude Insights:
{ai_insights}

💰 Revenue: ₱{total_revenue:,.0f} | 👥 {len(customers)} Customers
{customer_list}

✏️ Order:
Pouches ({total_pouches})
Cheese {pouches['Cheese']} | Sour Cream {pouches['Sour Cream']} | BBQ {pouches['BBQ']} | Original {pouches['Original']}
Tubs ({total_tubs})
Cheese {tubs['Cheese']} | Sour Cream {tubs['Sour Cream']} | BBQ {tubs['BBQ']} | Original {tubs['Original']}

💳 Payment:
Paid ({len(paid_customers)}):
{paid_formatted}
Unpaid ({len(unpaid_customers)}):
{unpaid_formatted}

🚚 Delivery:
Undelivered ({len(undelivered_orders)}):
{undelivered_formatted}
"""
            
            # Send response
            if len(final_message) > 4000:
                # Split into header + insights first, then details
                header_insights = f"""📊 Sales Report for {date_formatted if 'date_formatted' in locals() else week_start + ' - ' + week_end}

🎇 Claude Insights:
{ai_insights}"""
                
                details = f"""💰 Revenue: ₱{total_revenue:,.0f} | 👥 {len(customers)} Customers
{customer_list}

✏️ Order:
Pouches ({total_pouches})
Cheese {pouches['Cheese']} | Sour Cream {pouches['Sour Cream']} | BBQ {pouches['BBQ']} | Original {pouches['Original']}
Tubs ({total_tubs})
Cheese {tubs['Cheese']} | Sour Cream {tubs['Sour Cream']} | BBQ {tubs['BBQ']} | Original {tubs['Original']}

💳 Payment:
Paid ({len(paid_customers)}):
{paid_formatted}
Unpaid ({len(unpaid_customers)}):
{unpaid_formatted}

🚚 Delivery:
Undelivered ({len(undelivered_orders)}):
{undelivered_formatted}"""
                
                await update.message.reply_text(header_insights)
                await update.message.reply_text(details)
            else:
                await update.message.reply_text(final_message)
                
        except Exception as e:
            logger.error(f"Error in sales_today_command: {e}")
            await update.message.reply_text(f"❌ Error analyzing sales data: {str(e)}")
    
    async def sales_this_week_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get this week's sales analysis with AI insights"""
        if not self.sheets_client or not self.anthropic_client:
            await update.message.reply_text("❌ Services not available")
            return
        
        try:
            await update.message.reply_text("📊 Analyzing this week's sales data...")
            
            # Get this week's date range (Sunday to Saturday)
            now = datetime.now()
            # Get Sunday of this week (Sunday = 6 in weekday(), so we need to adjust)
            days_since_sunday = (now.weekday() + 1) % 7  # Convert Monday=0 to Sunday=0
            sunday = now - timedelta(days=days_since_sunday)
            # Generate this week's date formats
            week_dates = []
            for i in range(7):  # Sunday to Saturday
                day = sunday + timedelta(days=i)
                week_dates.extend([
                    day.strftime('%B %d, %Y'),  # July 31, 2025 (text format)
                    day.strftime('%m/%d/%Y'),   # 07/31/2025 (numeric format)
                    f"{day.month}/{day.day}/{day.year}",  # 7/31/2025
                    day.strftime('%Y-%m-%d'),   # 2025-07-31
                ])
            
            # Read ORDER sheet data with wider range to include Column AB (Price)
            data = self.sheets_client.read_sheet(sheet_name='ORDER', range_name='A:AF')
            
            if not data.get('headers') or not data.get('data'):
                await update.message.reply_text("❌ No order data found")
                return
            
            headers = data['headers']
            rows = data['data']
            
            # Find column indices
            try:
                date_col = headers.index('Order Date') if 'Order Date' in headers else 2  # Column C
                name_col = headers.index('Name') if 'Name' in headers else 3  # Column D
                payment_status_col = headers.index('Status Payment') if 'Status Payment' in headers else 7  # Column H
                delivery_status_col = headers.index('Status (Delivery)') if 'Status (Delivery)' in headers else 8  # Column I
                price_col = headers.index('Price') if 'Price' in headers else 27  # Column AB
                
                # Pouch columns (N, O, P, Q)
                p_chz_col = 13  # Column N
                p_sc_col = 14   # Column O
                p_bbq_col = 15  # Column P
                p_og_col = 16   # Column Q
                
                # Tub columns (T, U, V, W)
                t_chz_col = 19  # Column T
                t_sc_col = 20   # Column U
                t_bbq_col = 21  # Column V
                t_og_col = 22   # Column W
                
            except Exception as e:
                await update.message.reply_text(f"❌ Error finding columns: {str(e)}")
                return
            
            # Filter this week's orders and calculate metrics
            week_orders = []
            total_revenue = 0
            customers = set()
            pouches = {'Cheese': 0, 'Sour Cream': 0, 'BBQ': 0, 'Original': 0}
            tubs = {'Cheese': 0, 'Sour Cream': 0, 'BBQ': 0, 'Original': 0}
            paid_customers = []
            unpaid_customers = []
            undelivered_orders = []
            
            for row in rows:
                # Check if this is a valid order: Column C (date), D (name), or L (summary) has value
                if len(row) <= 11:  # Need at least 12 columns to check Column L
                    continue
                
                # Valid order if ANY of these have values: C, D, or L
                has_date = len(row) > 2 and str(row[2]).strip()
                has_name = len(row) > 3 and str(row[3]).strip()
                has_summary = len(row) > 11 and str(row[11]).strip()
                
                if not (has_date or has_name or has_summary):
                    continue  # Skip if none of the key fields have values
                
                # Check if order is from this week
                order_date = row[date_col] if date_col < len(row) else ''
                order_date_str = str(order_date).strip()
                
                # Try exact matching first, then substring matching
                is_this_week = False
                for week_date in week_dates:
                    # Try exact match
                    if order_date_str == week_date:
                        is_this_week = True
                        break
                    # Try substring match (for partial matches)
                    if week_date in order_date_str or order_date_str in week_date:
                        is_this_week = True
                        break
                
                if is_this_week:
                    week_orders.append(row)
                    
                    # Customer name (use "Unknown Customer" if missing)
                    customer_name = str(row[name_col]).strip() if name_col < len(row) and row[name_col] else 'Unknown Customer'
                    customers.add(customer_name)
                    
                    # Revenue (handle missing price gracefully)
                    try:
                        if price_col < len(row) and row[price_col]:
                            price_value = row[price_col]
                            # Extract numeric value, removing currency symbols and commas
                            import re
                            price_str = str(price_value)
                            # Find all numeric parts (digits, dots, commas)
                            numeric_parts = re.findall(r'[0-9.,]+', price_str)
                            if numeric_parts:
                                # Take the first numeric part and clean it
                                clean_price = numeric_parts[0].replace(',', '')
                                price = float(clean_price)
                                total_revenue += price
                    except (ValueError, IndexError, AttributeError):
                        # Price not available or invalid, count as 0
                        pass
                    
                    # Pouches (handle missing data gracefully)
                    try:
                        pouches['Cheese'] += int(row[p_chz_col]) if p_chz_col < len(row) and str(row[p_chz_col]).strip().isdigit() else 0
                        pouches['Sour Cream'] += int(row[p_sc_col]) if p_sc_col < len(row) and str(row[p_sc_col]).strip().isdigit() else 0
                        pouches['BBQ'] += int(row[p_bbq_col]) if p_bbq_col < len(row) and str(row[p_bbq_col]).strip().isdigit() else 0
                        pouches['Original'] += int(row[p_og_col]) if p_og_col < len(row) and str(row[p_og_col]).strip().isdigit() else 0
                    except (ValueError, IndexError):
                        pass
                    
                    # Tubs (handle missing data gracefully)
                    try:
                        tubs['Cheese'] += int(row[t_chz_col]) if t_chz_col < len(row) and str(row[t_chz_col]).strip().isdigit() else 0
                        tubs['Sour Cream'] += int(row[t_sc_col]) if t_sc_col < len(row) and str(row[t_sc_col]).strip().isdigit() else 0
                        tubs['BBQ'] += int(row[t_bbq_col]) if t_bbq_col < len(row) and str(row[t_bbq_col]).strip().isdigit() else 0
                        tubs['Original'] += int(row[t_og_col]) if t_og_col < len(row) and str(row[t_og_col]).strip().isdigit() else 0
                    except (ValueError, IndexError):
                        pass
                    
                    # Payment status (default to unpaid if missing)
                    payment_status = str(row[payment_status_col]).strip() if payment_status_col < len(row) and row[payment_status_col] else 'Unpaid'
                    if 'Paid' in payment_status:
                        paid_customers.append(customer_name)
                    else:
                        unpaid_customers.append(customer_name)
                    
                    # Delivery status (only "Delivered" counts as delivered, everything else is undelivered)
                    delivery_status = str(row[delivery_status_col]).strip() if delivery_status_col < len(row) and row[delivery_status_col] else 'Pending'
                    if delivery_status != 'Delivered':
                        undelivered_orders.append(customer_name)
            
            # Calculate totals
            total_pouches = sum(pouches.values())
            total_tubs = sum(tubs.values())
            
            # Format customer names with numbers
            customer_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(sorted(customers))]) if customers else "None"
            
            # Format names with vertical enumeration
            def format_numbered_names(names):
                if not names:
                    return "None"
                
                sorted_names = sorted(names)
                # Create shortened names with numbers, each on its own line
                numbered_names = [f"{i+1}. {name.split()[0]} {name.split()[-1][0]}." for i, name in enumerate(sorted_names)]
                
                return "\n".join(numbered_names)
                
            paid_formatted = format_numbered_names(paid_customers)
            unpaid_formatted = format_numbered_names(unpaid_customers)
            undelivered_formatted = format_numbered_names(undelivered_orders)
            
            # Format week range
            week_start = sunday.strftime('%b %d')
            week_end = (sunday + timedelta(days=6)).strftime('%b %d, %Y')
            
            # Get AI insights  
            structured_summary = f"""📊 Sales Report for {week_start} - {week_end}

Revenue: ₱{total_revenue:,.0f} | 👥 {len(customers)} Customers
{customer_list}

Order:
Pouches ({total_pouches})
Cheese {pouches['Cheese']} | Sour Cream {pouches['Sour Cream']} | BBQ {pouches['BBQ']} | Original {pouches['Original']}
Tubs ({total_tubs})
Cheese {tubs['Cheese']} | Sour Cream {tubs['Sour Cream']} | BBQ {tubs['BBQ']} | Original {tubs['Original']}

Status:
Paid ({len(paid_customers)}): {paid_formatted}
Unpaid ({len(unpaid_customers)}): {unpaid_formatted}
Undelivered ({len(undelivered_orders)}): {undelivered_formatted}
            """
            
            # Get AI insights
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=200,
                    messages=[{
                        "role": "user",
                        "content": f"Give me a brief, conversational summary of this week's sales performance. Keep it concise and friendly - no recommendations needed:\n\n{structured_summary}"
                    }]
                )
                ai_insights = response.content[0].text
            except Exception as e:
                ai_insights = f"AI analysis unavailable: {str(e)}"
            
            # Create final message with Claude Insights at the top
            final_message = f"""📊 Sales Report for {date_formatted if 'date_formatted' in locals() else week_start + ' - ' + week_end}

🎇 Claude Insights:
{ai_insights}

💰 Revenue: ₱{total_revenue:,.0f} | 👥 {len(customers)} Customers
{customer_list}

✏️ Order:
Pouches ({total_pouches})
Cheese {pouches['Cheese']} | Sour Cream {pouches['Sour Cream']} | BBQ {pouches['BBQ']} | Original {pouches['Original']}
Tubs ({total_tubs})
Cheese {tubs['Cheese']} | Sour Cream {tubs['Sour Cream']} | BBQ {tubs['BBQ']} | Original {tubs['Original']}

💳 Payment:
Paid ({len(paid_customers)}):
{paid_formatted}
Unpaid ({len(unpaid_customers)}):
{unpaid_formatted}

🚚 Delivery:
Undelivered ({len(undelivered_orders)}):
{undelivered_formatted}
"""
            
            # Send response
            if len(final_message) > 4000:
                # Split into header + insights first, then details
                header_insights = f"""📊 Sales Report for {date_formatted if 'date_formatted' in locals() else week_start + ' - ' + week_end}

🎇 Claude Insights:
{ai_insights}"""
                
                details = f"""💰 Revenue: ₱{total_revenue:,.0f} | 👥 {len(customers)} Customers
{customer_list}

✏️ Order:
Pouches ({total_pouches})
Cheese {pouches['Cheese']} | Sour Cream {pouches['Sour Cream']} | BBQ {pouches['BBQ']} | Original {pouches['Original']}
Tubs ({total_tubs})
Cheese {tubs['Cheese']} | Sour Cream {tubs['Sour Cream']} | BBQ {tubs['BBQ']} | Original {tubs['Original']}

💳 Payment:
Paid ({len(paid_customers)}):
{paid_formatted}
Unpaid ({len(unpaid_customers)}):
{unpaid_formatted}

🚚 Delivery:
Undelivered ({len(undelivered_orders)}):
{undelivered_formatted}"""
                
                await update.message.reply_text(header_insights)
                await update.message.reply_text(details)
            else:
                await update.message.reply_text(final_message)
                
        except Exception as e:
            logger.error(f"Error in sales_this_week_command: {e}")
            await update.message.reply_text(f"❌ Error analyzing weekly sales data: {str(e)}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user_message = update.message.text
        
        # Simple responses for common queries
        if "help" in user_message.lower():
            await self.start_command(update, context)
        elif "sheet" in user_message.lower():
            await self.list_sheets_command(update, context)
        else:
            await update.message.reply_text(
                "💡 Use /start to see available commands or type 'help' for assistance."
            )
    
    def run(self):
        """Start the bot"""
        try:
            # Create application
            application = Application.builder().token(self.telegram_token).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("sheets", self.list_sheets_command))
            application.add_handler(CommandHandler("read", self.read_sheet_command))
            application.add_handler(CommandHandler("write", self.write_sheet_command))
            application.add_handler(CommandHandler("orders", self.orders_command))
            application.add_handler(CommandHandler("inventory", self.inventory_command))
            application.add_handler(CommandHandler("expenses", self.expenses_command))
            application.add_handler(CommandHandler("sales_today", self.sales_today_command))
            application.add_handler(CommandHandler("sales_this_week", self.sales_this_week_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            logger.info("Bot started successfully")
            print("Telegram bot is running...")
            
            # Run the bot
            application.run_polling()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            print(f"Error starting bot: {e}")

def main():
    # Read configuration from environment variables or secret key file
    try:
        # Try environment variables first (for Railway)
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Fall back to secret key file (for local development)
        if not telegram_token or not anthropic_key:
            try:
                with open('secret key.txt', 'r') as f:
                    lines = f.readlines()
                    
                    for line in lines:
                        if 'telegram bot:' in line.lower() and not telegram_token:
                            telegram_token = line.split(':', 1)[1].strip()
                        elif 'anthropic key:' in line.lower() and not anthropic_key:
                            anthropic_key = line.split(':', 1)[1].strip()
            except FileNotFoundError:
                pass  # File doesn't exist in production
        
        if not telegram_token:
            raise ValueError("Telegram bot token not found in environment variables or secret key.txt")
        if not anthropic_key:
            raise ValueError("Anthropic API key not found in environment variables or secret key.txt")
        
        # Debug environment variables (without showing full values)
        print(f"Environment check:")
        print(f"TELEGRAM_BOT_TOKEN: {'✅' if telegram_token else '❌'}")
        print(f"ANTHROPIC_API_KEY: {'✅' if anthropic_key else '❌'}")
        print(f"GOOGLE_PRIVATE_KEY: {'✅' if os.getenv('GOOGLE_PRIVATE_KEY') else '❌'}")
        print(f"SPREADSHEET_ID: {os.getenv('SPREADSHEET_ID', 'using default')}")
        
        # Set up configuration
        credentials_file = 'credentials.json'
        spreadsheet_id = os.getenv('SPREADSHEET_ID', '1tKwSPYYPOzJxVhSfP4GBhHuqBSGVJUpJGDM6_b0zAmI')
        
        # Create and run bot
        bot = TelegramGoogleSheetsBot(
            telegram_token=telegram_token,
            anthropic_key=anthropic_key,
            credentials_file=credentials_file,
            spreadsheet_id=spreadsheet_id
        )
        
        bot.run()
        
    except Exception as e:
        print(f"Error starting bot: {e}")
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    main()