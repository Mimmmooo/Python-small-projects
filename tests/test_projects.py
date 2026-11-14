"""Offline tests for the calculator; periodic-table tests require its dependency."""

from decimal import Decimal
import unittest
import json
import tempfile
from pathlib import Path

from expense_history import load_history, save_history

from rent_calculator import expense_data, expense_report, parse_amount, split_expenses
from periodic_table import element_data, find_element, format_property, periodictable
from periodic_layout import element_category, periodic_positions, validate_periodic_positions


class PeriodicLayoutTests(unittest.TestCase):
    def test_layout_contains_all_elements_once(self):
        self.assertTrue(validate_periodic_positions())
        positions = periodic_positions()
        self.assertEqual(len(positions), 118)
        self.assertEqual(len(set(positions.values())), 118)

    def test_known_element_families(self):
        self.assertEqual(element_category(3), "alkali metal")
        self.assertEqual(element_category(26), "transition metal")
        self.assertEqual(element_category(54), "noble gas")
        self.assertEqual(element_category(92), "actinide")

    def test_invalid_atomic_number(self):
        for number in (0, 119):
            with self.subTest(number=number):
                with self.assertRaises(ValueError):
                    element_category(number)


class ExpenseHistoryTests(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "history.json"
            records = [{"total": "12.00", "shares": ["6.00", "6.00"]}]
            save_history(records, path)
            self.assertEqual(load_history(path), records)

    def test_history_is_limited_to_latest_100(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            records = [{"id": index, "shares": []} for index in range(125)]
            save_history(records, path)
            loaded = load_history(path)
            self.assertEqual(len(loaded), 100)
            self.assertEqual(loaded[0]["id"], 25)

    def test_corrupt_history_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            path.write_text("{broken", encoding="utf-8")
            self.assertEqual(load_history(path), [])


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
