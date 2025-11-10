"""
Simplified Implementation Verification Tests

These tests verify the two key changes:
1. Cron jobs configured for 3 PM and 11 PM
2. AI model upgraded to Sonnet 4.5 (claude-sonnet-4-5-20250929)
"""

import unittest
import os
import re


class TestCronJobImplementation(unittest.TestCase):
    """Verify cron job implementation in telegram_bot.py"""

    def setUp(self):
        """Load telegram_bot.py source code"""
        self.bot_file = os.path.join(os.path.dirname(__file__), 'telegram_bot.py')
        with open(self.bot_file, 'r') as f:
            self.source_code = f.read()
            self.source_lines = f.readlines()

    def test_3pm_cron_job_exists(self):
        """Verify 3 PM (hour=15) cron job is configured"""
        # Look for hour=15 (3 PM in 24-hour format)
        pattern_hour15 = r'hour\s*=\s*15'
        matches = re.findall(pattern_hour15, self.source_code)

        self.assertGreater(len(matches), 0,
                          "Should find at least one cron job configured for hour=15 (3 PM)")

        # Verify it's part of a CronTrigger
        pattern_cron_3pm = r'CronTrigger\s*\([^)]*hour\s*=\s*15'
        matches_cron = re.findall(pattern_cron_3pm, self.source_code, re.MULTILINE | re.DOTALL)

        self.assertGreater(len(matches_cron), 0,
                          "Should find CronTrigger configuration with hour=15 (3 PM)")

    def test_11pm_cron_job_exists(self):
        """Verify 11 PM (hour=23) cron job is configured"""
        # Look for hour=23 (11 PM in 24-hour format)
        pattern_hour23 = r'hour\s*=\s*23'
        matches = re.findall(pattern_hour23, self.source_code)

        self.assertGreater(len(matches), 0,
                          "Should find at least one cron job configured for hour=23 (11 PM)")

        # Verify it's part of a CronTrigger
        pattern_cron_11pm = r'CronTrigger\s*\([^)]*hour\s*=\s*23'
        matches_cron = re.findall(pattern_cron_11pm, self.source_code, re.MULTILINE | re.DOTALL)

        self.assertGreater(len(matches_cron), 0,
                          "Should find CronTrigger configuration with hour=23 (11 PM)")

    def test_both_cron_jobs_have_correct_minutes(self):
        """Verify both cron jobs are set to minute=0"""
        # Look for CronTrigger configurations with minute=0
        pattern = r'CronTrigger\s*\([^)]*hour\s*=\s*(15|23)[^)]*minute\s*=\s*0'
        matches = re.findall(pattern, self.source_code, re.MULTILINE | re.DOTALL)

        self.assertEqual(len(matches), 2,
                        "Should find exactly 2 CronTrigger configurations with minute=0 "
                        "(one for 3 PM and one for 11 PM)")

    def test_cron_job_ids_are_unique(self):
        """Verify cron jobs have unique and descriptive IDs"""
        # Look for job IDs
        pattern_3pm_id = r"id\s*=\s*['\"]sales_report_3pm['\"]"
        pattern_11pm_id = r"id\s*=\s*['\"]sales_report_11pm['\"]"

        matches_3pm = re.findall(pattern_3pm_id, self.source_code)
        matches_11pm = re.findall(pattern_11pm_id, self.source_code)

        self.assertGreater(len(matches_3pm), 0,
                          "Should find 'sales_report_3pm' job ID")
        self.assertGreater(len(matches_11pm), 0,
                          "Should find 'sales_report_11pm' job ID")

    def test_scheduler_uses_apscheduler(self):
        """Verify APScheduler is being used for scheduling"""
        # Check for AsyncIOScheduler import and usage
        self.assertIn('AsyncIOScheduler', self.source_code,
                     "Should import AsyncIOScheduler")

        self.assertIn('CronTrigger', self.source_code,
                     "Should import CronTrigger")

    def test_send_scheduled_sales_report_method_exists(self):
        """Verify send_scheduled_sales_report method exists"""
        pattern = r'async\s+def\s+send_scheduled_sales_report'
        matches = re.findall(pattern, self.source_code)

        self.assertGreater(len(matches), 0,
                          "Should have async send_scheduled_sales_report method")

    def test_setup_scheduler_method_exists(self):
        """Verify setup_scheduler method exists"""
        pattern = r'def\s+setup_scheduler'
        matches = re.findall(pattern, self.source_code)

        self.assertGreater(len(matches), 0,
                          "Should have setup_scheduler method")

    def test_timezone_support(self):
        """Verify timezone support is implemented"""
        # Check for pytz usage
        self.assertIn('pytz', self.source_code,
                     "Should use pytz for timezone support")

        # Check for timezone configuration
        pattern = r"os\.getenv\s*\(\s*['\"]TIMEZONE['\"]"
        matches = re.findall(pattern, self.source_code)

        self.assertGreater(len(matches), 0,
                          "Should read TIMEZONE from environment variables")


