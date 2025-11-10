# Scheduled Reports Setup Guide

## Overview

The bot now supports **automated daily sales reports** sent at **3 PM and 11 PM** to a specified Telegram chat.

## Features

- **Automatic Reports**: Sales reports are sent automatically twice daily
- **Timezone Support**: Configure your local timezone for accurate scheduling
- **Flexible Chat Targets**: Send reports to any chat (personal, group, or channel)

## Setup Instructions

### Step 1: Get Your Chat ID

You need to find the Telegram Chat ID where you want to receive the reports.

#### Option A: Personal Chat (Direct Messages)

1. Message your bot on Telegram
2. Run the bot and check the logs
3. Send any message to the bot
4. Look in the console logs for a line like: `Update from chat_id: 123456789`
5. That's your Chat ID!

#### Option B: Use @userinfobot

1. Search for `@userinfobot` on Telegram
2. Start a chat with it
3. It will reply with your Chat ID

#### Option C: Group or Channel

1. Add your bot to the group/channel
2. Send a message in the group
3. Check the bot logs for the chat ID
4. For channels, the ID will be negative (e.g., `-1001234567890`)

### Step 2: Configure Environment Variables

Add these to your `.env` file:

```env
# Required: Your Telegram Chat ID
REPORT_CHAT_ID=123456789

# Optional: Timezone (default is Asia/Manila)
TIMEZONE=Asia/Manila
```

### Step 3: Restart the Bot

```bash
python telegram_bot.py
```

You should see:
```
Telegram bot is running...
📅 Scheduled reports enabled at 3 PM and 11 PM
Scheduler started - Reports will be sent at 3 PM and 11 PM (Asia/Manila)
```

## Timezone Configuration

### Common Timezones

```
Asia/Manila       # Philippines (UTC+8)
America/New_York  # US Eastern Time
America/Chicago   # US Central Time
America/Los_Angeles # US Pacific Time
Europe/London     # UK
Europe/Paris      # Central European Time
Asia/Tokyo        # Japan (UTC+9)
Asia/Singapore    # Singapore (UTC+8)
Australia/Sydney  # Australia Eastern
```

### Find Your Timezone

Visit: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

Look for your timezone in the "TZ database name" column.

## How It Works

1. **Scheduler Setup**: When the bot starts, it creates two scheduled jobs
2. **Daily Execution**: At 3 PM and 11 PM (in your configured timezone)
3. **Report Generation**: The bot automatically runs the "Today" analysis
4. **Message Delivery**: Sends the formatted report to your specified chat

## Report Format

The automated report includes:

```
📊 **Automated Sales Report** - December 10, 2024

💰 Total Revenue: ₱15,000.00
   • Paid: ₱12,000.00
   • Unpaid: ₱3,000.00

👥 Customers: 25

📦 Products Sold:
   Pouches:
   • Cheese: 10
   • Sour Cream: 8
   • BBQ: 5
   • Original: 12

   Tubs:
   • Cheese: 3
   • Sour Cream: 2

📈 Performance Metrics:
   • 7-day average: ₱12,500/day
   • 30-day average: ₱11,800/day
   • Target streak: 5 days

[AI-generated insights from Claude]
```

## Testing

### Test Immediately

You can modify the schedule temporarily to test. Add a job that runs in 1 minute:

```python
# In telegram_bot.py, add this to setup_scheduler():
from datetime import datetime
test_time = datetime.now() + timedelta(minutes=1)

scheduler.add_job(
    self.send_scheduled_sales_report,
    trigger='date',
    run_date=test_time,
    args=[application],
    id='test_report'
)
```

### Check Logs

The bot logs all scheduled activities:

```
INFO - Scheduler started - Reports will be sent at 3 PM and 11 PM (Asia/Manila)
INFO - Sending scheduled sales report to chat 123456789
INFO - Scheduled sales report sent successfully
```

## Troubleshooting

### Reports Not Sending

1. **Check REPORT_CHAT_ID**: Make sure it's set in your `.env` file
2. **Verify Bot Permissions**: Bot must be able to send messages to the chat
3. **Check Logs**: Look for error messages in the console
4. **Timezone Issues**: Verify your timezone is correct

### Wrong Time

1. **Timezone Mismatch**: Double-check your `TIMEZONE` setting
2. **Server Time**: If deployed, ensure server timezone matches expectations

### Bot Not in Group

If sending to a group/channel:
1. Add the bot as a member
2. For channels, make the bot an admin

## Production Deployment (Railway)

Add these environment variables in Railway:

```
REPORT_CHAT_ID=your_chat_id
TIMEZONE=Asia/Manila
```

Railway will use the existing `TELEGRAM_BOT_TOKEN` and other credentials.

## Customization

### Change Schedule Times

Edit the `setup_scheduler()` method in [telegram_bot.py](telegram_bot.py:2752):

```python
# Change from 3 PM to 9 AM
scheduler.add_job(
    self.send_scheduled_sales_report,
    trigger=CronTrigger(hour=9, minute=0, timezone=timezone),  # Changed from 15 to 9
    ...
)
```

### Add More Schedules

Add additional jobs:

```python
# Add a noon report
scheduler.add_job(
    self.send_scheduled_sales_report,
    trigger=CronTrigger(hour=12, minute=0, timezone=timezone),
    args=[application],
    id='sales_report_noon',
    name='Daily Sales Report at Noon',
    replace_existing=True
)
```

### Send to Multiple Chats

Modify `send_scheduled_sales_report()` to loop through multiple chat IDs:

```python
chat_ids = os.getenv('REPORT_CHAT_IDS', '').split(',')
for chat_id in chat_ids:
    if chat_id.strip():
        await application.bot.send_message(...)
```

Then in `.env`:
```env
REPORT_CHAT_IDS=123456789,987654321,555555555
```

## Advanced: Cron Expressions

You can use more complex schedules:

```python
# Every weekday at 5 PM
CronTrigger(day_of_week='mon-fri', hour=17, minute=0)

# First day of each month at 9 AM
CronTrigger(day=1, hour=9, minute=0)

# Every 6 hours
CronTrigger(hour='*/6', minute=0)
```

## Support

If you encounter issues:
1. Check the bot logs for error messages
2. Verify all environment variables are set correctly
3. Ensure the bot has necessary permissions
4. Test with a simple personal chat first before using groups/channels

Happy automating! 🤖
