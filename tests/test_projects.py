"""Offline tests for the calculator; periodic-table tests require its dependency."""

from decimal import Decimal
import unittest

from rent_calculator import expense_data, expense_report, parse_amount, split_expenses
from periodic_table import element_data, find_element, format_property, periodictable


class RentCalculatorTests(unittest.TestCase):
    def test_amount_parsing(self):
        self.assertEqual(parse_amount("100.50"), Decimal("100.50"))
        self.assertEqual(parse_amount("0"), Decimal("0.00"))

    def test_rejects_invalid_amounts(self):
        for value in ("-1", "abc", "NaN", "Infinity", "12.345"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_amount(value)

    def test_exact_even_split(self):
        shares = split_expenses(
            Decimal("600.00"), Decimal("300.00"), Decimal("100.00"), 4
        )
        self.assertEqual(shares, [Decimal("250.00")] * 4)

    def test_uneven_split_keeps_every_cent(self):
        shares = split_expenses(
            Decimal("10.00"), Decimal("0.00"), Decimal("0.00"), 3
        )
        self.assertEqual(shares, [Decimal("3.34"), Decimal("3.33"), Decimal("3.33")])
        self.assertEqual(sum(shares), Decimal("10.00"))

    def test_zero_people_rejected(self):
        with self.assertRaises(ValueError):
            split_expenses(Decimal("1"), Decimal("2"), Decimal("3"), 0)

    def test_json_breakdown_keeps_exact_cents(self):
        result = expense_data(Decimal("10"), Decimal("0"), Decimal("0"), 3)
        self.assertEqual(result["total"], "10.00")
        self.assertEqual(result["shares"], ["3.34", "3.33", "3.33"])

    def test_report(self):
        report = expense_report(
            Decimal("100"), Decimal("20"), Decimal("0"), 2
        )
        self.assertIn("Each person pays : 60.00", report)


@unittest.skipIf(periodictable is None, "Install periodictable to run element tests")
class PeriodicTableTests(unittest.TestCase):
    def test_lookup_by_number_symbol_and_name(self):
        for value in ("8", "O", "oxygen"):
            with self.subTest(value=value):
                self.assertEqual(find_element(value).number, 8)

    def test_invalid_atomic_number(self):
        for value in ("0", "119", "not-an-element", ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    find_element(value)

    def test_element_data(self):
        result = element_data(find_element("Fe"))
        self.assertEqual(result["atomic_number"], 26)
        self.assertEqual(result["symbol"], "Fe")

    def test_missing_property(self):
        self.assertEqual(format_property(None), "Not available")


if __name__ == "__main__":
    unittest.main()
