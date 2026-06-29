import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from datetime import date, datetime
from io import BytesIO
from unittest import mock

import forecast_core
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


class RoundDollarsTests(unittest.TestCase):
    def test_rounds_up(self):
        self.assertEqual(webversion.round_dollars("$469.93"), "$470")

    def test_rounds_down(self):
        self.assertEqual(webversion.round_dollars("$469.20"), "$469")

    def test_integer_unchanged(self):
        self.assertEqual(webversion.round_dollars("$470"), "$470")

    def test_non_dollar_text_unchanged(self):
        self.assertEqual(
            webversion.round_dollars("Allowance unavailable"),
            "Allowance unavailable",
        )


class AllowanceCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)  # start with no cache file
        self.env = mock.patch.dict(
            os.environ, {"WX_ALLOWANCE_CACHE": self.tmp.name}, clear=False
        )
        self.env.start()
        os.environ.pop("WX_ALLOWANCE", None)

    def tearDown(self):
        self.env.stop()
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    @contextmanager
    def _urlopen_returning(self, text):
        calls = {"n": 0}

        def fake(url, timeout=0):
            calls["n"] += 1
            return _FakeResponse(text)

        with mock.patch.object(forecast_core, "urlopen", side_effect=fake):
            yield calls

    def test_fetches_then_caches_for_the_day(self):
        with self._urlopen_returning("$469.93") as calls:
            self.assertEqual(forecast_core.allowance(), "$469.93")
            self.assertEqual(forecast_core.allowance(), "$469.93")
            self.assertEqual(calls["n"], 1)  # second call served from cache
        today = datetime.now(forecast_core.TZ).date().isoformat()
        with open(self.tmp.name) as fh:
            self.assertEqual(
                json.load(fh), {"date": today, "allowance": "$469.93"}
            )

    def test_stale_cache_is_refetched(self):
        with open(self.tmp.name, "w") as fh:
            json.dump({"date": "2000-01-01", "allowance": "$1"}, fh)
        with self._urlopen_returning("$500.00") as calls:
            self.assertEqual(forecast_core.allowance(), "$500.00")
            self.assertEqual(calls["n"], 1)

    def test_network_failure_falls_back_to_cache(self):
        with open(self.tmp.name, "w") as fh:
            json.dump({"date": "2000-01-01", "allowance": "$42"}, fh)

        def boom(url, timeout=0):
            raise forecast_core.URLError("down")

        with mock.patch.object(forecast_core, "urlopen", side_effect=boom):
            self.assertEqual(forecast_core.allowance(), "$42")

    def test_network_failure_without_cache(self):
        def boom(url, timeout=0):
            raise forecast_core.URLError("down")

        with mock.patch.object(forecast_core, "urlopen", side_effect=boom):
            self.assertEqual(forecast_core.allowance(), "Allowance unavailable")


class _FakeResponse:
    def __init__(self, text):
        self._buf = BytesIO(text.encode("utf-8"))

    def __enter__(self):
        return self._buf

    def __exit__(self, *exc):
        return False


if __name__ == "__main__":
    unittest.main()
