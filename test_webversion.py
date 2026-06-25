import unittest
from datetime import date

import webversion


class EventCountdownTests(unittest.TestCase):
    def test_future_date_no_label(self):
        self.assertEqual(
            webversion.event_countdown(date(2026, 6, 25), "2026-07-05", None),
            "10 days",
        )

    def test_future_date_with_label(self):
        self.assertEqual(
            webversion.event_countdown(date(2026, 6, 25), "2026-07-05", "vacation"),
            "10 days until vacation",
        )

    def test_today_is_zero_days(self):
        self.assertEqual(
            webversion.event_countdown(date(2026, 6, 25), "2026-06-25", None),
            "0 days",
        )

    def test_past_date_returns_none(self):
        self.assertIsNone(
            webversion.event_countdown(date(2026, 6, 25), "2024-06-20", None)
        )

    def test_unset_returns_none(self):
        self.assertIsNone(webversion.event_countdown(date(2026, 6, 25), None, None))
        self.assertIsNone(webversion.event_countdown(date(2026, 6, 25), "", None))

    def test_invalid_returns_none(self):
        self.assertIsNone(
            webversion.event_countdown(date(2026, 6, 25), "not-a-date", None)
        )


class ComposeAllowanceTests(unittest.TestCase):
    def test_with_countdown(self):
        self.assertEqual(
            webversion.compose_allowance("$469.93", "10 days"),
            "$469.93, 10 days",
        )

    def test_without_countdown(self):
        self.assertEqual(webversion.compose_allowance("$469.93", None), "$469.93")


if __name__ == "__main__":
    unittest.main()
