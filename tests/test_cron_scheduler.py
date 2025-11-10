"""
Comprehensive Test Suite for Cron Job Scheduling Feature

This test suite validates the scheduled report functionality that sends
automated sales reports at 3 PM and 11 PM daily.

Test Coverage:
- Cron job configuration correctness
- Schedule timing verification (3 PM and 11 PM)
- Timezone handling
- Scheduler initialization
- Job registration and execution
- Error handling and edge cases
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
from datetime import datetime, time
import pytz
import os
import sys

# Add parent directory to path to import telegram_bot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import TelegramGoogleSheetsBot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class TestCronSchedulerConfiguration(unittest.TestCase):
    """Test the cron scheduler configuration and setup"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token_12345',
            'ANTHROPIC_API_KEY': 'test_anthropic_key',
            'SPREADSHEET_ID': 'test_spreadsheet_id',
            'GOOGLE_CREDENTIALS_B64': 'dGVzdF9jcmVkZW50aWFscw==',  # base64 of 'test_credentials'
            'TIMEZONE': 'Asia/Manila',
            'REPORT_CHAT_ID': '123456789'
        })
        self.env_patcher.start()

        # Mock the anthropic client
        self.anthropic_patcher = patch('telegram_bot.anthropic.Anthropic')
        self.mock_anthropic = self.anthropic_patcher.start()

        # Mock Google Sheets client
        self.sheets_patcher = patch('telegram_bot.GoogleSheetsClient')
        self.mock_sheets = self.sheets_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.anthropic_patcher.stop()
        self.sheets_patcher.stop()

    def test_scheduler_initialization(self):
        """Test that scheduler is properly initialized"""
        bot = TelegramGoogleSheetsBot(
            telegram_token='test_token',
            anthropic_key='test_key',
            credentials_file=None,
            spreadsheet_id='test_id'
        )
        mock_app = Mock()

        scheduler = bot.setup_scheduler(mock_app)

        # Verify scheduler is created
        self.assertIsNotNone(scheduler)
        self.assertIsInstance(scheduler, AsyncIOScheduler)

    def test_cron_job_3pm_configuration(self):
        """Test that 3 PM cron job is configured correctly"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()

        scheduler = bot.setup_scheduler(mock_app)

        # Get the 3 PM job
        jobs = scheduler.get_jobs()
        pm3_job = next((job for job in jobs if job.id == 'sales_report_3pm'), None)

        # Verify job exists
        self.assertIsNotNone(pm3_job, "3 PM job should be registered")

        # Verify job name
        self.assertEqual(pm3_job.name, 'Daily Sales Report at 3 PM')

        # Verify trigger configuration
        self.assertIsInstance(pm3_job.trigger, CronTrigger)

        # Verify schedule time - 3 PM is hour 15
        trigger_fields = pm3_job.trigger.fields
        self.assertEqual(str(trigger_fields[5]), '15', "Hour should be 15 (3 PM)")
        self.assertEqual(str(trigger_fields[6]), '0', "Minute should be 0")

    def test_cron_job_11pm_configuration(self):
        """Test that 11 PM cron job is configured correctly"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()

        scheduler = bot.setup_scheduler(mock_app)

        # Get the 11 PM job
        jobs = scheduler.get_jobs()
        pm11_job = next((job for job in jobs if job.id == 'sales_report_11pm'), None)

        # Verify job exists
        self.assertIsNotNone(pm11_job, "11 PM job should be registered")

        # Verify job name
        self.assertEqual(pm11_job.name, 'Daily Sales Report at 11 PM')

        # Verify trigger configuration
        self.assertIsInstance(pm11_job.trigger, CronTrigger)

        # Verify schedule time - 11 PM is hour 23
        trigger_fields = pm11_job.trigger.fields
        self.assertEqual(str(trigger_fields[5]), '23', "Hour should be 23 (11 PM)")
        self.assertEqual(str(trigger_fields[6]), '0', "Minute should be 0")

    def test_both_cron_jobs_registered(self):
        """Test that both cron jobs (3 PM and 11 PM) are registered"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()

        scheduler = bot.setup_scheduler(mock_app)
        jobs = scheduler.get_jobs()

        # Verify we have exactly 2 jobs
        self.assertEqual(len(jobs), 2, "Should have exactly 2 scheduled jobs")

        # Verify both job IDs exist
        job_ids = [job.id for job in jobs]
        self.assertIn('sales_report_3pm', job_ids, "3 PM job should be registered")
        self.assertIn('sales_report_11pm', job_ids, "11 PM job should be registered")

    def test_timezone_configuration_default(self):
        """Test default timezone configuration (Asia/Manila)"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()

        scheduler = bot.setup_scheduler(mock_app)

        # Verify scheduler timezone
        expected_tz = pytz.timezone('Asia/Manila')
        self.assertEqual(scheduler.timezone, expected_tz)

    def test_timezone_configuration_custom(self):
        """Test custom timezone configuration"""
        with patch.dict(os.environ, {'TIMEZONE': 'America/New_York'}):
            bot = TelegramGoogleSheetsBot()
            mock_app = Mock()

            scheduler = bot.setup_scheduler(mock_app)

            # Verify scheduler timezone
            expected_tz = pytz.timezone('America/New_York')
            self.assertEqual(scheduler.timezone, expected_tz)

    def test_timezone_job_trigger_alignment(self):
        """Test that cron job triggers use the correct timezone"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()

        scheduler = bot.setup_scheduler(mock_app)
        jobs = scheduler.get_jobs()

        manila_tz = pytz.timezone('Asia/Manila')

        for job in jobs:
            # Verify each job's trigger has the correct timezone
            self.assertEqual(job.trigger.timezone, manila_tz,
                           f"Job {job.id} should use Manila timezone")

    def test_scheduler_starts_running(self):
        """Test that scheduler starts in running state"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()

        scheduler = bot.setup_scheduler(mock_app)

        # Verify scheduler is running
        self.assertTrue(scheduler.running, "Scheduler should be in running state")

    def test_job_function_reference(self):
        """Test that jobs reference the correct function"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()

        scheduler = bot.setup_scheduler(mock_app)
        jobs = scheduler.get_jobs()

        for job in jobs:
            # Verify job calls the send_scheduled_sales_report method
            self.assertEqual(job.func, bot.send_scheduled_sales_report,
                           f"Job {job.id} should reference send_scheduled_sales_report")

    def test_job_arguments(self):
        """Test that jobs receive the correct arguments"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()

        scheduler = bot.setup_scheduler(mock_app)
        jobs = scheduler.get_jobs()

        for job in jobs:
            # Verify job has application as argument
            self.assertEqual(len(job.args), 1,
                           f"Job {job.id} should have 1 argument")
            self.assertEqual(job.args[0], mock_app,
                           f"Job {job.id} should receive application as argument")

    def test_replace_existing_jobs(self):
        """Test that jobs replace existing ones with same ID"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()

        # Set up scheduler twice
        scheduler1 = bot.setup_scheduler(mock_app)
        job_count_1 = len(scheduler1.get_jobs())

        # Shutdown first scheduler
        scheduler1.shutdown()

        # Create second scheduler - should replace jobs
        scheduler2 = bot.setup_scheduler(mock_app)
        job_count_2 = len(scheduler2.get_jobs())

        # Should have same number of jobs
        self.assertEqual(job_count_1, job_count_2,
                        "Job count should remain the same when replacing")
        self.assertEqual(job_count_2, 2, "Should still have 2 jobs")

        scheduler2.shutdown()


class TestScheduledReportExecution(unittest.IsolatedAsyncioTestCase):
    """Test the scheduled report execution functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token_12345',
            'ANTHROPIC_API_KEY': 'test_anthropic_key',
            'SPREADSHEET_ID': 'test_spreadsheet_id',
            'GOOGLE_CREDENTIALS_B64': 'dGVzdF9jcmVkZW50aWFscw==',
            'TIMEZONE': 'Asia/Manila',
            'REPORT_CHAT_ID': '123456789'
        })
        self.env_patcher.start()

        self.anthropic_patcher = patch('telegram_bot.anthropic.Anthropic')
        self.mock_anthropic = self.anthropic_patcher.start()

        self.sheets_patcher = patch('telegram_bot.GoogleSheetsClient')
        self.mock_sheets = self.sheets_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.anthropic_patcher.stop()
        self.sheets_patcher.stop()

    async def test_send_scheduled_report_success(self):
        """Test successful scheduled report sending"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()
        mock_app.bot = AsyncMock()

        # Mock the analyze_sales_for_dates method
        bot.analyze_sales_for_dates = Mock(return_value="Test sales report")

        await bot.send_scheduled_sales_report(mock_app)

        # Verify message was sent
        mock_app.bot.send_message.assert_called_once()
        call_args = mock_app.bot.send_message.call_args

        # Verify chat_id
        self.assertEqual(call_args.kwargs['chat_id'], '123456789')

        # Verify message contains report
        self.assertIn('Automated Sales Report', call_args.kwargs['text'])
        self.assertIn('Test sales report', call_args.kwargs['text'])

    async def test_send_scheduled_report_no_chat_id(self):
        """Test scheduled report skips when REPORT_CHAT_ID is not set"""
        with patch.dict(os.environ, {'REPORT_CHAT_ID': ''}, clear=False):
            bot = TelegramGoogleSheetsBot()
            mock_app = Mock()
            mock_app.bot = AsyncMock()

            await bot.send_scheduled_sales_report(mock_app)

            # Verify message was NOT sent
            mock_app.bot.send_message.assert_not_called()

    async def test_send_scheduled_report_no_data(self):
        """Test scheduled report handles no data gracefully"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()
        mock_app.bot = AsyncMock()

        # Mock analyze_sales_for_dates to return None
        bot.analyze_sales_for_dates = Mock(return_value=None)

        await bot.send_scheduled_sales_report(mock_app)

        # Verify warning message was sent
        mock_app.bot.send_message.assert_called_once()
        call_args = mock_app.bot.send_message.call_args
        self.assertIn('Could not generate scheduled sales report', call_args.kwargs['text'])

    async def test_send_scheduled_report_date_format(self):
        """Test that scheduled report uses correct date format"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()
        mock_app.bot = AsyncMock()

        bot.analyze_sales_for_dates = Mock(return_value="Test report")

        # Mock datetime to test specific date
        with patch('telegram_bot.datetime') as mock_datetime:
            mock_now = datetime(2025, 3, 15, 15, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime

            await bot.send_scheduled_sales_report(mock_app)

            # Verify analyze_sales_for_dates was called with correct date
            bot.analyze_sales_for_dates.assert_called_once_with('2025-03-15', '2025-03-15')


class TestEdgeCasesAndErrorHandling(unittest.IsolatedAsyncioTestCase):
    """Test edge cases and error handling for scheduled reports"""

    def setUp(self):
        """Set up test fixtures"""
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token_12345',
            'ANTHROPIC_API_KEY': 'test_anthropic_key',
            'SPREADSHEET_ID': 'test_spreadsheet_id',
            'GOOGLE_CREDENTIALS_B64': 'dGVzdF9jcmVkZW50aWFscw==',
            'TIMEZONE': 'Asia/Manila',
            'REPORT_CHAT_ID': '123456789'
        })
        self.env_patcher.start()

        self.anthropic_patcher = patch('telegram_bot.anthropic.Anthropic')
        self.mock_anthropic = self.anthropic_patcher.start()

        self.sheets_patcher = patch('telegram_bot.GoogleSheetsClient')
        self.mock_sheets = self.sheets_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.anthropic_patcher.stop()
        self.sheets_patcher.stop()

    async def test_error_in_send_message(self):
        """Test error handling when sending message fails"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()
        mock_app.bot = AsyncMock()
        mock_app.bot.send_message.side_effect = Exception("Network error")

        bot.analyze_sales_for_dates = Mock(return_value="Test report")

        # Should not raise exception
        await bot.send_scheduled_sales_report(mock_app)

    async def test_error_in_data_analysis(self):
        """Test error handling when data analysis fails"""
        bot = TelegramGoogleSheetsBot()
        mock_app = Mock()
        mock_app.bot = AsyncMock()

        bot.analyze_sales_for_dates = Mock(side_effect=Exception("Data error"))

        # Should not raise exception
        await bot.send_scheduled_sales_report(mock_app)

    def test_invalid_timezone_handling(self):
        """Test handling of invalid timezone"""
        with patch.dict(os.environ, {'TIMEZONE': 'Invalid/Timezone'}):
            bot = TelegramGoogleSheetsBot()
            mock_app = Mock()

            # Should raise exception for invalid timezone
            with self.assertRaises(Exception):
                bot.setup_scheduler(mock_app)

    def test_scheduler_multiple_timezone_configurations(self):
        """Test scheduler with different timezone configurations"""
        timezones = [
            'Asia/Manila',
            'America/New_York',
            'Europe/London',
            'Asia/Tokyo',
            'UTC'
        ]

        for tz in timezones:
            with self.subTest(timezone=tz):
                with patch.dict(os.environ, {'TIMEZONE': tz}):
                    bot = TelegramGoogleSheetsBot()
                    mock_app = Mock()

                    scheduler = bot.setup_scheduler(mock_app)
                    expected_tz = pytz.timezone(tz)

                    self.assertEqual(scheduler.timezone, expected_tz)
                    scheduler.shutdown()


def run_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCronSchedulerConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestScheduledReportExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCasesAndErrorHandling))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
