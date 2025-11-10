"""
Comprehensive Test Suite for AI Model Upgrade to Sonnet 4.5

This test suite validates that the AI model has been correctly upgraded from
claude-3-5-sonnet-20240620 to claude-sonnet-4-5-20250929 (Sonnet 4.5).

Test Coverage:
- Model ID verification across all API calls
- API request parameter validation
- Response handling compatibility
- Error handling with new model
- Token limit configurations
- Integration with existing functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import os
import sys

# Add parent directory to path to import telegram_bot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import TelegramGoogleSheetsBot


class TestAIModelConfiguration(unittest.TestCase):
    """Test AI model configuration and model ID usage"""

    # Expected model ID for Sonnet 4.5
    EXPECTED_MODEL_ID = "claude-sonnet-4-5-20250929"

    # Old model ID that should NOT be present
    OLD_MODEL_ID = "claude-3-5-sonnet-20240620"

    def setUp(self):
        """Set up test fixtures"""
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token_12345',
            'ANTHROPIC_API_KEY': 'test_anthropic_key',
            'SPREADSHEET_ID': 'test_spreadsheet_id',
            'GOOGLE_CREDENTIALS_B64': 'dGVzdF9jcmVkZW50aWFscw==',
        })
        self.env_patcher.start()

        # Mock the anthropic client
        self.anthropic_patcher = patch('telegram_bot.anthropic.Anthropic')
        self.mock_anthropic_class = self.anthropic_patcher.start()
        self.mock_anthropic_instance = MagicMock()
        self.mock_anthropic_class.return_value = self.mock_anthropic_instance

        # Mock Google Sheets client
        self.sheets_patcher = patch('telegram_bot.GoogleSheetsClient')
        self.mock_sheets = self.sheets_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.anthropic_patcher.stop()
        self.sheets_patcher.stop()

    def test_model_id_not_old_version(self):
        """Test that old model ID is NOT used anywhere in the codebase"""
        # Read the telegram_bot.py file to check for old model ID
        bot_file_path = os.path.join(os.path.dirname(__file__), 'telegram_bot.py')

        with open(bot_file_path, 'r') as f:
            content = f.read()

        # Count occurrences of old model ID
        old_model_count = content.count(self.OLD_MODEL_ID)

        # This test will fail if the old model ID is still present
        # This helps verify the upgrade was completed
        self.assertEqual(old_model_count, 0,
                        f"Found {old_model_count} occurrences of old model ID '{self.OLD_MODEL_ID}'. "
                        f"All instances should be upgraded to '{self.EXPECTED_MODEL_ID}'")

    def test_model_id_updated_to_sonnet_45(self):
        """Test that new Sonnet 4.5 model ID is present in the codebase"""
        # Read the telegram_bot.py file to check for new model ID
        bot_file_path = os.path.join(os.path.dirname(__file__), 'telegram_bot.py')

        with open(bot_file_path, 'r') as f:
            content = f.read()

        # Check for new model ID
        new_model_count = content.count(self.EXPECTED_MODEL_ID)

        # Should have multiple occurrences (one for each API call location)
        self.assertGreater(new_model_count, 0,
                          f"Expected to find new model ID '{self.EXPECTED_MODEL_ID}' in the code. "
                          f"Found {new_model_count} occurrences.")

        # Based on the grep results, we expect at least 5 locations
        self.assertGreaterEqual(new_model_count, 5,
                               f"Expected at least 5 occurrences of new model ID, found {new_model_count}")


class TestAIModelAPIIntegration(unittest.TestCase):
    """Test AI model integration with Anthropic API"""

    EXPECTED_MODEL_ID = "claude-sonnet-4-5-20250929"

    def setUp(self):
        """Set up test fixtures"""
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token_12345',
            'ANTHROPIC_API_KEY': 'test_anthropic_key',
            'SPREADSHEET_ID': 'test_spreadsheet_id',
            'GOOGLE_CREDENTIALS_B64': 'dGVzdF9jcmVkZW50aWFscw==',
        })
        self.env_patcher.start()

        self.anthropic_patcher = patch('telegram_bot.anthropic.Anthropic')
        self.mock_anthropic_class = self.anthropic_patcher.start()
        self.mock_anthropic_instance = MagicMock()
        self.mock_anthropic_class.return_value = self.mock_anthropic_instance

        # Set up mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test AI response")]
        self.mock_anthropic_instance.messages.create.return_value = mock_response

        self.sheets_patcher = patch('telegram_bot.GoogleSheetsClient')
        self.mock_sheets_class = self.sheets_patcher.start()
        self.mock_sheets_instance = MagicMock()
        self.mock_sheets_class.return_value = self.mock_sheets_instance

        # Mock sheets data
        self.mock_sheets_instance.read_sheet.return_value = [
            ['Date', 'Customer', 'Product', 'Amount', 'Status'],
            ['2025-01-15', 'John Doe', 'Cheese Pouch', '100', 'Paid']
        ]

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.anthropic_patcher.stop()
        self.sheets_patcher.stop()

    def test_api_call_uses_correct_model_id(self):
        """Test that API calls use the correct Sonnet 4.5 model ID"""
        bot = TelegramGoogleSheetsBot()

        # Trigger an analysis that uses the AI model
        result = bot.analyze_sales_for_dates('2025-01-15', '2025-01-15')

        # Verify the anthropic client was called
        self.mock_anthropic_instance.messages.create.assert_called()

        # Get all calls to messages.create
        calls = self.mock_anthropic_instance.messages.create.call_args_list

        # Verify each call uses the correct model
        for call_item in calls:
            call_kwargs = call_item.kwargs if call_item.kwargs else call_item[1]

            # Check model parameter
            self.assertIn('model', call_kwargs,
                         "API call should include 'model' parameter")

            # Note: This test will fail until the model is upgraded
            # It serves as verification that the upgrade needs to happen
            actual_model = call_kwargs['model']
            self.assertEqual(actual_model, self.EXPECTED_MODEL_ID,
                           f"Expected model '{self.EXPECTED_MODEL_ID}', "
                           f"but got '{actual_model}'. Model needs to be upgraded.")

    def test_api_request_parameters_valid(self):
        """Test that API requests include all required parameters"""
        bot = TelegramGoogleSheetsBot()

        result = bot.analyze_sales_for_dates('2025-01-15', '2025-01-15')

        # Verify the anthropic client was called
        self.mock_anthropic_instance.messages.create.assert_called()

        # Get call arguments
        call_kwargs = self.mock_anthropic_instance.messages.create.call_args.kwargs

        # Verify required parameters
        required_params = ['model', 'max_tokens', 'messages']
        for param in required_params:
            self.assertIn(param, call_kwargs,
                         f"API call should include '{param}' parameter")

        # Verify model is correct
        self.assertEqual(call_kwargs['model'], self.EXPECTED_MODEL_ID)

        # Verify max_tokens is set
        self.assertIsInstance(call_kwargs['max_tokens'], int)
        self.assertGreater(call_kwargs['max_tokens'], 0)

        # Verify messages structure
        self.assertIsInstance(call_kwargs['messages'], list)
        self.assertGreater(len(call_kwargs['messages']), 0)

    def test_token_limits_configuration(self):
        """Test that token limits are appropriately configured for different use cases"""
        bot = TelegramGoogleSheetsBot()

        # Trigger analysis
        result = bot.analyze_sales_for_dates('2025-01-15', '2025-01-15')

        # Get all API calls
        calls = self.mock_anthropic_instance.messages.create.call_args_list

        for call_item in calls:
            call_kwargs = call_item.kwargs if call_item.kwargs else call_item[1]

            # Verify max_tokens is reasonable (between 100 and 1000 for this use case)
            max_tokens = call_kwargs.get('max_tokens', 0)
            self.assertGreater(max_tokens, 0,
                             "max_tokens should be greater than 0")
            self.assertLessEqual(max_tokens, 1000,
                                "max_tokens should not exceed 1000 for summary tasks")


class TestAIModelResponseHandling(unittest.TestCase):
    """Test AI model response handling and compatibility"""

    EXPECTED_MODEL_ID = "claude-sonnet-4-5-20250929"

    def setUp(self):
        """Set up test fixtures"""
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token_12345',
            'ANTHROPIC_API_KEY': 'test_anthropic_key',
            'SPREADSHEET_ID': 'test_spreadsheet_id',
            'GOOGLE_CREDENTIALS_B64': 'dGVzdF9jcmVkZW50aWFscw==',
        })
        self.env_patcher.start()

        self.anthropic_patcher = patch('telegram_bot.anthropic.Anthropic')
        self.mock_anthropic_class = self.anthropic_patcher.start()
        self.mock_anthropic_instance = MagicMock()
        self.mock_anthropic_class.return_value = self.mock_anthropic_instance

        self.sheets_patcher = patch('telegram_bot.GoogleSheetsClient')
        self.mock_sheets_class = self.sheets_patcher.start()
        self.mock_sheets_instance = MagicMock()
        self.mock_sheets_class.return_value = self.mock_sheets_instance

        # Mock sheets data
        self.mock_sheets_instance.read_sheet.return_value = [
            ['Date', 'Customer', 'Product', 'Amount', 'Status'],
            ['2025-01-15', 'John Doe', 'Cheese Pouch', '100', 'Paid']
        ]

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.anthropic_patcher.stop()
        self.sheets_patcher.stop()

    def test_successful_response_handling(self):
        """Test that successful AI responses are handled correctly"""
        bot = TelegramGoogleSheetsBot()

        # Mock successful response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Strong sales performance today!")]
        self.mock_anthropic_instance.messages.create.return_value = mock_response

        result = bot.analyze_sales_for_dates('2025-01-15', '2025-01-15')

        # Verify result is not None
        self.assertIsNotNone(result, "Should receive a valid response")

        # Verify result is a string
        self.assertIsInstance(result, str, "Response should be a string")

    def test_empty_response_handling(self):
        """Test handling of empty AI responses"""
        bot = TelegramGoogleSheetsBot()

        # Mock empty response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="")]
        self.mock_anthropic_instance.messages.create.return_value = mock_response

        result = bot.analyze_sales_for_dates('2025-01-15', '2025-01-15')

        # Should still return a result (with fallback or data only)
        self.assertIsNotNone(result)

    def test_api_error_handling(self):
        """Test error handling when API call fails"""
        bot = TelegramGoogleSheetsBot()

        # Mock API error
        self.mock_anthropic_instance.messages.create.side_effect = Exception("API Error")

        # Should not crash, should handle gracefully
        result = bot.analyze_sales_for_dates('2025-01-15', '2025-01-15')

        # Should return some result even without AI insights
        self.assertIsNotNone(result, "Should handle API errors gracefully")

    def test_response_text_extraction(self):
        """Test that response text is correctly extracted from API response"""
        bot = TelegramGoogleSheetsBot()

        # Mock response with specific text
        expected_text = "Sales are up 25% from last week!"
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=expected_text)]
        self.mock_anthropic_instance.messages.create.return_value = mock_response

        result = bot.analyze_sales_for_dates('2025-01-15', '2025-01-15')

        # Result should contain the AI insight
        self.assertIn(expected_text, result,
                     "Result should include AI-generated insight")


class TestModelUpgradeRegressionChecks(unittest.TestCase):
    """Regression tests to ensure model upgrade doesn't break existing functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token_12345',
            'ANTHROPIC_API_KEY': 'test_anthropic_key',
            'SPREADSHEET_ID': 'test_spreadsheet_id',
            'GOOGLE_CREDENTIALS_B64': 'dGVzdF9jcmVkZW50aWFscw==',
        })
        self.env_patcher.start()

        self.anthropic_patcher = patch('telegram_bot.anthropic.Anthropic')
        self.mock_anthropic_class = self.anthropic_patcher.start()
        self.mock_anthropic_instance = MagicMock()
        self.mock_anthropic_class.return_value = self.mock_anthropic_instance

        # Mock successful response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Good sales today!")]
        self.mock_anthropic_instance.messages.create.return_value = mock_response

        self.sheets_patcher = patch('telegram_bot.GoogleSheetsClient')
        self.mock_sheets_class = self.sheets_patcher.start()
        self.mock_sheets_instance = MagicMock()
        self.mock_sheets_class.return_value = self.mock_sheets_instance

        # Mock sheets data
        self.mock_sheets_instance.read_sheet.return_value = [
            ['Date', 'Customer', 'Product', 'Amount', 'Status'],
            ['2025-01-15', 'John Doe', 'Cheese Pouch', '100', 'Paid'],
            ['2025-01-15', 'Jane Smith', 'BBQ Pouch', '150', 'Paid']
        ]

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.anthropic_patcher.stop()
        self.sheets_patcher.stop()

    def test_single_date_analysis_still_works(self):
        """Test that single date analysis works with new model"""
        bot = TelegramGoogleSheetsBot()

        result = bot.analyze_sales_for_dates('2025-01-15', '2025-01-15')

        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_date_range_analysis_still_works(self):
        """Test that date range analysis works with new model"""
        bot = TelegramGoogleSheetsBot()

        # Mock sheets data for multiple dates
        self.mock_sheets_instance.read_sheet.return_value = [
            ['Date', 'Customer', 'Product', 'Amount', 'Status'],
            ['2025-01-15', 'John Doe', 'Cheese Pouch', '100', 'Paid'],
            ['2025-01-16', 'Jane Smith', 'BBQ Pouch', '150', 'Paid'],
            ['2025-01-17', 'Bob Johnson', 'Original Pouch', '200', 'Paid']
        ]

        result = bot.analyze_sales_for_dates('2025-01-15', '2025-01-17')

        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_bot_initialization_successful(self):
        """Test that bot initializes successfully with new model"""
        try:
            bot = TelegramGoogleSheetsBot()
            self.assertIsNotNone(bot)
            self.assertIsNotNone(bot.anthropic_client)
        except Exception as e:
            self.fail(f"Bot initialization failed: {e}")

    def test_multiple_ai_calls_all_use_new_model(self):
        """Test that multiple AI calls all use the correct model"""
        bot = TelegramGoogleSheetsBot()

        # Make multiple analysis calls
        bot.analyze_sales_for_dates('2025-01-15', '2025-01-15')
        bot.analyze_sales_for_dates('2025-01-16', '2025-01-16')

        # Get all calls
        calls = self.mock_anthropic_instance.messages.create.call_args_list

        # Verify all calls use the correct model
        for call_item in calls:
            call_kwargs = call_item.kwargs if call_item.kwargs else call_item[1]
            self.assertEqual(call_kwargs['model'], "claude-sonnet-4-5-20250929",
                           "All API calls should use Sonnet 4.5 model")


