import unittest

from tiktok_pdf_organizer.tracking import extract_trackings


class TrackingTests(unittest.TestCase):
    def test_extracts_exact_13_digit_tracking(self) -> None:
        self.assertEqual(
            extract_trackings("Rastreio: 3321234567890"),
            ("3321234567890",),
        )

    def test_does_not_extract_from_a_longer_number(self) -> None:
        self.assertEqual(extract_trackings("133212345678901"), ())

    def test_ignores_other_13_digit_numbers(self) -> None:
        self.assertEqual(extract_trackings("1231234567890"), ())

    def test_returns_unique_codes_in_order(self) -> None:
        text = "3320000000001 3320000000002 3320000000001"
        self.assertEqual(
            extract_trackings(text),
            ("3320000000001", "3320000000002"),
        )


if __name__ == "__main__":
    unittest.main()