class TestAIModelUpgrade(unittest.TestCase):
    """Verify AI model has been upgraded to Sonnet 4.5"""

    EXPECTED_MODEL_ID = "claude-sonnet-4-5-20250929"
    OLD_MODEL_ID = "claude-3-5-sonnet-20240620"

    def setUp(self):
        """Load telegram_bot.py source code"""
        self.bot_file = os.path.join(os.path.dirname(__file__), 'telegram_bot.py')
        with open(self.bot_file, 'r') as f:
            self.source_code = f.read()
            self.source_lines = f.readlines()

    def test_old_model_not_present(self):
        """CRITICAL: Verify old model ID is NOT in the codebase"""
        count = self.source_code.count(self.OLD_MODEL_ID)

        if count > 0:
            # Find line numbers with old model ID
            lines_with_old_model = []
            for i, line in enumerate(self.source_lines, 1):
                if self.OLD_MODEL_ID in line:
                    lines_with_old_model.append(f"  Line {i}: {line.strip()}")

            error_msg = (
                f"\n\nCRITICAL ISSUE: Found {count} occurrence(s) of OLD model ID "
                f"'{self.OLD_MODEL_ID}'\n\n"
                f"The model has NOT been upgraded to Sonnet 4.5!\n\n"
                f"Locations:\n" + "\n".join(lines_with_old_model) + "\n\n"
                f"All instances must be changed to '{self.EXPECTED_MODEL_ID}'\n"
            )
            self.fail(error_msg)

    def test_new_model_present(self):
        """CRITICAL: Verify new Sonnet 4.5 model ID is in the codebase"""
        count = self.source_code.count(self.EXPECTED_MODEL_ID)

        if count == 0:
            self.fail(
                f"\n\nCRITICAL ISSUE: New model ID '{self.EXPECTED_MODEL_ID}' NOT FOUND!\n\n"
                f"The AI model has not been upgraded to Sonnet 4.5.\n"
                f"Please update all model references to use '{self.EXPECTED_MODEL_ID}'\n"
            )

        # Should have multiple occurrences (one for each API call)
        self.assertGreaterEqual(count, 3,
                               f"Expected at least 3 occurrences of new model ID, found {count}")

    def test_anthropic_client_usage(self):
        """Verify Anthropic client is being used correctly"""
        # Check for anthropic.messages.create calls
        pattern = r'\.messages\.create\s*\('
        matches = re.findall(pattern, self.source_code)

        self.assertGreater(len(matches), 0,
                          "Should have calls to anthropic.messages.create")

    def test_model_parameter_in_api_calls(self):
        """Verify model parameter is specified in API calls"""
        # Look for model parameter in API calls
        pattern = r'model\s*=\s*["\']([^"\']+)["\']'
        matches = re.findall(pattern, self.source_code)

        # Filter to only Claude models
        claude_models = [m for m in matches if 'claude' in m.lower()]

        self.assertGreater(len(claude_models), 0,
                          "Should find Claude model specifications in API calls")

        # All should be the new model
        for model in claude_models:
            self.assertEqual(model, self.EXPECTED_MODEL_ID,
                           f"Found model '{model}', expected '{self.EXPECTED_MODEL_ID}'")

    def test_no_mixed_model_versions(self):
        """Verify no mixing of old and new model versions"""
        # Count all Claude model references
        pattern = r'model\s*=\s*["\']claude-[^"\']+["\']'
        all_models = re.findall(pattern, self.source_code)

        if not all_models:
            self.fail("No Claude model specifications found in code")

        # Extract just the model IDs
        model_ids = [re.search(r'["\']([^"\']+)["\']', m).group(1) for m in all_models]

        # All should be the same (new) model
        unique_models = set(model_ids)

        if len(unique_models) > 1:
            self.fail(
                f"\n\nINCONSISTENCY: Found multiple Claude model versions:\n"
                f"{unique_models}\n\n"
                f"All should be '{self.EXPECTED_MODEL_ID}'\n"
            )

        # The single model should be the new one
        self.assertEqual(list(unique_models)[0], self.EXPECTED_MODEL_ID,
                        f"All models should be '{self.EXPECTED_MODEL_ID}'")


class TestDocumentation(unittest.TestCase):
    """Verify documentation is present for new features"""

    def test_scheduled_reports_documentation_exists(self):
        """Verify SCHEDULED_REPORTS.md file exists"""
        doc_file = os.path.join(os.path.dirname(__file__), 'SCHEDULED_REPORTS.md')
        self.assertTrue(os.path.exists(doc_file),
                       "SCHEDULED_REPORTS.md documentation should exist")

    def test_documentation_mentions_schedule_times(self):
        """Verify documentation mentions 3 PM and 11 PM"""
        doc_file = os.path.join(os.path.dirname(__file__), 'SCHEDULED_REPORTS.md')

        if os.path.exists(doc_file):
            with open(doc_file, 'r') as f:
                content = f.read()

            self.assertIn('3 PM', content,
                         "Documentation should mention 3 PM schedule")
            self.assertIn('11 PM', content,
                         "Documentation should mention 11 PM schedule")


def run_tests():
    """Run all verification tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCronJobImplementation))
    suite.addTests(loader.loadTestsFromTestCase(TestAIModelUpgrade))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentation))

    # Run with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("IMPLEMENTATION VERIFICATION SUMMARY")
    print("="*70)

    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
        print("\nBoth implementations are CORRECT:")
        print("  ✓ Cron jobs configured for 3 PM and 11 PM")
        print("  ✓ AI model upgraded to Sonnet 4.5")
    else:
        print("✗ SOME TESTS FAILED")
        print(f"\nFailures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

    print("="*70)

    return result


if __name__ == '__main__':
    import sys
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