class TestModelIDConsistency(unittest.TestCase):
    """Test model ID consistency across the codebase"""

    def test_no_hardcoded_old_model_ids(self):
        """Test that no hardcoded old model IDs exist in the code"""
        bot_file_path = os.path.join(os.path.dirname(__file__), 'telegram_bot.py')

        with open(bot_file_path, 'r') as f:
            lines = f.readlines()

        # Look for old model ID in each line
        lines_with_old_model = []
        for i, line in enumerate(lines, 1):
            if 'claude-3-5-sonnet-20240620' in line:
                lines_with_old_model.append((i, line.strip()))

        # Fail if any old model IDs found
        if lines_with_old_model:
            error_msg = "Found old model ID in the following lines:\n"
            for line_num, line_content in lines_with_old_model:
                error_msg += f"  Line {line_num}: {line_content}\n"
            error_msg += "\nAll instances should be updated to 'claude-sonnet-4-5-20250929'"
            self.fail(error_msg)

    def test_new_model_id_present(self):
        """Test that new model ID is present in the code"""
        bot_file_path = os.path.join(os.path.dirname(__file__), 'telegram_bot.py')

        with open(bot_file_path, 'r') as f:
            content = f.read()

        # Check for new model ID
        self.assertIn('claude-sonnet-4-5-20250929', content,
                     "New model ID 'claude-sonnet-4-5-20250929' should be present in the code")


def run_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAIModelConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestAIModelAPIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAIModelResponseHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestModelUpgradeRegressionChecks))
    suite.addTests(loader.loadTestsFromTestCase(TestModelIDConsistency))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
