import unittest
from datetime import date

from link_analytics.domain import (
    DailyMetrics,
    classify_request,
    normalize_destination,
    signed_browser_token,
    visitor_hash,
)


class DestinationTests(unittest.TestCase):
    def test_valid_links_and_normalization(self):
        self.assertEqual(
            normalize_destination(" https://telegram.me/channel?start=demo "),
            "https://t.me/channel?start=demo",
        )
        self.assertEqual(normalize_destination("https://t.me/+invite"), "https://t.me/+invite")

    def test_rejects_unsafe_destinations(self):
        for url in (
            "http://t.me/a",
            "https://t.me.evil.test/a",
            "https://t.me@evil.test/a",
            "https://t.me:443/a",
            "https://t.me/",
            "javascript:alert(1)",
            "https://t.me/a\r\nx:y",
            "https://t.me\\@evil.test/a",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                normalize_destination(url)


class RequestTests(unittest.TestCase):
    def test_classification(self):
        for method, headers, expected in (
            ("GET", {"User-Agent": "Mozilla/5.0"}, "transition"),
            ("GET", {"user-agent": "TelegramBot"}, "technical"),
            ("GET", {}, "technical"),
            ("HEAD", {"purpose": "prefetch"}, "head"),
            ("GET", {"Sec-Purpose": "prefetch"}, "prefetch"),
        ):
            with self.subTest(expected=expected):
                self.assertEqual(classify_request(method, headers), expected)

    def test_signed_token_and_day_scoping(self):
        secret = b"test-only-secret"
        token = signed_browser_token(secret)
        self.assertEqual(signed_browser_token(secret, token), token)
        self.assertNotEqual(signed_browser_token(secret, token + "x"), token + "x")
        first = visitor_hash(secret, date(2026, 1, 1), token)
        self.assertEqual(first, visitor_hash(secret, date(2026, 1, 1), token))
        self.assertNotEqual(first, visitor_hash(secret, date(2026, 1, 2), token))
        self.assertNotIn(token, first)

    def test_metrics_invariants(self):
        self.assertEqual(DailyMetrics(5, 3, 2).technical_requests, 2)
        for values in ((-1, 0, 0), (2, 3, 1), (3, 2, 3)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                DailyMetrics(*values)


if __name__ == "__main__":
    unittest.main()
