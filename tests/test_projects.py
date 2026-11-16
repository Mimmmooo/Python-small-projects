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
from expense_settlement import calculate_settlement


class PeriodicLayoutTests(unittest.TestCase):
    def test_layout_contains_all_elements_once(self):
        self.assertTrue(validate_periodic_positions())
        positions = periodic_positions()
        self.assertEqual(len(positions), 118)
        self.assertEqual(len(set(positions.values())), 118)

    def test_known_element_families(self):
        self.assertEqual(element_category(1), "reactive nonmetal")
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

    def test_history_round_trip_preserves_settlement_details(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            record = {
                "total": "90.00",
                "shares": ["30.00", "30.00", "30.00"],
                "settlement": {
                    "participants": [{"name": "A", "paid": "90.00", "share": "30.00", "net": "+60.00"}],
                    "transfers": [{"from": "B", "to": "A", "amount": "30.00"}],
                },
            }
            save_history([record], path)
            self.assertEqual(load_history(path), [record])


class ExpenseSettlementTests(unittest.TestCase):
    def test_unequal_payments_create_repayments(self):
        result = calculate_settlement(Decimal("90.00"), [("A", Decimal("90.00")), ("B", Decimal("0.00")), ("C", Decimal("0.00"))])
        self.assertEqual(result["transfers"], [{"from": "B", "to": "A", "amount": "30.00"}, {"from": "C", "to": "A", "amount": "30.00"}])
        self.assertEqual([row["net"] for row in result["participants"]], ["+60.00", "-30.00", "-30.00"])

    def test_invalid_contributions_are_rejected(self):
        with self.assertRaises(ValueError):
            calculate_settlement(Decimal("10.00"), [("A", Decimal("5.00"))])
        with self.assertRaises(ValueError):
            calculate_settlement(Decimal("10.00"), [("A", Decimal("5.00")), ("a", Decimal("5.00"))])

    def test_even_payments_need_no_transfers(self):
        result = calculate_settlement(Decimal("30.00"), [("A", Decimal("10.00")), ("B", Decimal("10.00")), ("C", Decimal("10.00"))])
        self.assertEqual(result["transfers"], [])

    def test_rejects_non_text_names_and_non_decimal_payments(self):
        invalid_cases = [
            (Decimal("10.00"), [(None, Decimal("10.00"))]),
            (Decimal("10.00"), [("A", 10.0)]),
            (Decimal("10.00"), [("A", Decimal("10.001"))]),
            (Decimal("10.00"), [("A", Decimal("1000000000000.00"))]),
        ]
        for total, contributions in invalid_cases:
            with self.subTest(contributions=contributions):
                with self.assertRaises(ValueError):
                    calculate_settlement(total, contributions)

    def test_rejects_too_many_participants(self):
        contributions = [(f"Person {index}", Decimal("0.00")) for index in range(10001)]
        with self.assertRaises(ValueError):
            calculate_settlement(Decimal("0.00"), contributions)

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


    def test_named_participants_are_included_in_report_and_json(self):
        result = expense_data(
            Decimal("10.00"), Decimal("0.00"), Decimal("0.00"), 3,
            ["Ayon", "Mim", "Rafi"],
        )
        self.assertEqual(
            result["participants"],
            [
                {"name": "Ayon", "share": "3.34"},
                {"name": "Mim", "share": "3.33"},
                {"name": "Rafi", "share": "3.33"},
            ],
        )
        report = expense_report(
            Decimal("10.00"), Decimal("0.00"), Decimal("0.00"), 3,
            ["Ayon", "Mim", "Rafi"], "BDT",
        )
        self.assertIn("Ayon pays : 3.34 BDT", report)
        self.assertIn("Rafi pays : 3.33 BDT", report)

    def test_invalid_names_are_rejected(self):
        for names in (["A", "A"], ["A", ""], ["A"], ["x" * 61, "B"]):
            with self.subTest(names=names):
                with self.assertRaises(ValueError):
                    expense_data(Decimal("10.00"), Decimal("0.00"), Decimal("0.00"), 2, names)

    def test_amount_parser_rejects_empty_and_non_string_input(self):
        for value in ("", "   ", None, 100):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_amount(value)

    def test_amount_limit_and_decimal_precision(self):
        self.assertEqual(parse_amount("999999999999.99"), Decimal("999999999999.99"))
        for value in ("1000000000000", "1.001", "1e999999"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_amount(value)

    def test_people_must_be_a_real_positive_integer(self):
        for people in (0, -1, 1.5, True, 10001):
            with self.subTest(people=people):
                with self.assertRaises(ValueError):
                    split_expenses(Decimal("1.00"), Decimal("0.00"), Decimal("0.00"), people)


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
